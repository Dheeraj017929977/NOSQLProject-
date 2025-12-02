"""
Social Graph Module
Handles relationship-based use cases:
- UC-5  : Follow Another User
- UC-6  : Unfollow a User
- UC-7  : View Friends/Connections
- UC-8  : Mutual Connections
- UC-9  : Friend Recommendations
- UC-10 : Search Users
- UC-11 : Explore Popular Users
"""

from neo4j_connection import Neo4jConnection


class SocialGraph:
    def __init__(self, db_connection: Neo4jConnection):
        self.db = db_connection

    # ==========================================================
    # UC-5: Follow Another User
    # ==========================================================
    def follow_user(self, follower_username, followee_username):
        """
        Follow a user.
        Creates a FOLLOWS relationship from follower -> followee.

        Returns (success: bool, message: str)
        """
        if follower_username == followee_username:
            return False, "Cannot follow yourself"

        session = self.db.get_session()
        try:
            # 1) Check if both users exist
            result = session.run(
                """
                MATCH (follower:User {username: $follower_username})
                MATCH (followee:User {username: $followee_username})
                RETURN follower, followee
                """,
                follower_username=follower_username,
                followee_username=followee_username,
            )
            record = result.single()
            if not record:
                return False, "One or both users not found"

            # 2) Check if already following
            result = session.run(
                """
                MATCH (follower:User {username: $follower_username})
                      -[r:FOLLOWS]->
                      (followee:User {username: $followee_username})
                RETURN r
                """,
                follower_username=follower_username,
                followee_username=followee_username,
            )
            if result.single():
                return False, f"Already following {followee_username}"

            # 3) Create FOLLOWS relationship
            result = session.run(
                """
                MATCH (follower:User {username: $follower_username})
                MATCH (followee:User {username: $followee_username})
                MERGE (follower)-[r:FOLLOWS]->(followee)
                ON CREATE SET r.messageCount = 0,
                              r.createdAt   = datetime()
                RETURN follower.username AS follower,
                       followee.username AS followee
                """,
                follower_username=follower_username,
                followee_username=followee_username,
            )
            record = result.single()
            if record:
                # No session.commit() needed – neo4j driver auto-commits
                return True, f"Successfully followed {followee_username}"
            else:
                return False, "Failed to create follow relationship"

        except Exception as e:
            return False, f"Error following user: {str(e)}"
        finally:
            session.close()

    # ==========================================================
    # UC-6: Unfollow a User
    # ==========================================================
    def unfollow_user(self, follower_username, followee_username):
        """
        Unfollow a user.
        Deletes the FOLLOWS relationship from follower -> followee.

        Returns (success: bool, message: str)
        """
        if follower_username == followee_username:
            return False, "Cannot unfollow yourself"

        session = self.db.get_session()
        try:
            result = session.run(
                """
                MATCH (follower:User {username: $follower_username})
                      -[r:FOLLOWS]->
                      (followee:User {username: $followee_username})
                DELETE r
                RETURN follower.username AS follower,
                       followee.username AS followee
                """,
                follower_username=follower_username,
                followee_username=followee_username,
            )
            record = result.single()
            if record:
                # Again, no session.commit() in new driver
                return True, f"Successfully unfollowed {followee_username}"
            else:
                return False, f"Not following {followee_username}"

        except Exception as e:
            return False, f"Error unfollowing user: {str(e)}"
        finally:
            session.close()

    # ==========================================================
    # UC-7: View Friends / Connections
    # ==========================================================
    def view_connections(self, username):
        """
        View all connections for a user.

        Returns:
          success: bool
          data: {
            "following": [ {username, name, bio}, ... ],
            "followers": [ {username, name, bio}, ... ]
          }
          message: str
        """
        session = self.db.get_session()
        try:
            # Users this person follows
            following_result = session.run(
                """
                MATCH (u:User {username: $username})-[:FOLLOWS]->(following:User)
                RETURN following.username AS username,
                       following.name     AS name,
                       following.bio      AS bio
                ORDER BY following.name
                """,
                username=username,
            )
            following = [
                {
                    "username": record["username"],
                    "name": record["name"],
                    "bio": record["bio"] or "No bio",
                }
                for record in following_result
            ]

            # Users who follow this person
            followers_result = session.run(
                """
                MATCH (follower:User)-[:FOLLOWS]->(u:User {username: $username})
                RETURN follower.username AS username,
                       follower.name     AS name,
                       follower.bio      AS bio
                ORDER BY follower.name
                """,
                username=username,
            )
            followers = [
                {
                    "username": record["username"],
                    "name": record["name"],
                    "bio": record["bio"] or "No bio",
                }
                for record in followers_result
            ]

            return True, {"following": following, "followers": followers}, "Connections retrieved successfully"

        except Exception as e:
            return False, None, f"Error viewing connections: {str(e)}"
        finally:
            session.close()

    # ==========================================================
    # UC-8: Mutual Connections
    # ==========================================================
    def mutual_connections(self, username1, username2):
        """
        Find mutual connections between two users.
        A mutual connection is a user that *both* username1 and username2 follow.

        Returns:
          success: bool
          data: [ {username, name, bio}, ... ]
          message: str
        """
        session = self.db.get_session()
        try:
            # Ensure both users exist
            result = session.run(
                """
                MATCH (u1:User {username: $username1})
                MATCH (u2:User {username: $username2})
                RETURN u1, u2
                """,
                username1=username1,
                username2=username2,
            )
            if not result.single():
                return False, None, "One or both users not found"

            # Find mutual connections
            result = session.run(
                """
                MATCH (u1:User {username: $username1})-[:FOLLOWS]->(mutual:User)
                      <-[:FOLLOWS]-(u2:User {username: $username2})
                WHERE u1 <> mutual AND u2 <> mutual
                RETURN mutual.username AS username,
                       mutual.name     AS name,
                       mutual.bio      AS bio
                ORDER BY mutual.name
                """,
                username1=username1,
                username2=username2,
            )
            mutual = [
                {
                    "username": record["username"],
                    "name": record["name"],
                    "bio": record["bio"] or "No bio",
                }
                for record in result
            ]

            return True, mutual, f"Found {len(mutual)} mutual connection(s)"

        except Exception as e:
            return False, None, f"Error finding mutual connections: {str(e)}"
        finally:
            session.close()

    # ==========================================================
    # UC-9: Friend Recommendations
    # ==========================================================
    def recommend_friends(self, username, limit=10):
        """
        UC-9: Friend Recommendations

        Suggest new users to follow based on "friends of friends":
        - Find users followed by people that *you* follow.
        - Exclude:
            * yourself
            * users you already follow
        - Rank by number of mutual connections (common friends).

        Returns:
          success: bool
          data: [ {username, name, bio, mutualCount}, ... ]
          message: str
        """
        session = self.db.get_session()
        try:
            result = session.run(
                """
                MATCH (u:User {username: $username})-[:FOLLOWS]->(f:User)-[:FOLLOWS]->(candidate:User)
                WHERE NOT (u)-[:FOLLOWS]->(candidate)   // you don't already follow them
                  AND candidate.username <> $username   // not yourself
                WITH candidate, COUNT(DISTINCT f) AS mutualCount
                ORDER BY mutualCount DESC, candidate.username
                RETURN candidate.username AS username,
                       candidate.name     AS name,
                       candidate.bio      AS bio,
                       mutualCount
                LIMIT $limit
                """,
                username=username,
                limit=limit,
            )

            recommendations = [
                {
                    "username": record["username"],
                    "name": record["name"],
                    "bio": record["bio"] or "No bio",
                    "mutualCount": record["mutualCount"],
                }
                for record in result
            ]

            return True, recommendations, f"Found {len(recommendations)} friend recommendation(s)"

        except Exception as e:
            return False, None, f"Error getting friend recommendations: {str(e)}"
        finally:
            session.close()

    # ==========================================================
    # UC-10: Search Users (by name or username)
    # ==========================================================
    def search_users(self, search_term, exclude_username=None):
        """
        UC-10: Search Users.

        Search for users where username or name CONTAINS the given term
        (case-insensitive). Optionally exclude the current user so you
        don't see yourself in the results.

        Returns:
          success: bool
          data: [ {username, name, bio}, ... ]
          message: str
        """
        session = self.db.get_session()
        try:
            if exclude_username:
                query = """
                    MATCH (u:User)
                    WHERE (toLower(u.username) CONTAINS toLower($search_term)
                           OR toLower(u.name)     CONTAINS toLower($search_term))
                      AND u.username <> $exclude_username
                    RETURN u.username AS username,
                           u.name     AS name,
                           u.bio      AS bio
                    ORDER BY u.name
                    LIMIT 20
                """
                params = {
                    "search_term": search_term,
                    "exclude_username": exclude_username,
                }
            else:
                query = """
                    MATCH (u:User)
                    WHERE toLower(u.username) CONTAINS toLower($search_term)
                       OR toLower(u.name)     CONTAINS toLower($search_term)
                    RETURN u.username AS username,
                           u.name     AS name,
                           u.bio      AS bio
                    ORDER BY u.name
                    LIMIT 20
                """
                params = {"search_term": search_term}

            result = session.run(query, **params)

            users = [
                {
                    "username": record["username"],
                    "name": record["name"],
                    "bio": record["bio"] or "No bio",
                }
                for record in result
            ]

            return True, users, f"Found {len(users)} user(s)"

        except Exception as e:
            return False, None, f"Error searching users: {str(e)}"
        finally:
            session.close()

    # ==========================================================
    # UC-11: Explore Popular Users (most-followed)
    # ==========================================================
    def get_popular_users(self, limit=10):
        """
        UC-11: Explore Popular Users.

        Returns users ordered by number of followers (descending).

        Returns:
          success: bool
          data: [ {username, name, bio, followers}, ... ]
          message: str
        """
        session = self.db.get_session()
        try:
            result = session.run(
                """
                MATCH (u:User)
                OPTIONAL MATCH (u)<-[f:FOLLOWS]-(:User)
                WITH u, COUNT(f) AS followerCount
                RETURN u.username    AS username,
                       u.name        AS name,
                       u.bio         AS bio,
                       followerCount AS followers
                ORDER BY followers DESC, username
                LIMIT $limit
                """,
                limit=limit,
            )

            users = [
                {
                    "username": record["username"],
                    "name": record["name"],
                    "bio": record["bio"] or "No bio",
                    "followers": record["followers"],
                }
                for record in result
            ]

            return True, users, f"Retrieved top {len(users)} popular user(s)"

        except Exception as e:
            return False, None, f"Error getting popular users: {str(e)}"
        finally:
            session.close()
