"""
Main Console Application
Social Network Application with User Management
"""

from neo4j_connection import Neo4jConnection
from user_management import UserManagement
from neo4j_schema import Neo4jSchema
from data_loader import DataLoader
from dataset_processor import process_college_msg_dataset
import os
import sys


class SocialNetworkApp:
    def __init__(self):
        self.db = Neo4jConnection()
        self.user_mgmt = None
        self.current_user = None

    def initialize(self):
        """Initialize database connection and setup"""
        print("=" * 60)
        print("Social Network Application - User Management")
        print("=" * 60)
        print()

        if not self.db.connect():
            print("\nPlease ensure Neo4j is running and try again.")
            print("Default connection: bolt://localhost:7687")
            print(
                "You can set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD environment variables"
            )
            return False

        self.user_mgmt = UserManagement(self.db)
        return True

    def display_main_menu(self):
        """Display main menu options"""
        print("\n" + "=" * 60)
        print("MAIN MENU")
        print("=" * 60)
        if self.current_user:
            print(
                f"Logged in as: {self.current_user['name']} (@{self.current_user['username']})"
            )
        print("1. Register New User (UC-1)")
        print("2. Login (UC-2)")
        print("3. View Profile (UC-3)")
        print("4. Edit Profile (UC-4)")
        print("5. Logout")
        print("6. Setup Database (Schema + Load Data)")
        print("7. Exit")
        print("=" * 60)

    def register_user(self):
        """Handle user registration"""
        print("\n--- User Registration (UC-1) ---")
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty")
            return

        password = input("Password: ").strip()
        if not password:
            print("Password cannot be empty")
            return

        email = input("Email: ").strip()
        if not email:
            print("Email cannot be empty")
            return

        name = input("Full Name: ").strip()
        if not name:
            print("Name cannot be empty")
            return

        bio = input("Bio (optional): ").strip()

        success, message = self.user_mgmt.register_user(
            username, password, email, name, bio
        )
        print(f"\n{message}")
        if success:
            print("You can now login with your credentials.")

    def login_user(self):
        """Handle user login"""
        print("\n--- User Login (UC-2) ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        success, user_data, message = self.user_mgmt.login(username, password)
        print(f"\n{message}")
        if success:
            self.current_user = user_data
            print(f"Welcome, {user_data['name']}!")

    def view_profile(self):
        """Handle viewing profile"""
        if not self.current_user:
            print("\nPlease login first to view your profile.")
            return

        print("\n--- View Profile (UC-3) ---")
        success, profile, message = self.user_mgmt.view_profile(
            self.current_user["username"]
        )

        if success:
            print("\n" + "-" * 40)
            print("PROFILE INFORMATION")
            print("-" * 40)
            print(f"Username: {profile['username']}")
            print(f"Name: {profile['name']}")
            print(f"Email: {profile['email']}")
            print(f"Bio: {profile['bio']}")
            print(f"Created: {profile['createdAt']}")
            print(f"Following: {profile['following_count']} users")
            print(f"Followers: {profile['followers_count']} users")
            print("-" * 40)
        else:
            print(f"\n{message}")

    def edit_profile(self):
        """Handle profile editing"""
        if not self.current_user:
            print("\nPlease login first to edit your profile.")
            return

        print("\n--- Edit Profile (UC-4) ---")
        print("Leave fields empty to keep current values")

        name = input(f"Name (current): ").strip()
        name = name if name else None

        email = input(f"Email (current): ").strip()
        email = email if email else None

        bio = input(f"Bio (current): ").strip()
        bio = bio if bio else None

        if not any([name, email, bio]):
            print("No changes provided")
            return

        success, message = self.user_mgmt.edit_profile(
            self.current_user["username"], name=name, email=email, bio=bio
        )
        print(f"\n{message}")

    def setup_database(self):
        """Setup database schema and load data"""
        print("\n--- Database Setup ---")
        print("This will:")
        print("1. Create schema (constraints and indexes)")
        print("2. Process CollegeMsg.txt dataset")
        print("3. Load users and relationships into Neo4j")
        print()

        confirm = input("Continue? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Setup cancelled")
            return

        # Setup schema
        schema = Neo4jSchema(self.db)
        if not schema.setup_schema():
            print("Schema setup failed")
            return

        # Process dataset
        dataset_path = "CollegeMsg.txt"
        if not os.path.exists(dataset_path):
            print(f"\nDataset file not found at: {dataset_path}")
            print("Please ensure CollegeMsg.txt is in the project directory")
            return

        print("\nProcessing dataset...")
        success, message = process_college_msg_dataset(dataset_path)
        if not success:
            print(f"Error: {message}")
            return
        print(message)

        # Load data
        loader = DataLoader(self.db)
        success, message = loader.load_all_data()
        if not success:
            print(f"Error: {message}")
            return

        print("\nDatabase setup completed successfully!")

    def logout(self):
        """Handle logout"""
        if self.current_user:
            print(f"\nLogged out: {self.current_user['name']}")
            self.current_user = None
        else:
            print("\nNo user logged in")

    def run(self):
        """Main application loop"""
        if not self.initialize():
            return

        while True:
            try:
                self.display_main_menu()
                choice = input("\nEnter your choice (1-7): ").strip()

                if choice == "1":
                    self.register_user()
                elif choice == "2":
                    self.login_user()
                elif choice == "3":
                    self.view_profile()
                elif choice == "4":
                    self.edit_profile()
                elif choice == "5":
                    self.logout()
                elif choice == "6":
                    self.setup_database()
                elif choice == "7":
                    print("\nThank you for using Social Network Application!")
                    break
                else:
                    print("\nInvalid choice. Please try again.")

            except KeyboardInterrupt:
                print("\n\nApplication interrupted by user")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")

        self.db.close()


if __name__ == "__main__":
    app = SocialNetworkApp()
    app.run()
