# Neo4j Schema Documentation

## Property Graph Schema

### Node Labels

#### User
Represents a user in the social network.

**Properties:**
- `userId` (String, Unique) - Unique identifier from the dataset
- `username` (String, Unique) - Login username
- `email` (String, Unique) - User email address
- `name` (String) - Full name of the user
- `bio` (String, Optional) - User biography/description
- `password` (String) - Bcrypt hashed password
- `createdAt` (DateTime) - Account creation timestamp
- `lastModified` (DateTime, Optional) - Last profile update timestamp

**Constraints:**
```cypher
CREATE CONSTRAINT user_username_unique FOR (u:User) REQUIRE u.username IS UNIQUE;
CREATE CONSTRAINT user_email_unique FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT user_userId_unique FOR (u:User) REQUIRE u.userId IS UNIQUE;
```

**Indexes:**
```cypher
CREATE INDEX user_username_index FOR (u:User) ON (u.username);
CREATE INDEX user_email_index FOR (u:User) ON (u.email);
CREATE INDEX user_userId_index FOR (u:User) ON (u.userId);
```

### Relationship Types

#### FOLLOWS
Represents a follow relationship between users, derived from message exchanges.

**Direction:** `(User)-[:FOLLOWS]->(User)`

**Properties:**
- `messageCount` (Integer) - Number of messages exchanged between users

**Example:**
```cypher
(u1:User)-[:FOLLOWS {messageCount: 5}]->(u2:User)
```

## Schema Setup Cypher Queries

### Complete Schema Setup

```cypher
// Constraints
CREATE CONSTRAINT user_username_unique IF NOT EXISTS 
FOR (u:User) REQUIRE u.username IS UNIQUE;

CREATE CONSTRAINT user_email_unique IF NOT EXISTS 
FOR (u:User) REQUIRE u.email IS UNIQUE;

CREATE CONSTRAINT user_userId_unique IF NOT EXISTS 
FOR (u:User) REQUIRE u.userId IS UNIQUE;

// Indexes
CREATE INDEX user_username_index IF NOT EXISTS 
FOR (u:User) ON (u.username);

CREATE INDEX user_email_index IF NOT EXISTS 
FOR (u:User) ON (u.email);

CREATE INDEX user_userId_index IF NOT EXISTS 
FOR (u:User) ON (u.userId);
```

## Data Model Examples

### Creating a User Node

```cypher
CREATE (u:User {
    userId: "123",
    username: "johndoe",
    email: "john@example.com",
    name: "John Doe",
    bio: "Software developer",
    password: "$2b$12$...",  // bcrypt hash
    createdAt: datetime()
})
```

### Creating a Follow Relationship

```cypher
MATCH (u1:User {userId: "1"}), (u2:User {userId: "2"})
CREATE (u1)-[:FOLLOWS {messageCount: 10}]->(u2)
```

### Query Examples

**Find all users a person follows:**
```cypher
MATCH (u:User {username: "johndoe"})-[:FOLLOWS]->(following:User)
RETURN following.name, following.username
```

**Find all followers of a user:**
```cypher
MATCH (follower:User)-[:FOLLOWS]->(u:User {username: "johndoe"})
RETURN follower.name, follower.username
```

**Count followers and following:**
```cypher
MATCH (u:User {username: "johndoe"})
OPTIONAL MATCH (u)-[:FOLLOWS]->(f:User)
OPTIONAL MATCH (follower:User)-[:FOLLOWS]->(u)
RETURN u.username, 
       count(DISTINCT f) as following_count,
       count(DISTINCT follower) as followers_count
```

## Schema Visualization

```
┌─────────────────────────────────────┐
│            User Node                 │
├─────────────────────────────────────┤
│ userId: String (UNIQUE)             │
│ username: String (UNIQUE)           │
│ email: String (UNIQUE)              │
│ name: String                        │
│ bio: String (optional)              │
│ password: String (hashed)           │
│ createdAt: DateTime                 │
│ lastModified: DateTime (optional)   │
└──────────────┬──────────────────────┘
               │
               │ FOLLOWS
               │ {messageCount: Integer}
               │
               ▼
┌─────────────────────────────────────┐
│            User Node                 │
└─────────────────────────────────────┘
```

## Data Loading

### Loading Users from CSV

```cypher
LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row
MERGE (u:User {userId: row.userId})
SET u.name = row.name,
    u.email = row.email
```

### Loading Follows from CSV

```cypher
LOAD CSV WITH HEADERS FROM 'file:///follows.csv' AS row
MATCH (source:User {userId: row.source})
MATCH (target:User {userId: row.target})
MERGE (source)-[f:FOLLOWS]->(target)
SET f.messageCount = toInteger(row.messageCount)
```

## Schema Statistics

After loading the CollegeMsg dataset:
- **Nodes**: ~1,899 User nodes
- **Relationships**: ~20,296+ FOLLOWS relationships (bidirectional from messages)
- **Properties per User**: 7-8 properties
- **Properties per Relationship**: 1 property (messageCount)

## Performance Considerations

- Indexes on `username`, `email`, and `userId` ensure fast lookups for login and queries
- Unique constraints prevent duplicate users and ensure data integrity
- Batch loading is used for efficient data import (1000 records per batch)

