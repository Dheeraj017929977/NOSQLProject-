"""
Neo4j Database Connection Module
Handles connection to Neo4j database
"""

from neo4j import GraphDatabase
import os


class Neo4jConnection:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initialize Neo4j connection
        Default credentials can be overridden via environment variables
        """
        self.uri = os.getenv("NEO4J_URI", uri)
        self.user = os.getenv("NEO4J_USER", user)
        self.password = os.getenv("NEO4J_PASSWORD", password)
        self.driver = None

    def connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
            # Verify connection
            self.driver.verify_connectivity()
            print("Successfully connected to Neo4j")
            return True
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            print("Please ensure Neo4j is running and credentials are correct")
            return False

    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
            print("Connection closed")

    def get_session(self):
        """Get a new database session"""
        if not self.driver:
            raise Exception("Database not connected. Call connect() first.")
        return self.driver.session()
