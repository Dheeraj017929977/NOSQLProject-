"""
Social Graph Module
Handles relationship-based use cases (follow/unfollow, view connections, mutual connections)
Uses Cypher queries for FOLLOWS relationships
"""

from neo4j_connection import Neo4jConnection


class SocialGraph:
    def __init__(self, db_connection: Neo4jConnection):
        self.db = db_connection

    def follow_user(self, follower_username, followee_username):
        """
        Follow a user
        Creates a FOLLOWS relationship from follower to followee
        """
        if follower_username == followee_username:
            return False, "Cannot follow yourself"

        session = self.db.get_session()
        try:
            # Check if both users exist
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

            # Check if already following
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

            # Create FOLLOWS relationship
            result = session.run(
                """
                MATCH (follower:User {username: $follower_username})
                MATCH (followee:User {username: $followee_username})
                MERGE (follower)-[r:FOLLOWS]->(followee)
                ON CREATE SET r.messageCount = 0, r.createdAt = datetime()
                RETURN follower.username as follower, followee.username as followee
                """,
                follower_username=follower_username,
                followee_username=followee_username,
            )
            record = result.single()
            if record:
                session.commit()
                return True, f"Successfully followed {followee_username}"
            else:
                return False, "Failed to create follow relationship"

        except Exception as e:
            return False, f"Error following user: {str(e)}"
        finally:
            session.close()

    def unfollow_user(self, follower_username, followee_username):
        """
        Unfollow a user
        Removes the FOLLOWS relationship from follower to followee
        """
        if follower_username == followee_username:
            return False, "Cannot unfollow yourself"

        session = self.db.get_session()
        try:
            # Check if relationship exists
            result = session.run(
                """
                MATCH (follower:User {username: $follower_username})
                -[r:FOLLOWS]->
                (followee:User {username: $followee_username})
                DELETE r
                RETURN follower.username as follower, followee.username as followee
                """,
                follower_username=follower_username,
                followee_username=followee_username,
            )
            record = result.single()
            if record:
                session.commit()
                return True, f"Successfully unfollowed {followee_username}"
            else:
                return False, f"Not following {followee_username}"

        except Exception as e:
            return False, f"Error unfollowing user: {str(e)}"
        finally:
            session.close()

    def view_connections(self, username):
        """
        View all connections (following and followers) for a user
        Returns both users the person follows and users who follow them
        """
        session = self.db.get_session()
        try:
            # Get users this person follows
            following_result = session.run(
                """
                MATCH (u:User {username: $username})-[:FOLLOWS]->(following:User)
                RETURN following.username as username,
                       following.name as name,
                       following.bio as bio
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

            # Get users who follow this person
            followers_result = session.run(
                """
                MATCH (follower:User)-[:FOLLOWS]->(u:User {username: $username})
                RETURN follower.username as username,
                       follower.name as name,
                       follower.bio as bio
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

    def mutual_connections(self, username1, username2):
        """
        Find mutual connections between two users
        Returns users that both username1 and username2 follow
        """
        session = self.db.get_session()
        try:
            # Check if both users exist
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
                MATCH (u1:User {username: $username1})-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(u2:User {username: $username2})
                WHERE u1 <> mutual AND u2 <> mutual
                RETURN mutual.username as username,
                       mutual.name as name,
                       mutual.bio as bio
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

    def search_users(self, search_term, exclude_username=None):
        """
        Search for users by username or name
        Useful for finding users to follow
        """
        session = self.db.get_session()
        try:
            if exclude_username:
                result = session.run(
                    """
                    MATCH (u:User)
                    WHERE (u.username CONTAINS $search_term OR u.name CONTAINS $search_term)
                    AND u.username <> $exclude_username
                    RETURN u.username as username,
                           u.name as name,
                           u.bio as bio
                    ORDER BY u.name
                    LIMIT 20
                    """,
                    search_term=search_term,
                    exclude_username=exclude_username,
                )
            else:
                result = session.run(
                    """
                    MATCH (u:User)
                    WHERE u.username CONTAINS $search_term OR u.name CONTAINS $search_term
                    RETURN u.username as username,
                           u.name as name,
                           u.bio as bio
                    ORDER BY u.name
                    LIMIT 20
                    """,
                    search_term=search_term,
                )

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

