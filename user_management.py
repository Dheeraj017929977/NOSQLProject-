"""
User Management Module
Handles user registration, login, profile viewing, and editing (UC-1 to UC-4)
"""

from neo4j_connection import Neo4jConnection
import bcrypt
from datetime import datetime


class UserManagement:
    def __init__(self, db_connection: Neo4jConnection):
        self.db = db_connection

    def register_user(self, username, password, email, name, bio=""):
        """
        UC-1: User Registration
        Register a new user with hashed password
        """
        session = self.db.get_session()
        try:
            # Check if username already exists
            result = session.run(
                "MATCH (u:User {username: $username}) RETURN u", username=username
            )
            if result.single():
                return False, "Username already exists"

            # Check if email already exists
            result = session.run("MATCH (u:User {email: $email}) RETURN u", email=email)
            if result.single():
                return False, "Email already registered"

            # Hash password
            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            # Create user node
            result = session.run(
                """
                CREATE (u:User {
                    username: $username,
                    email: $email,
                    name: $name,
                    bio: $bio,
                    password: $password,
                    createdAt: datetime()
                })
                RETURN u.username as username, u.name as name
                """,
                username=username,
                email=email,
                name=name,
                bio=bio,
                password=hashed_password,
            )

            record = result.single()
            if record:
                session.commit()
                return True, f"User '{record['username']}' registered successfully"
            else:
                return False, "Registration failed"

        except Exception as e:
            return False, f"Registration error: {str(e)}"
        finally:
            session.close()

    def login(self, username, password):
        """
        UC-2: User Login
        Authenticate user credentials
        """
        session = self.db.get_session()
        try:
            result = session.run(
                "MATCH (u:User {username: $username}) RETURN u.password as password, u.username as username, u.name as name",
                username=username,
            )
            record = result.single()

            if not record:
                return False, None, "Username not found"

            stored_password = record["password"]
            if bcrypt.checkpw(
                password.encode("utf-8"), stored_password.encode("utf-8")
            ):
                return (
                    True,
                    {"username": record["username"], "name": record["name"]},
                    "Login successful",
                )
            else:
                return False, None, "Incorrect password"

        except Exception as e:
            return False, None, f"Login error: {str(e)}"
        finally:
            session.close()

    def view_profile(self, username):
        """
        UC-3: View Profile
        View user's own profile information
        """
        session = self.db.get_session()
        try:
            result = session.run(
                """
                MATCH (u:User {username: $username})
                OPTIONAL MATCH (u)-[:FOLLOWS]->(f:User)
                OPTIONAL MATCH (follower:User)-[:FOLLOWS]->(u)
                RETURN u.username as username,
                       u.name as name,
                       u.email as email,
                       u.bio as bio,
                       u.createdAt as createdAt,
                       count(DISTINCT f) as following_count,
                       count(DISTINCT follower) as followers_count
                """,
                username=username,
            )
            record = result.single()

            if not record:
                return False, None, "User not found"

            profile = {
                "username": record["username"],
                "name": record["name"],
                "email": record["email"],
                "bio": record["bio"] or "No bio set",
                "createdAt": record["createdAt"],
                "following_count": record["following_count"],
                "followers_count": record["followers_count"],
            }
            return True, profile, "Profile retrieved successfully"

        except Exception as e:
            return False, None, f"Error viewing profile: {str(e)}"
        finally:
            session.close()

    def edit_profile(self, username, name=None, bio=None, email=None):
        """
        UC-4: Edit Profile
        Update user profile information
        """
        session = self.db.get_session()
        try:
            # Build update query dynamically based on provided fields
            updates = []
            params = {"username": username}

            if name is not None:
                updates.append("u.name = $name")
                params["name"] = name

            if bio is not None:
                updates.append("u.bio = $bio")
                params["bio"] = bio

            if email is not None:
                # Check if email is already taken by another user
                check_result = session.run(
                    "MATCH (u:User {email: $email}) WHERE u.username <> $username RETURN u",
                    email=email,
                    username=username,
                )
                if check_result.single():
                    return False, "Email already registered to another user"

                updates.append("u.email = $email")
                params["email"] = email

            if not updates:
                return False, "No fields to update"

            # Update last modified timestamp
            updates.append("u.lastModified = datetime()")

            query = f"""
                MATCH (u:User {{username: $username}})
                SET {', '.join(updates)}
                RETURN u.username as username, u.name as name
            """

            result = session.run(query, **params)
            record = result.single()

            if record:
                session.commit()
                return True, f"Profile updated successfully for '{record['username']}'"
            else:
                return False, "User not found"

        except Exception as e:
            return False, f"Error updating profile: {str(e)}"
        finally:
            session.close()
