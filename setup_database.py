"""
Database Setup Script
Standalone script to setup Neo4j schema and load data
"""

from neo4j_connection import Neo4jConnection
from neo4j_schema import Neo4jSchema
from data_loader import DataLoader
from dataset_processor import process_college_msg_dataset
import os


def main():
    print("=" * 60)
    print("Neo4j Database Setup Script")
    print("=" * 60)
    print()

    # Connect to Neo4j
    db = Neo4jConnection()
    if not db.connect():
        print("\nFailed to connect to Neo4j. Please check your connection settings.")
        return

    try:
        # Step 1: Setup Schema
        print("\n[Step 1/3] Setting up schema...")
        schema = Neo4jSchema(db)
        schema.setup_schema()
        schema.get_schema_info()

        # Step 2: Process Dataset
        print("\n[Step 2/3] Processing dataset...")
        dataset_path = "CollegeMsg.txt"
        if not os.path.exists(dataset_path):
            print(f"Error: Dataset file not found at {dataset_path}")
            print("Please ensure CollegeMsg.txt is in the project directory")
            return

        success, message = process_college_msg_dataset(dataset_path)
        if not success:
            print(f"Error: {message}")
            return
        print(message)

        # Step 3: Load Data
        print("\n[Step 3/3] Loading data into Neo4j...")
        loader = DataLoader(db)
        success, message = loader.load_all_data()
        if not success:
            print(f"Error: {message}")
            return

        print("\n" + "=" * 60)
        print("Database setup completed successfully!")
        print("=" * 60)
        print("\nYou can now run the main application: python main.py")

    except Exception as e:
        print(f"\nError during setup: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
