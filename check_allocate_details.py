from pymongo import MongoClient
from config import MONGODB_URI
from pprint import pprint

def check_allocate_details():
    """Check details of jobs with 'allocate' in description"""
    client = MongoClient(MONGODB_URI)
    db = client['db']
    jobs_collection = db['jobs']
    companies_collection = db['companies']
    
    # Find jobs with 'allocate' in description
    jobs = list(jobs_collection.find({
        'description': {'$regex': 'allocate', '$options': 'i'}
    }))
    
    print(f"Jobs with 'allocate' in description: {len(jobs)}\n")
    
    for i, job in enumerate(jobs, 1):
        print("="*80)
        print(f"Job #{i}")
        print("="*80)
        print(f"Title: {job.get('title', 'N/A')}")
        print(f"Location: {job.get('location', 'N/A')}")
        print(f"Job ID: {job.get('_id')}")
        
        # Get company info
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"Company: {company.get('employer_name', 'N/A')}")
                print(f"Company Email: {company.get('email', 'N/A')}")
        
        # Show description with context around 'allocate'
        desc = str(job.get('description', ''))
        desc_lower = desc.lower()
        if 'allocate' in desc_lower:
            idx = desc_lower.find('allocate')
            start = max(0, idx - 100)
            end = min(len(desc), idx + 300)
            print(f"\nDescription snippet (around 'allocate'):")
            print(f"...{desc[start:end]}...")
        
        print()
    
    # Also check all analyst positions
    print("\n" + "="*80)
    print("ALL ANALYST POSITIONS IN DATABASE")
    print("="*80)
    
    analyst_jobs = list(jobs_collection.find({
        'title': {'$regex': 'analyst', '$options': 'i'}
    }))
    
    print(f"\nTotal analyst positions: {len(analyst_jobs)}\n")
    
    for i, job in enumerate(analyst_jobs, 1):
        print(f"{i}. {job.get('title', 'N/A')} at {job.get('location', 'N/A')}")
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"   Company: {company.get('employer_name', 'N/A')}")
    
    client.close()

if __name__ == "__main__":
    check_allocate_details()

