"""
Data Loader Module
Loads CSV data into Neo4j database
"""

from neo4j_connection import Neo4jConnection
import os
import csv


class DataLoader:
    def __init__(self, db_connection: Neo4jConnection):
        self.db = db_connection

    def load_users_from_csv(self, csv_file):
        """
        Load users from users.csv into Neo4j
        """
        if not os.path.exists(csv_file):
            return False, f"CSV file not found: {csv_file}"

        session = self.db.get_session()
        try:
            print(f"Loading users from {csv_file}...")

            # First, clear existing users from dataset (optional - comment out if you want to keep them)
            # session.run("MATCH (u:User) WHERE u.userId IS NOT NULL DELETE u")

            loaded_count = 0
            with open(csv_file, "r") as f:
                reader = csv.DictReader(f)
                batch = []
                batch_size = 1000

                for row in reader:
                    batch.append(
                        {
                            "userId": row["userId"],
                            "name": row["name"],
                            "email": row["email"],
                        }
                    )

                    if len(batch) >= batch_size:
                        self._insert_user_batch(session, batch)
                        loaded_count += len(batch)
                        print(f"  Loaded {loaded_count} users...")
                        batch = []

                # Insert remaining users
                if batch:
                    self._insert_user_batch(session, batch)
                    loaded_count += len(batch)

            session.commit()
            print(f"Successfully loaded {loaded_count} users")
            return True, f"Loaded {loaded_count} users"

        except Exception as e:
            return False, f"Error loading users: {str(e)}"
        finally:
            session.close()

    def _insert_user_batch(self, session, batch):
        """Insert a batch of users"""
        query = """
        UNWIND $batch AS user
        MERGE (u:User {userId: user.userId})
        SET u.name = user.name,
            u.email = user.email
        """
        session.run(query, batch=batch)

    def load_follows_from_csv(self, csv_file):
        """
        Load follow relationships from follows.csv into Neo4j
        """
        if not os.path.exists(csv_file):
            return False, f"CSV file not found: {csv_file}"

        session = self.db.get_session()
        try:
            print(f"Loading follow relationships from {csv_file}...")

            loaded_count = 0
            with open(csv_file, "r") as f:
                reader = csv.DictReader(f)
                batch = []
                batch_size = 1000

                for row in reader:
                    batch.append(
                        {
                            "source": row["source"],
                            "target": row["target"],
                            "messageCount": int(row.get("messageCount", 0)),
                        }
                    )

                    if len(batch) >= batch_size:
                        self._insert_follows_batch(session, batch)
                        loaded_count += len(batch)
                        print(f"  Loaded {loaded_count} relationships...")
                        batch = []

                # Insert remaining relationships
                if batch:
                    self._insert_follows_batch(session, batch)
                    loaded_count += len(batch)

            session.commit()
            print(f"Successfully loaded {loaded_count} follow relationships")
            return True, f"Loaded {loaded_count} relationships"

        except Exception as e:
            return False, f"Error loading relationships: {str(e)}"
        finally:
            session.close()

    def _insert_follows_batch(self, session, batch):
        """Insert a batch of follow relationships"""
        query = """
        UNWIND $batch AS rel
        MATCH (source:User {userId: rel.source})
        MATCH (target:User {userId: rel.target})
        MERGE (source)-[f:FOLLOWS]->(target)
        SET f.messageCount = rel.messageCount
        """
        session.run(query, batch=batch)

    def load_all_data(self, data_dir="data"):
        """
        Load all CSV files from data directory
        """
        users_file = os.path.join(data_dir, "users.csv")
        follows_file = os.path.join(data_dir, "follows.csv")

        print("\n=== Loading Data into Neo4j ===\n")

        # Load users
        success, message = self.load_users_from_csv(users_file)
        if not success:
            return False, message

        # Load relationships
        success, message = self.load_follows_from_csv(follows_file)
        if not success:
            return False, message

        return True, "All data loaded successfully"
