import sys
import os
from database import test_connection, fetch_example_data

def check_virtual_env():
    # Print Python version and location
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Running in a virtual environment: Yes")
        print(f"Virtual environment path: {sys.prefix}")
    else:
        print("Running in a virtual environment: No")

def fetch_data_from_db():
    # Test the database connection
    connection_success = test_connection()
    
    if connection_success:
        # If connection is successful, fetch some data
        print("\nFetching data from database...")
        db_info = fetch_example_data()
        print(f"Connected to database: {db_info['database']}")
        print(f"Connected as user: {db_info['user']}")
    else:
        print("Skipping data fetch due to connection failure.")

if __name__ == "__main__":
    print("Testing virtual environment configuration...")
    check_virtual_env()
    
    print("\nTesting database connection...")
    fetch_data_from_db()