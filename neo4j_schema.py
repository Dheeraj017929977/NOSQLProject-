"""
Neo4j Schema Setup Module
Defines and creates constraints, indexes, and schema for the social network
"""

from neo4j_connection import Neo4jConnection


class Neo4jSchema:
    def __init__(self, db_connection: Neo4jConnection):
        self.db = db_connection

    def setup_schema(self):
        """
        Create all constraints and indexes for the social network schema
        """
        print("Setting up Neo4j schema...")
        try:
            # get a session and make sure it's closed automatically
            with self.db.get_session() as session:

                # Create constraints (uniqueness)
                constraints = [
                    "CREATE CONSTRAINT user_username_unique IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE",
                    "CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
                    "CREATE CONSTRAINT user_userId_unique IF NOT EXISTS FOR (u:User) REQUIRE u.userId IS UNIQUE",
                ]

                for constraint in constraints:
                    try:
                        session.run(constraint)
                        print(f"  Created constraint: {constraint.split()[-1]}")
                    except Exception as e:
                        print(f"  Warning: Constraint may already exist: {e}")

                # Create indexes for better query performance
                indexes = [
                    "CREATE INDEX user_username_index IF NOT EXISTS FOR (u:User) ON (u.username)",
                    "CREATE INDEX user_email_index IF NOT EXISTS FOR (u:User) ON (u.email)",
                    "CREATE INDEX user_userId_index IF NOT EXISTS FOR (u:User) ON (u.userId)",
                ]

                for index in indexes:
                    try:
                        session.run(index)
                        print(f"  Created index: {index.split()[-1]}")
                    except Exception as e:
                        print(f"  Warning: Index may already exist: {e}")

            # no session.commit() needed – each session.run() is autocommitted
            print("Schema setup completed")
            return True

        except Exception as e:
            print(f"Error setting up schema: {e}")
            return False

    def get_schema_info(self):
        """
        Retrieve and display current schema information
        """
        session = self.db.get_session()
        try:
            print("\n=== Neo4j Schema Information ===\n")

            # Get constraints
            result = session.run("SHOW CONSTRAINTS")
            print("Constraints:")
            for record in result:
                print(f"  - {record.get('name', 'N/A')}: {record.get('type', 'N/A')}")

            # Get indexes
            result = session.run("SHOW INDEXES")
            print("\nIndexes:")
            for record in result:
                print(f"  - {record.get('name', 'N/A')}: {record.get('type', 'N/A')}")

            # Get node labels
            result = session.run("CALL db.labels()")
            print("\nNode Labels:")
            for record in result:
                print(f"  - {record['label']}")

            # Get relationship types
            result = session.run("CALL db.relationshipTypes()")
            print("\nRelationship Types:")
            for record in result:
                print(f"  - {record['relationshipType']}")

        except Exception as e:
            print(f"Error retrieving schema info: {e}")
        finally:
            session.close()
