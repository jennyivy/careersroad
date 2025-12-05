from connect_prod import get_database
from pprint import pprint
import re

def search_variance_product_engineer():
    """Search for Product Engineer positions from Variance in production database"""
    db, client = get_database('db')
    
    if db is None:
        print("Failed to connect to database.")
        return
    
    jobs_collection = db['jobs']
    companies_collection = db['companies']
    
    print("="*80)
    print("SEARCHING FOR PRODUCT ENGINEER POSITIONS FROM VARIANCE")
    print("="*80)
    
    # Search 1: Companies with "variance" in name
    print("\n1. Searching for companies with 'variance' in name:")
    variance_companies = list(companies_collection.find({
        'employer_name': {'$regex': 'variance', '$options': 'i'}
    }))
    print(f"   Found: {len(variance_companies)} companies")
    
    variance_company_ids = []
    for company in variance_companies:
        print(f"   - {company.get('employer_name', 'N/A')} (ID: {company.get('_id')})")
        print(f"     Email: {company.get('email', 'N/A')}")
        variance_company_ids.append(company['_id'])
    
    # Search 2: Jobs from Variance companies
    if variance_company_ids:
        print(f"\n2. Searching for jobs from Variance companies:")
        variance_jobs = list(jobs_collection.find({
            'company': {'$in': variance_company_ids}
        }))
        print(f"   Found: {len(variance_jobs)} jobs")
        
        for job in variance_jobs:
            print(f"\n   {'='*70}")
            print(f"   Job Title: {job.get('title', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Job ID: {job.get('_id')}")
            print(f"   Skills: {job.get('skills', 'N/A')}")
            print(f"   Created Date: {job.get('created_date', 'N/A')}")
            if job.get('description'):
                desc = str(job.get('description', ''))
                print(f"\n   Description:")
                print(f"   {desc[:800]}...")
    else:
        print("\n   No Variance companies found, checking all jobs...")
    
    # Search 3: Jobs with "product engineer" in title
    print(f"\n\n3. Searching for jobs with 'product engineer' in title:")
    product_engineer_jobs = list(jobs_collection.find({
        'title': {'$regex': 'product engineer', '$options': 'i'}
    }))
    print(f"   Found: {len(product_engineer_jobs)} jobs")
    
    for job in product_engineer_jobs:
        print(f"\n   {'='*70}")
        print(f"   Job Title: {job.get('title', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Job ID: {job.get('_id')}")
        # Get company name
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"   Company: {company.get('employer_name', 'N/A')}")
                print(f"   Company Email: {company.get('email', 'N/A')}")
        print(f"   Skills: {job.get('skills', 'N/A')}")
        if job.get('description'):
            desc = str(job.get('description', ''))
            print(f"\n   Description:")
            print(f"   {desc[:800]}...")
    
    # Search 4: Jobs with "variance" in any field
    print(f"\n\n4. Searching for jobs with 'variance' in any field:")
    variance_in_jobs = list(jobs_collection.find({
        '$or': [
            {'title': {'$regex': 'variance', '$options': 'i'}},
            {'description': {'$regex': 'variance', '$options': 'i'}},
            {'skills': {'$regex': 'variance', '$options': 'i'}}
        ]
    }))
    print(f"   Found: {len(variance_in_jobs)} jobs")
    
    for job in variance_in_jobs:
        print(f"\n   {'='*70}")
        print(f"   Job Title: {job.get('title', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        # Get company name
        if job.get('company'):
            company = companies_collection.find_one({'_id': job['company']})
            if company:
                print(f"   Company: {company.get('employer_name', 'N/A')}")
    
    # Search 5: Combined search - Product Engineer from Variance
    print(f"\n\n5. Combined search: Product Engineer from Variance:")
    if variance_company_ids:
        combined_jobs = list(jobs_collection.find({
            'company': {'$in': variance_company_ids},
            'title': {'$regex': 'product engineer', '$options': 'i'}
        }))
        print(f"   Found: {len(combined_jobs)} jobs matching both criteria")
        
        for job in combined_jobs:
            print(f"\n   {'='*70}")
            print(f"   ✅ MATCH FOUND!")
            print(f"   Job Title: {job.get('title', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Job ID: {job.get('_id')}")
            print(f"   Skills: {job.get('skills', 'N/A')}")
            print(f"   Created Date: {job.get('created_date', 'N/A')}")
            if job.get('description'):
                desc = str(job.get('description', ''))
                print(f"\n   Full Description:")
                print(f"   {desc}")
    else:
        print("   No Variance companies found, so no combined matches possible.")
    
    client.close()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    if variance_company_ids:
        print(f"✅ Found {len(variance_companies)} company/companies named 'Variance'")
        if variance_company_ids:
            variance_jobs_count = len(list(jobs_collection.find({'company': {'$in': variance_company_ids}})))
            print(f"✅ Found {variance_jobs_count} total job(s) from Variance")
    else:
        print("❌ No companies found with 'Variance' in name")
    
    if len(product_engineer_jobs) > 0:
        print(f"✅ Found {len(product_engineer_jobs)} job(s) with 'Product Engineer' in title")
    else:
        print("❌ No jobs found with 'Product Engineer' in title")

if __name__ == "__main__":
    search_variance_product_engineer()

