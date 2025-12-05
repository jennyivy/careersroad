from pymongo import MongoClient
from config import MONGODB_URI
from pprint import pprint
import json

def comprehensive_search():
    """Comprehensive search for Dialogue AI Founding Software Engineer in Los Angeles"""
    client = MongoClient(MONGODB_URI)
    db = client['db']
    jobs_collection = db['jobs']
    companies_collection = db['companies']
    
    print("="*80)
    print("COMPREHENSIVE SEARCH FOR DIALOGUE AI FOUNDING SOFTWARE ENGINEER")
    print("="*80)
    
    # Search 1: All jobs with "dialogue" anywhere
    print("\n1. Searching for 'dialogue' in any job field:")
    dialogue_jobs = list(jobs_collection.find({
        '$or': [
            {'title': {'$regex': 'dialogue', '$options': 'i'}},
            {'description': {'$regex': 'dialogue', '$options': 'i'}},
            {'skills': {'$regex': 'dialogue', '$options': 'i'}},
            {'location': {'$regex': 'dialogue', '$options': 'i'}}
        ]
    }))
    print(f"   Found: {len(dialogue_jobs)} jobs")
    for job in dialogue_jobs:
        print(f"   - {job.get('title', 'N/A')} at {job.get('location', 'N/A')}")
    
    # Search 2: All jobs with "founding" anywhere
    print("\n2. Searching for 'founding' in any job field:")
    founding_jobs = list(jobs_collection.find({
        '$or': [
            {'title': {'$regex': 'founding', '$options': 'i'}},
            {'description': {'$regex': 'founding', '$options': 'i'}},
            {'skills': {'$regex': 'founding', '$options': 'i'}}
        ]
    }))
    print(f"   Found: {len(founding_jobs)} jobs")
    for job in founding_jobs:
        print(f"   - {job.get('title', 'N/A')} at {job.get('location', 'N/A')}")
        if job.get('description'):
            desc = str(job.get('description', ''))[:200]
            print(f"     Description: {desc}...")
    
    # Search 3: All jobs in Los Angeles (various formats)
    print("\n3. Searching for Los Angeles jobs (various formats):")
    la_variations = ['los angeles', 'los angeles,', 'la,', '^la$', 'los angeles ca', 'los angeles, ca']
    la_jobs = []
    for variation in la_variations:
        jobs = list(jobs_collection.find({
            'location': {'$regex': variation, '$options': 'i'}
        }))
        la_jobs.extend(jobs)
    
    # Remove duplicates
    seen_ids = set()
    unique_la_jobs = []
    for job in la_jobs:
        if job['_id'] not in seen_ids:
            seen_ids.add(job['_id'])
            unique_la_jobs.append(job)
    
    print(f"   Found: {len(unique_la_jobs)} jobs")
    for job in unique_la_jobs:
        print(f"   - {job.get('title', 'N/A')} at {job.get('location', 'N/A')}")
        # Get company name
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"     Company: {company.get('employer_name', 'N/A')}")
    
    # Search 4: Companies with "dialogue" in name
    print("\n4. Searching for companies with 'dialogue' in name:")
    dialogue_companies = list(companies_collection.find({
        'employer_name': {'$regex': 'dialogue', '$options': 'i'}
    }))
    print(f"   Found: {len(dialogue_companies)} companies")
    for company in dialogue_companies:
        print(f"   - {company.get('employer_name', 'N/A')} (ID: {company.get('_id')})")
        # Find jobs from this company
        company_jobs = list(jobs_collection.find({'company': company['_id']}))
        print(f"     Jobs from this company: {len(company_jobs)}")
        for job in company_jobs:
            print(f"       - {job.get('title', 'N/A')} at {job.get('location', 'N/A')}")
    
    # Search 5: All unique locations
    print("\n5. All unique job locations in database:")
    all_jobs = list(jobs_collection.find({}, {'location': 1}))
    unique_locations = set()
    for job in all_jobs:
        loc = job.get('location', '').strip()
        if loc:
            unique_locations.add(loc)
    sorted_locations = sorted(unique_locations)
    print(f"   Total unique locations: {len(sorted_locations)}")
    for loc in sorted_locations[:30]:  # Show first 30
        print(f"   - {loc}")
    
    client.close()
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    if len(dialogue_jobs) == 0 and len(founding_jobs) == 0 and len(unique_la_jobs) == 0 and len(dialogue_companies) == 0:
        print("❌ The specific job (Founding Software Engineer at Dialogue AI in Los Angeles) was NOT FOUND in the database.")
        print("\nPossible reasons:")
        print("  1. The job may not be in the database yet")
        print("  2. The company name might be stored differently")
        print("  3. The location might be stored in a different format")
        print("  4. The job title might be slightly different")
    else:
        print("✅ Found some related results (see above)")

if __name__ == "__main__":
    comprehensive_search()

