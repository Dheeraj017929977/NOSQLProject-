"""
Dataset Processing Module
Processes CollegeMsg.txt dataset and creates CSV files for Neo4j import
"""

import csv
import os
from collections import defaultdict


def process_college_msg_dataset(input_file, output_dir="data"):
    """
    Process CollegeMsg.txt dataset and create users.csv and follows.csv
    Format: SRC DST UNIXTS (space-separated)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    users_file = os.path.join(output_dir, "users.csv")
    follows_file = os.path.join(output_dir, "follows.csv")

    # Track unique users and their message counts
    users = set()
    follows_relationships = []
    message_counts = defaultdict(int)  # Track message frequency between users

    print(f"Processing dataset from {input_file}...")

    try:
        with open(input_file, "r") as f:
            for line_num, line in enumerate(f, 1):
                if line_num % 10000 == 0:
                    print(f"  Processed {line_num} lines...")

                parts = line.strip().split()
                if len(parts) >= 3:
                    src = parts[0]
                    dst = parts[1]
                    timestamp = parts[2]

                    users.add(src)
                    users.add(dst)

                    # Store relationship (we'll aggregate multiple messages)
                    follows_relationships.append(
                        {"source": src, "target": dst, "timestamp": timestamp}
                    )

                    # Count messages between users
                    message_counts[(src, dst)] += 1

        print(f"Found {len(users)} unique users")
        print(f"Found {len(follows_relationships)} message relationships")

        # Write users.csv
        print(f"Writing {users_file}...")
        with open(users_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["userId", "name", "email"])
            for user_id in sorted(users, key=lambda x: int(x)):
                # Generate synthetic data for users
                name = f"User_{user_id}"
                email = f"user{user_id}@college.edu"
                writer.writerow([user_id, name, email])

        print(f"Created {users_file} with {len(users)} users")

        # Write follows.csv (aggregate relationships - if users exchanged messages, they follow each other)
        print(f"Writing {follows_file}...")
        unique_follows = set()
        for src, dst in message_counts.keys():
            # Create bidirectional follows (if A messaged B, they follow each other)
            unique_follows.add((src, dst))
            unique_follows.add((dst, src))  # Make it bidirectional for social network

        with open(follows_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["source", "target", "messageCount"])
            for src, dst in sorted(unique_follows):
                count = message_counts.get((src, dst), 0) + message_counts.get(
                    (dst, src), 0
                )
                writer.writerow([src, dst, count])

        print(f"Created {follows_file} with {len(unique_follows)} follow relationships")

        return (
            True,
            f"Processed {len(users)} users and {len(unique_follows)} relationships",
        )

    except FileNotFoundError:
        return False, f"Dataset file not found: {input_file}"
    except Exception as e:
        return False, f"Error processing dataset: {str(e)}"


if __name__ == "__main__":
    # Process the dataset
    dataset_path = "CollegeMsg.txt"
    if not os.path.exists(dataset_path):
        print(f"Warning: {dataset_path} not found. Please provide the correct path.")
    else:
        success, message = process_college_msg_dataset(dataset_path)
        print(message)
