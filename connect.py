from pymongo import MongoClient
from config import MONGODB_URI

def connect_to_mongodb():
    """
    Connect to MongoDB using the connection string from config.py
    """
    try:
        # Create a MongoClient instance
        client = MongoClient(MONGODB_URI)
        
        # Test the connection by accessing the server info
        server_info = client.server_info()
        print(f"Successfully connected to MongoDB!")
        print(f"MongoDB version: {server_info['version']}")
        
        # List all databases
        db_list = client.list_database_names()
        print(f"Available databases: {db_list}")
        
        return client
    
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def get_database(db_name='db'):
    """
    Get a specific database from MongoDB
    """
    try:
        client = MongoClient(MONGODB_URI)
        db = client[db_name]
        return db, client
    except Exception as e:
        print(f"Error connecting to database '{db_name}': {e}")
        return None, None

if __name__ == "__main__":
    # Connect to MongoDB
    client = connect_to_mongodb()
    
    if client:
        # Access the 'db' database
        db = client['db']
        print(f"\nUsing database: 'db'")
        
        # List all collections in the database
        collections = db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Example: Access a specific collection
        # collection = db['your_collection_name']
        
        # Close the connection when done
        client.close()
        print("Connection closed.")

