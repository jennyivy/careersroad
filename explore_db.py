from pymongo import MongoClient
from config import MONGODB_URI
from collections import defaultdict
import json
from pprint import pprint

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

def get_collection_stats(collection):
    """
    Get statistics for a collection
    """
    try:
        count = collection.count_documents({})
        return count
    except Exception as e:
        return f"Error: {e}"

def get_sample_document(collection, limit=1):
    """
    Get a sample document from a collection
    """
    try:
        sample = list(collection.find().limit(limit))
        return sample
    except Exception as e:
        return None

def analyze_document_structure(doc, prefix=""):
    """
    Recursively analyze document structure to show all fields and their types
    """
    structure = {}
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, dict):
                structure[key] = {
                    'type': 'object',
                    'fields': analyze_document_structure(value, f"{prefix}.{key}")
                }
            elif isinstance(value, list):
                if len(value) > 0:
                    if isinstance(value[0], dict):
                        structure[key] = {
                            'type': 'array[object]',
                            'sample_fields': analyze_document_structure(value[0], f"{prefix}.{key}[0]")
                        }
                    else:
                        structure[key] = {
                            'type': f'array[{type(value[0]).__name__}]',
                            'sample': value[0] if len(value) > 0 else None
                        }
                else:
                    structure[key] = {'type': 'array[]'}
            else:
                structure[key] = {
                    'type': type(value).__name__,
                    'sample': str(value)[:50] if value is not None else None
                }
    return structure

def get_collection_indexes(collection):
    """
    Get indexes for a collection
    """
    try:
        indexes = list(collection.list_indexes())
        return indexes
    except Exception as e:
        return []

def explore_collection(db, collection_name):
    """
    Explore a specific collection in detail
    """
    print(f"\n{'='*80}")
    print(f"Collection: {collection_name}")
    print(f"{'='*80}")
    
    collection = db[collection_name]
    
    # Get document count
    count = get_collection_stats(collection)
    print(f"Document count: {count}")
    
    if count == 0:
        print("Collection is empty.")
        return
    
    # Get indexes
    indexes = get_collection_indexes(collection)
    if indexes:
        print(f"\nIndexes ({len(indexes)}):")
        for idx in indexes:
            idx_name = idx.get('name', 'unknown')
            idx_keys = idx.get('key', {})
            print(f"  - {idx_name}: {idx_keys}")
    
    # Get sample documents
    samples = get_sample_document(collection, limit=3)
    if samples:
        print(f"\nSample documents ({len(samples)}):")
        for i, doc in enumerate(samples, 1):
            print(f"\n--- Sample Document {i} ---")
            # Remove _id for cleaner output, or show it
            doc_display = {k: v for k, v in doc.items()}
            pprint(doc_display, width=100, depth=5)
        
        # Analyze structure from first document
        if samples:
            print(f"\n--- Document Structure Analysis ---")
            structure = analyze_document_structure(samples[0])
            print(json.dumps(structure, indent=2, default=str))

def explore_database(db_name='db'):
    """
    Explore the entire database
    """
    db, client = get_database(db_name)
    
    if db is None:
        print("Failed to connect to database.")
        return
    
    print(f"\n{'='*80}")
    print(f"Exploring Database: {db_name}")
    print(f"{'='*80}")
    
    # Get all collections
    collections = db.list_collection_names()
    print(f"\nTotal collections: {len(collections)}")
    
    # Summary of all collections
    print(f"\n{'='*80}")
    print("Collection Summary")
    print(f"{'='*80}")
    print(f"{'Collection Name':<40} {'Document Count':<20}")
    print("-" * 80)
    
    collection_stats = []
    for col_name in collections:
        collection = db[col_name]
        count = get_collection_stats(collection)
        collection_stats.append((col_name, count))
        print(f"{col_name:<40} {str(count):<20}")
    
    # Explore each collection in detail
    print(f"\n{'='*80}")
    print("Detailed Collection Exploration")
    print(f"{'='*80}")
    
    for col_name in collections:
        explore_collection(db, col_name)
    
    # Close connection
    client.close()
    print(f"\n{'='*80}")
    print("Exploration complete!")
    print(f"{'='*80}")

def explore_specific_collection(db_name='db', collection_name=None):
    """
    Explore a specific collection
    """
    db, client = get_database(db_name)
    
    if db is None:
        print("Failed to connect to database.")
        return
    
    if collection_name:
        if collection_name in db.list_collection_names():
            explore_collection(db, collection_name)
        else:
            print(f"Collection '{collection_name}' not found.")
            print(f"Available collections: {db.list_collection_names()}")
    else:
        print("Please specify a collection name.")
    
    client.close()

if __name__ == "__main__":
    import sys
    
    # Check if a specific collection is requested
    if len(sys.argv) > 1:
        collection_name = sys.argv[1]
        explore_specific_collection('db', collection_name)
    else:
        # Explore all collections
        explore_database('db')

