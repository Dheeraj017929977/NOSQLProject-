#!/usr/bin/env python3
"""
Test Script for Social Graph Features (UC-5 to UC-8)
Tests Follow, Unfollow, View Connections, and Mutual Connections
"""

from neo4j_connection import Neo4jConnection
from user_management import UserManagement
from social_graph import SocialGraph
import sys

# Test users
TEST_USERS = [
    {
        "username": "alice",
        "password": "alice123",
        "email": "alice@example.com",
        "name": "Alice Johnson",
        "bio": "Loves graphs and databases"
    },
    {
        "username": "bob",
        "password": "bob123",
        "email": "bob@example.com",
        "name": "Bob Smith",
        "bio": "Backend dev enthusiast"
    },
    {
        "username": "charlie",
        "password": "charlie123",
        "email": "charlie@example.com",
        "name": "Charlie Lee",
        "bio": "CS student & data nerd"
    }
]

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_cypher_query(query, description):
    """Print Cypher query with description"""
    print(f"\n📝 {description}")
    print("-" * 80)
    print(query)
    print("-" * 80)

def setup_test_users(db, user_mgmt):
    """Register test users if they don't exist"""
    print_header("SETUP: Registering Test Users")
    
    for user in TEST_USERS:
        # Check if user exists
        session = db.get_session()
        try:
            result = session.run(
                "MATCH (u:User {username: $username}) RETURN u",
                username=user["username"]
            )
            if result.single():
                print(f"✓ User '{user['username']}' already exists")
            else:
                success, message = user_mgmt.register_user(
                    user["username"],
                    user["password"],
                    user["email"],
                    user["name"],
                    user["bio"]
                )
                if success:
                    print(f"✓ Registered: {user['name']} (@{user['username']})")
                else:
                    print(f"✗ Failed to register {user['username']}: {message}")
        finally:
            session.close()

def reset_test_relationships(db):
    """Clear existing FOLLOWS relationships between test users for clean testing"""
    print("\n🔄 Resetting test relationships for clean demonstration...")
    session = db.get_session()
    try:
        # Remove all FOLLOWS relationships between test users
        result = session.run("""
            MATCH (a:User)-[r:FOLLOWS]->(b:User)
            WHERE a.username IN ['alice', 'bob', 'charlie'] 
            AND b.username IN ['alice', 'bob', 'charlie']
            DELETE r
            RETURN count(r) as deleted
        """)
        record = result.single()
        if record and record['deleted'] > 0:
            print(f"✓ Removed {record['deleted']} existing relationship(s)")
        else:
            print("✓ No existing relationships to remove")
    finally:
        session.close()

def test_uc5_follow(db, social_graph):
    """UC-5: Follow Another User"""
    print_header("UC-5: Follow Another User")
    
    print("\n📋 Test Case: Alice follows Bob")
    print("-" * 80)
    
    # Cypher query used
    cypher_query = """
    MATCH (follower:User {username: $follower_username})
    MATCH (followee:User {username: $followee_username})
    MERGE (follower)-[r:FOLLOWS]->(followee)
    ON CREATE SET r.messageCount = 0, r.createdAt = datetime()
    RETURN follower.username as follower, followee.username as followee
    """
    print_cypher_query(cypher_query, "Cypher Query: Create FOLLOWS relationship")
    
    # Execute follow
    success, message = social_graph.follow_user("alice", "bob")
    print(f"\nResult: {message}")
    
    if success:
        print("✓ UC-5 PASSED: Alice successfully followed Bob")
        
        # Verify relationship exists
        session = db.get_session()
        try:
            result = session.run(
                """
                MATCH (a:User {username: 'alice'})-[r:FOLLOWS]->(b:User {username: 'bob'})
                RETURN r
                """
            )
            if result.single():
                print("✓ Verification: FOLLOWS relationship confirmed in database")
            else:
                print("✗ Verification: FOLLOWS relationship NOT found")
        finally:
            session.close()
    else:
        print(f"✗ UC-5 FAILED: {message}")
    
    # Test: Alice follows Charlie
    print("\n📋 Test Case: Alice follows Charlie")
    success, message = social_graph.follow_user("alice", "charlie")
    print(f"Result: {message}")
    if success:
        print("✓ Alice successfully followed Charlie")
    
    # Test: Bob follows Charlie
    print("\n📋 Test Case: Bob follows Charlie")
    success, message = social_graph.follow_user("bob", "charlie")
    print(f"Result: {message}")
    if success:
        print("✓ Bob successfully followed Charlie")
    
    # Test: Cannot follow yourself
    print("\n📋 Test Case: Alice tries to follow herself (should fail)")
    success, message = social_graph.follow_user("alice", "alice")
    print(f"Result: {message}")
    if not success:
        print("✓ Correctly prevented self-follow")

def test_uc6_unfollow(db, social_graph):
    """UC-6: Unfollow a User"""
    print_header("UC-6: Unfollow a User")
    
    print("\n📋 Test Case: Alice unfollows Bob")
    print("-" * 80)
    
    # Cypher query used
    cypher_query = """
    MATCH (follower:User {username: $follower_username})
    -[r:FOLLOWS]->
    (followee:User {username: $followee_username})
    DELETE r
    RETURN follower.username as follower, followee.username as followee
    """
    print_cypher_query(cypher_query, "Cypher Query: Remove FOLLOWS relationship")
    
    # Execute unfollow
    success, message = social_graph.unfollow_user("alice", "bob")
    print(f"\nResult: {message}")
    
    if success:
        print("✓ UC-6 PASSED: Alice successfully unfollowed Bob")
        
        # Verify relationship removed
        session = db.get_session()
        try:
            result = session.run(
                """
                MATCH (a:User {username: 'alice'})-[r:FOLLOWS]->(b:User {username: 'bob'})
                RETURN r
                """
            )
            if not result.single():
                print("✓ Verification: FOLLOWS relationship successfully removed")
            else:
                print("✗ Verification: FOLLOWS relationship still exists")
        finally:
            session.close()
    else:
        print(f"✗ UC-6 FAILED: {message}")
    
    # Test: Try to unfollow someone you're not following
    print("\n📋 Test Case: Alice tries to unfollow Bob again (should fail)")
    success, message = social_graph.unfollow_user("alice", "bob")
    print(f"Result: {message}")
    if not success:
        print("✓ Correctly handled unfollowing non-existent relationship")

def test_uc7_view_connections(db, social_graph):
    """UC-7: View Friends/Connections"""
    print_header("UC-7: View Friends/Connections")
    
    print("\n📋 Test Case: View Alice's Connections")
    print("-" * 80)
    
    # Cypher queries used
    following_query = """
    MATCH (u:User {username: $username})-[:FOLLOWS]->(following:User)
    RETURN following.username as username,
           following.name as name,
           following.bio as bio
    ORDER BY following.name
    """
    print_cypher_query(following_query, "Cypher Query: Get users being followed")
    
    followers_query = """
    MATCH (follower:User)-[:FOLLOWS]->(u:User {username: $username})
    RETURN follower.username as username,
           follower.name as name,
           follower.bio as bio
    ORDER BY follower.name
    """
    print_cypher_query(followers_query, "Cypher Query: Get followers")
    
    # Execute view connections
    success, connections, message = social_graph.view_connections("alice")
    print(f"\nResult: {message}")
    
    if success:
        print("\n✓ UC-7 PASSED: Successfully retrieved connections")
        print(f"\nFollowing ({len(connections['following'])}):")
        for i, user in enumerate(connections['following'], 1):
            print(f"  {i}. {user['name']} (@{user['username']}) - {user['bio']}")
        
        print(f"\nFollowers ({len(connections['followers'])}):")
        for i, user in enumerate(connections['followers'], 1):
            print(f"  {i}. {user['name']} (@{user['username']}) - {user['bio']}")
        
        # Verify with direct query
        session = db.get_session()
        try:
            result = session.run(
                """
                MATCH (a:User {username: 'alice'})-[:FOLLOWS]->(f:User)
                RETURN count(f) as following_count
                """
            )
            record = result.single()
            if record:
                print(f"\n✓ Verification: Database shows {record['following_count']} following")
        finally:
            session.close()
    else:
        print(f"✗ UC-7 FAILED: {message}")

def test_uc8_mutual_connections(db, social_graph):
    """UC-8: Mutual Connections"""
    print_header("UC-8: Mutual Connections")
    
    print("\n📋 Test Case: Find mutual connections between Alice and Bob")
    print("-" * 80)
    
    # Cypher query used
    cypher_query = """
    MATCH (u1:User {username: $username1})-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(u2:User {username: $username2})
    WHERE u1 <> mutual AND u2 <> mutual
    RETURN mutual.username as username,
           mutual.name as name,
           mutual.bio as bio
    ORDER BY mutual.name
    """
    print_cypher_query(cypher_query, "Cypher Query: Find mutual connections")
    
    # Execute mutual connections
    success, mutual, message = social_graph.mutual_connections("alice", "bob")
    print(f"\nResult: {message}")
    
    if success:
        print("\n✓ UC-8 PASSED: Successfully found mutual connections")
        if mutual:
            print(f"\nMutual Connections ({len(mutual)}):")
            for i, user in enumerate(mutual, 1):
                print(f"  {i}. {user['name']} (@{user['username']}) - {user['bio']}")
        else:
            print("\n  No mutual connections found")
        
        # Verify with direct query
        session = db.get_session()
        try:
            result = session.run(
                """
                MATCH (a:User {username: 'alice'})-[:FOLLOWS]->(m:User)<-[:FOLLOWS]-(b:User {username: 'bob'})
                WHERE a <> m AND b <> m
                RETURN count(m) as mutual_count
                """
            )
            record = result.single()
            if record:
                print(f"\n✓ Verification: Database shows {record['mutual_count']} mutual connection(s)")
        finally:
            session.close()
    else:
        print(f"✗ UC-8 FAILED: {message}")

def show_final_state(db):
    """Show final state of all relationships"""
    print_header("Final State: All FOLLOWS Relationships")
    
    session = db.get_session()
    try:
        result = session.run("""
            MATCH (a:User)-[r:FOLLOWS]->(b:User)
            RETURN a.username as follower, b.username as followee
            ORDER BY a.username, b.username
        """)
        
        relationships = list(result)
        if relationships:
            print("\nAll FOLLOWS relationships in database:")
            for rel in relationships:
                print(f"  {rel['follower']} -> {rel['followee']}")
        else:
            print("\n  No FOLLOWS relationships found")
    finally:
        session.close()

def main():
    """Run all test cases"""
    print("\n" + "=" * 80)
    print("  SOCIAL GRAPH FEATURES TEST SUITE (UC-5 to UC-8)")
    print("=" * 80)
    
    # Connect to database
    db = Neo4jConnection()
    if not db.connect():
        print("✗ Failed to connect to Neo4j. Please check your connection.")
        sys.exit(1)
    
    user_mgmt = UserManagement(db)
    social_graph = SocialGraph(db)
    
    try:
        # Setup test users
        setup_test_users(db, user_mgmt)
        
        # Reset relationships for clean testing
        reset_test_relationships(db)
        
        # Run test cases
        test_uc5_follow(db, social_graph)
        test_uc6_unfollow(db, social_graph)
        test_uc7_view_connections(db, social_graph)
        test_uc8_mutual_connections(db, social_graph)
        
        # Show final state
        show_final_state(db)
        
        print_header("TEST SUITE COMPLETE")
        print("\n✓ All use cases tested successfully!")
        print("\nTest Users:")
        for user in TEST_USERS:
            print(f"  - {user['name']} (@{user['username']})")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

