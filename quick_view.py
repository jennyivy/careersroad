from pymongo import MongoClient
from config import MONGODB_URI
from pprint import pprint

def get_database(db_name='db'):
    """Get a specific database from MongoDB"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[db_name]
        return db, client
    except Exception as e:
        print(f"Error connecting to database '{db_name}': {e}")
        return None, None

def quick_view_collection(collection_name, limit=5):
    """Quick view of a collection - count and sample documents"""
    db, client = get_database('db')
    
    if db is None:
        return
    
    collection = db[collection_name]
    count = collection.count_documents({})
    
    print(f"\n{'='*60}")
    print(f"Collection: {collection_name}")
    print(f"Total documents: {count}")
    print(f"{'='*60}")
    
    if count > 0:
        print(f"\nSample documents (showing {min(limit, count)}):")
        samples = list(collection.find().limit(limit))
        for i, doc in enumerate(samples, 1):
            print(f"\n--- Document {i} ---")
            pprint(doc, width=100, depth=3)
    else:
        print("Collection is empty.")
    
    client.close()

def list_collections():
    """List all collections with document counts"""
    db, client = get_database('db')
    
    if db is None:
        return
    
    collections = db.list_collection_names()
    print(f"\n{'='*60}")
    print(f"Database: db")
    print(f"Total collections: {len(collections)}")
    print(f"{'='*60}\n")
    
    print(f"{'Collection Name':<40} {'Count':<15}")
    print("-" * 60)
    
    for col_name in collections:
        collection = db[col_name]
        count = collection.count_documents({})
        print(f"{col_name:<40} {count:<15}")
    
    client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        collection_name = sys.argv[1]
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        quick_view_collection(collection_name, limit)
    else:
        list_collections()
        print("\nUsage: python quick_view.py <collection_name> [limit]")
        print("Example: python quick_view.py users 10")

