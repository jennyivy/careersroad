from pymongo import MongoClient
from config import MONGODB_URI
from pprint import pprint
import re

def search_allocate_jobs():
    """Search for Data Quality Analyst positions from Allocate"""
    client = MongoClient(MONGODB_URI)
    db = client['db']
    jobs_collection = db['jobs']
    companies_collection = db['companies']
    
    print("="*80)
    print("SEARCHING FOR DATA QUALITY ANALYST POSITIONS FROM ALLOCATE")
    print("="*80)
    
    # Search 1: Companies with "allocate" in name
    print("\n1. Searching for companies with 'allocate' in name:")
    allocate_companies = list(companies_collection.find({
        'employer_name': {'$regex': 'allocate', '$options': 'i'}
    }))
    print(f"   Found: {len(allocate_companies)} companies")
    
    allocate_company_ids = []
    for company in allocate_companies:
        print(f"   - {company.get('employer_name', 'N/A')} (ID: {company.get('_id')})")
        allocate_company_ids.append(company['_id'])
    
    # Search 2: Jobs from Allocate companies
    if allocate_company_ids:
        print(f"\n2. Searching for jobs from Allocate companies:")
        allocate_jobs = list(jobs_collection.find({
            'company': {'$in': allocate_company_ids}
        }))
        print(f"   Found: {len(allocate_jobs)} jobs")
        
        for job in allocate_jobs:
            print(f"\n   {'='*70}")
            print(f"   Job Title: {job.get('title', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Job ID: {job.get('_id')}")
            print(f"   Skills: {job.get('skills', 'N/A')}")
            print(f"   Created Date: {job.get('created_date', 'N/A')}")
            if job.get('description'):
                desc = str(job.get('description', ''))
                print(f"\n   Description:")
                print(f"   {desc[:500]}...")
    
    # Search 3: Jobs with "data quality analyst" in title
    print(f"\n\n3. Searching for jobs with 'data quality analyst' in title:")
    dqa_jobs = list(jobs_collection.find({
        'title': {'$regex': 'data quality analyst', '$options': 'i'}
    }))
    print(f"   Found: {len(dqa_jobs)} jobs")
    
    for job in dqa_jobs:
        print(f"\n   {'='*70}")
        print(f"   Job Title: {job.get('title', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Job ID: {job.get('_id')}")
        # Get company name
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"   Company: {company.get('employer_name', 'N/A')}")
        print(f"   Skills: {job.get('skills', 'N/A')}")
        if job.get('description'):
            desc = str(job.get('description', ''))
            print(f"\n   Description:")
            print(f"   {desc[:500]}...")
    
    # Search 4: Jobs with "data quality" anywhere
    print(f"\n\n4. Searching for jobs with 'data quality' in any field:")
    data_quality_jobs = list(jobs_collection.find({
        '$or': [
            {'title': {'$regex': 'data quality', '$options': 'i'}},
            {'description': {'$regex': 'data quality', '$options': 'i'}},
            {'skills': {'$regex': 'data quality', '$options': 'i'}}
        ]
    }))
    print(f"   Found: {len(data_quality_jobs)} jobs")
    
    for job in data_quality_jobs:
        print(f"\n   {'='*70}")
        print(f"   Job Title: {job.get('title', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        # Get company name
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"   Company: {company.get('employer_name', 'N/A')}")
        if job.get('description'):
            desc = str(job.get('description', ''))
            # Find where "data quality" appears
            desc_lower = desc.lower()
            if 'data quality' in desc_lower:
                idx = desc_lower.find('data quality')
                start = max(0, idx - 100)
                end = min(len(desc), idx + 200)
                print(f"\n   Description snippet (around 'data quality'):")
                print(f"   ...{desc[start:end]}...")
    
    # Search 5: Jobs with "allocate" in description or title
    print(f"\n\n5. Searching for jobs with 'allocate' in any field:")
    allocate_in_jobs = list(jobs_collection.find({
        '$or': [
            {'title': {'$regex': 'allocate', '$options': 'i'}},
            {'description': {'$regex': 'allocate', '$options': 'i'}},
            {'skills': {'$regex': 'allocate', '$options': 'i'}}
        ]
    }))
    print(f"   Found: {len(allocate_in_jobs)} jobs")
    
    for job in allocate_in_jobs:
        print(f"\n   {'='*70}")
        print(f"   Job Title: {job.get('title', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        # Get company name
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"   Company: {company.get('employer_name', 'N/A')}")
    
    client.close()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    if allocate_company_ids and len(allocate_jobs) > 0:
        print(f"✅ Found {len(allocate_jobs)} job(s) from Allocate company/companies")
    else:
        print("❌ No jobs found from companies named 'Allocate'")
    
    if len(dqa_jobs) > 0:
        print(f"✅ Found {len(dqa_jobs)} job(s) with 'Data Quality Analyst' in title")
    else:
        print("❌ No jobs found with 'Data Quality Analyst' in title")
    
    if len(data_quality_jobs) > 0:
        print(f"✅ Found {len(data_quality_jobs)} job(s) with 'data quality' mentioned")
    else:
        print("❌ No jobs found with 'data quality' mentioned")

if __name__ == "__main__":
    search_allocate_jobs()

