from pymongo import MongoClient
from config import MONGODB_URI
from pprint import pprint
import re

def search_jobs(keywords=None, company=None, location=None, title=None):
    """Search for jobs with specific criteria"""
    client = MongoClient(MONGODB_URI)
    db = client['db']
    jobs_collection = db['jobs']
    
    # Build query
    query = {}
    
    if company:
        # Case-insensitive search for company name
        query['company'] = {'$regex': re.escape(company), '$options': 'i'}
    
    if location:
        # Case-insensitive search for location
        query['location'] = {'$regex': re.escape(location), '$options': 'i'}
    
    if title:
        # Case-insensitive search in title
        query['title'] = {'$regex': re.escape(title), '$options': 'i'}
    
    if keywords:
        # Search in title, description, or skills
        query['$or'] = [
            {'title': {'$regex': keywords, '$options': 'i'}},
            {'description': {'$regex': keywords, '$options': 'i'}},
            {'skills': {'$regex': keywords, '$options': 'i'}}
        ]
    
    # Execute search
    jobs = list(jobs_collection.find(query))
    
    print(f"\n{'='*80}")
    print(f"Search Results: Found {len(jobs)} job(s)")
    print(f"{'='*80}\n")
    
    if jobs:
        for i, job in enumerate(jobs, 1):
            print(f"{'='*80}")
            print(f"Job #{i}")
            print(f"{'='*80}")
            print(f"Job ID: {job.get('_id')}")
            print(f"Title: {job.get('title', 'N/A')}")
            print(f"Company ID: {job.get('company', 'N/A')}")
            print(f"Location: {job.get('location', 'N/A')}")
            print(f"Skills: {job.get('skills', 'N/A')}")
            print(f"Created Date: {job.get('created_date', 'N/A')}")
            print(f"\nDescription:")
            print(f"{job.get('description', 'N/A')[:500]}...")
            print()
            
            # Try to get company name if we have company ID
            if job.get('company'):
                companies_collection = db['companies']
                company_doc = companies_collection.find_one({'_id': job['company']})
                if company_doc:
                    print(f"Company Name: {company_doc.get('name', 'N/A')}")
                    print()
    else:
        print("No jobs found matching the criteria.")
        print("\nTrying broader search...")
        
        # Try searching for "dialogue" in description/title
        broad_query = {
            '$or': [
                {'title': {'$regex': 'dialogue', '$options': 'i'}},
                {'description': {'$regex': 'dialogue', '$options': 'i'}},
                {'location': {'$regex': 'los angeles', '$options': 'i'}},
                {'title': {'$regex': 'founding', '$options': 'i'}}
            ]
        }
        broad_results = list(jobs_collection.find(broad_query))
        print(f"Found {len(broad_results)} jobs with related keywords:")
        for job in broad_results[:5]:  # Show first 5
            print(f"  - {job.get('title', 'N/A')} at {job.get('location', 'N/A')}")
    
    client.close()

if __name__ == "__main__":
    # Search for Dialogue AI Founding Software Engineer in Los Angeles
    print("Searching for: Founding Software Engineer at Dialogue AI in Los Angeles")
    search_jobs(
        company='dialogue',
        location='los angeles',
        title='founding software engineer'
    )
    
    # Also try variations
    print("\n\n" + "="*80)
    print("Trying alternative searches...")
    print("="*80)
    
    print("\n1. Searching for 'dialogue' in any field:")
    search_jobs(keywords='dialogue')
    
    print("\n2. Searching for 'founding' in title:")
    search_jobs(title='founding')
    
    print("\n3. Searching for Los Angeles jobs:")
    search_jobs(location='los angeles')

