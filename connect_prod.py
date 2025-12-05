from pymongo import MongoClient
from urllib.parse import quote_plus
import sys

# Production MongoDB credentials
DB_USERNAME = 'xiaojiao'
DB_PASSWORD = 'Birthday_123!'
DB_CLUSTER = 'careerscrossroad-prod.rkx86.mongodb.net'

# Build connection string with proper URL encoding
def build_connection_string():
    """Build MongoDB connection string with proper URL encoding"""
    # URL encode the password to handle special characters
    encoded_password = quote_plus(DB_PASSWORD)
    connection_string = f'mongodb+srv://{DB_USERNAME}:{encoded_password}@{DB_CLUSTER}/'
    return connection_string

MONGODB_URI = build_connection_string()

def connect_to_mongodb():
    """
    Connect to MongoDB Production using the connection string
    """
    try:
        # Create a MongoClient instance
        client = MongoClient(MONGODB_URI)
        
        # Test the connection by accessing the server info
        server_info = client.server_info()
        print(f"✅ Successfully connected to MongoDB Production!")
        print(f"MongoDB version: {server_info['version']}")
        
        # List all databases
        db_list = client.list_database_names()
        print(f"Available databases: {db_list}")
        
        return client
    
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return None

def get_database(db_name='db'):
    """
    Get a specific database from MongoDB Production
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
        
        # Show collection counts
        print(f"\nCollection statistics:")
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            print(f"  - {collection_name}: {count} documents")
        
        # Close the connection when done
        client.close()
        print("\n✅ Connection closed.")
    else:
        sys.exit(1)

