from connect_prod import get_database
from bson import ObjectId
from pprint import pprint

def search_dqa_palo_alto():
    """Search for Data Quality Analyst position in Palo Alto"""
    db, client = get_database('db')
    
    jobs_collection = db['jobs']
    companies_collection = db['companies']
    
    print("="*80)
    print("SEARCHING FOR DATA QUALITY ANALYST IN PALO ALTO")
    print("="*80)
    
    # Search 1: Jobs with "data quality analyst" in title
    print("\n1. Searching for 'Data Quality Analyst' in title:")
    dqa_jobs = list(jobs_collection.find({
        'title': {'$regex': 'data quality analyst', '$options': 'i'}
    }))
    print(f"   Found: {len(dqa_jobs)} jobs")
    
    for job in dqa_jobs:
        print(f"\n   {'='*70}")
        print(f"   Job Title: {job.get('title', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Job ID: {job.get('_id')}")
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"   Company: {company.get('employer_name', 'N/A')}")
        print(f"   Skills: {job.get('skills', 'N/A')}")
    
    # Search 2: Jobs in Palo Alto
    print(f"\n\n2. Searching for jobs in Palo Alto:")
    palo_alto_jobs = list(jobs_collection.find({
        'location': {'$regex': 'palo alto', '$options': 'i'}
    }))
    print(f"   Found: {len(palo_alto_jobs)} jobs")
    
    for job in palo_alto_jobs:
        print(f"\n   {'='*70}")
        print(f"   Job Title: {job.get('title', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Job ID: {job.get('_id')}")
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"   Company: {company.get('employer_name', 'N/A')}")
    
    # Search 3: Combined - Data Quality Analyst in Palo Alto
    print(f"\n\n3. Combined search: Data Quality Analyst in Palo Alto:")
    combined_jobs = list(jobs_collection.find({
        'title': {'$regex': 'data quality analyst', '$options': 'i'},
        'location': {'$regex': 'palo alto', '$options': 'i'}
    }))
    print(f"   Found: {len(combined_jobs)} jobs")
    
    for job in combined_jobs:
        print(f"\n   {'='*70}")
        print(f"   ✅ MATCH FOUND!")
        print(f"   Job Title: {job.get('title', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Job ID: {job.get('_id')}")
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"   Company: {company.get('employer_name', 'N/A')}")
        print(f"   Skills: {job.get('skills', 'N/A')}")
        if job.get('description'):
            desc = str(job.get('description', ''))
            print(f"\n   Description:")
            print(f"   {desc[:500]}...")
    
    # Search 4: If not found, search for "data quality" in Palo Alto
    if len(combined_jobs) == 0:
        print(f"\n\n4. Searching for 'data quality' jobs in Palo Alto:")
        data_quality_pa = list(jobs_collection.find({
            '$or': [
                {'title': {'$regex': 'data quality', '$options': 'i'}},
                {'description': {'$regex': 'data quality', '$options': 'i'}}
            ],
            'location': {'$regex': 'palo alto', '$options': 'i'}
        }))
        print(f"   Found: {len(data_quality_pa)} jobs")
        
        for job in data_quality_pa:
            print(f"\n   {'='*70}")
            print(f"   Job Title: {job.get('title', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Job ID: {job.get('_id')}")
            if job.get('company'):
                company = companies_collection.find_one({'_id': job['company']})
                if company:
                    print(f"   Company: {company.get('employer_name', 'N/A')}")
    
    client.close()
    
    return combined_jobs if combined_jobs else (data_quality_pa if 'data_quality_pa' in locals() else [])

if __name__ == "__main__":
    jobs = search_dqa_palo_alto()
    if jobs:
        print(f"\n✅ Found {len(jobs)} matching job(s)")
    else:
        print("\n❌ No Data Quality Analyst jobs found in Palo Alto")


