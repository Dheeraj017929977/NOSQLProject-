# Social Network Application - NoSQL Project

**Author:** Dheeraj Kumar Alla

A social networking application built with Python and Neo4j graph database, implementing user management features and utilizing the CollegeMsg dataset from SNAP (Stanford Network Analysis Project).

## Project Overview

This project implements a basic social networking application with:
- **Front-End**: Python console interface
- **Back-End**: Neo4j graph database
- **Dataset**: CollegeMsg dataset (1,899 users, 59,835 message relationships)

## Features Implemented (Person 1 - User Management + Data Loading)

### Use Cases (UC-1 to UC-4)
- **UC-1: User Registration** - New users can sign up with username, email, password, and profile information
- **UC-2: User Login** - Secure authentication with password hashing
- **UC-3: View Profile** - Users can view their profile with statistics
- **UC-4: Edit Profile** - Users can update their name, email, and bio

### Dataset Handling
- Processes CollegeMsg.txt dataset from SNAP
- Generates `users.csv` and `follows.csv` for Neo4j import
- Creates bidirectional follow relationships from message data
- Meets requirements: 1,899 nodes (exceeds 1,000) and 59,835+ relationships (exceeds 5,000)

### Neo4j Schema
- Defined constraints for uniqueness (username, email, userId)
- Created indexes for optimal query performance
- Documented property graph schema

## Prerequisites

- Python 3.7 or higher
- Neo4j Database (Community Edition or Desktop)
- Neo4j running on `bolt://localhost:7687` (default)
- CollegeMsg.txt dataset file

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dheeraj017929977/NOSQLProject-.git
   cd NOSQLProject-
   ```

2. **Create and activate virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Neo4j credentials**
   
   Create a `.env` file in the project root with your Neo4j credentials:
   ```bash
   cat > .env << EOF
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   EOF
   ```
   
   **Note:** 
   - Default credentials are usually `neo4j` / `neo4j` or `neo4j` / `password`
   - If you're using Neo4j Desktop, check your database connection settings
   - If you're using Neo4j Community Edition and forgot your password, you can reset it:
     ```bash
     neo4j stop
     neo4j-admin dbms set-initial-password your_new_password
     neo4j start
     ```
     (Note: This only works if the database hasn't been started before. For existing databases, you may need to delete the auth file first.)

5. **Start Neo4j Database**
   - If using Neo4j Desktop: Start your database instance
   - If using Neo4j Community: Run `neo4j start`
   - Default credentials: `neo4j` / `password`

6. **Prepare the dataset**
   - Place `CollegeMsg.txt` in the project directory (same folder as main.py)
   - The dataset should be named `CollegeMsg.txt`

## Setup Database

Run the setup script to initialize the database schema and load data:

```bash
# Make sure virtual environment is activated first
source venv/bin/activate  # On macOS/Linux
python setup_database.py
```

This will:
1. Create Neo4j constraints and indexes
2. Process CollegeMsg.txt dataset
3. Generate users.csv and follows.csv
4. Load all data into Neo4j

## Running the Application

Start the main console application:

```bash
# Make sure virtual environment is activated first
source venv/bin/activate  # On macOS/Linux
python main.py
```

**Note:** Always activate the virtual environment before running Python scripts:
```bash
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate
```

### Menu Options

1. **Register New User (UC-1)** - Create a new user account
2. **Login (UC-2)** - Authenticate and login
3. **View Profile (UC-3)** - View your profile information
4. **Edit Profile (UC-4)** - Update your profile details
5. **Logout** - Log out from current session
6. **Setup Database** - Initialize schema and load data (alternative to setup_database.py)
7. **Exit** - Close the application

## Project Structure

```
NOSQLProject-/
|-- main.py                 # Main console application
|-- neo4j_connection.py     # Database connection handler
|-- user_management.py      # User management (UC-1 to UC-4)
|-- dataset_processor.py    # Dataset preprocessing
|-- neo4j_schema.py         # Schema setup and documentation
|-- data_loader.py          # CSV data import to Neo4j
|-- setup_database.py       # Standalone setup script
|-- requirements.txt        # Python dependencies
|-- README.md              # This file
|-- SCHEMA.md              # Schema documentation
|-- CollegeMsg.txt         # Dataset file
`-- data/                  # Generated CSV files (created during setup)
    |-- users.csv
    `-- follows.csv
```

## Neo4j Schema

### Node Labels

**User**
- Properties:
  - `userId`: String (unique, from dataset)
  - `username`: String (unique, for login)
  - `email`: String (unique)
  - `name`: String
  - `bio`: String (optional)
  - `password`: String (bcrypt hashed)
  - `createdAt`: DateTime
  - `lastModified`: DateTime (optional)

### Relationship Types

**FOLLOWS**
- Direction: `(User)-[:FOLLOWS]->(User)`
- Properties:
  - `messageCount`: Integer (number of messages exchanged)

### Constraints

- `User.username IS UNIQUE`
- `User.email IS UNIQUE`
- `User.userId IS UNIQUE`

### Indexes

- `User.username` (for fast login lookups)
- `User.email` (for fast email lookups)
- `User.userId` (for fast dataset user lookups)

## Schema Diagram

```
+-----------------+
|      User       |
+-----------------+
| userId*         |
| username*       |
| email*          |
| name            |
| bio             |
| password        |
| createdAt       |
| lastModified    |
+--------+--------+
         |
         | FOLLOWS
         | (messageCount)
         |
         v
+-----------------+
|      User       |
+-----------------+
```

* = Unique constraint/index

## Dataset Information

- **Source**: [SNAP CollegeMsg Dataset](https://snap.stanford.edu/data/CollegeMsg.html)
- **Nodes**: 1,899 users
- **Temporal Edges**: 59,835 messages
- **Static Edges**: 20,296 unique relationships
- **Time Span**: 193 days
- **Format**: SRC DST UNIXTS (space-separated)

## Security Features

- Password hashing using bcrypt
- Username and email uniqueness validation
- Secure password storage (never stored in plain text)

## Deliverables

- Working registration/login/edit console menu
- users.csv and follows.csv generation
- Import scripts for Neo4j
- Schema diagram and Cypher setup documentation
- Complete user management system (UC-1 to UC-4)

## Usage Example

```bash
# 1. Activate virtual environment
source venv/bin/activate  # On macOS/Linux

# 2. Setup database (just run this once)
python setup_database.py

# 3. Run application
python main.py

# 3. In the menu:
#    - Register a new user
#    - Login with credentials
#    - View your profile
#    - Edit your profile
```

## Notes

- The dataset is processed to create bidirectional follow relationships (if A messaged B, both follow each other)
- User passwords are hashed using bcrypt before storage
- All timestamps are stored as Neo4j DateTime objects
- The application uses batch processing for efficient data loading

## Future Enhancements

- Additional use cases (UC-5 to UC-11) for social interactions
- Friend recommendations
- Network analysis queries
- Advanced graph algorithms

## License

This project is part of a NoSQL database course assignment.

## Contact

**Author:** Dheeraj Kumar Alla
