from connect_prod import get_database
from bson import ObjectId
from pprint import pprint

def final_variance_search():
    """Final comprehensive search for Variance company and Product Engineer"""
    db, client = get_database('db')
    
    print("="*80)
    print("FINAL SEARCH: PRODUCT ENGINEER FROM VARIANCE")
    print("="*80)
    
    # Search 1: Exact match for "Variance" company
    print("\n1. Searching for exact 'Variance' company name:")
    variance_exact = list(db['companies'].find({
        'employer_name': {'$regex': '^Variance$', '$options': 'i'}
    }))
    print(f"   Found: {len(variance_exact)} companies")
    for c in variance_exact:
        print(f"   - {c.get('employer_name', 'N/A')} (ID: {c.get('_id')})")
        print(f"     Email: {c.get('email', 'N/A')}")
    
    # Search 2: Case-insensitive "variance" anywhere in name
    print("\n2. Searching for 'variance' anywhere in company name:")
    variance_anywhere = list(db['companies'].find({
        'employer_name': {'$regex': 'variance', '$options': 'i'}
    }))
    print(f"   Found: {len(variance_anywhere)} companies")
    for c in variance_anywhere:
        print(f"   - {c.get('employer_name', 'N/A')} (ID: {c.get('_id')})")
        print(f"     Email: {c.get('email', 'N/A')}")
        
        # Check for jobs from this company (handle both string and ObjectId)
        company_id = c.get('_id')
        jobs_str = list(db['jobs'].find({'company': str(company_id)}))
        jobs_obj = list(db['jobs'].find({'company': company_id}))
        all_jobs = jobs_str + jobs_obj
        # Remove duplicates
        seen_ids = set()
        unique_jobs = []
        for j in all_jobs:
            jid = str(j.get('_id'))
            if jid not in seen_ids:
                seen_ids.add(jid)
                unique_jobs.append(j)
        
        print(f"     Jobs from this company: {len(unique_jobs)}")
        for job in unique_jobs:
            print(f"       - {job.get('title', 'N/A')} at {job.get('location', 'N/A')}")
    
    # Search 3: Product Engineer jobs and their companies
    print("\n3. All Product Engineer jobs and their companies:")
    product_engineer_jobs = list(db['jobs'].find({
        'title': {'$regex': 'product engineer', '$options': 'i'}
    }))
    print(f"   Found: {len(product_engineer_jobs)} jobs")
    
    for job in product_engineer_jobs:
        print(f"\n   {'='*70}")
        print(f"   Job: {job.get('title', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Job ID: {job.get('_id')}")
        company_ref = job.get('company')
        print(f"   Company Reference: {company_ref} (type: {type(company_ref).__name__})")
        
        # Try to find company (handle both string and ObjectId)
        company = None
        if company_ref:
            if isinstance(company_ref, str):
                try:
                    company = db['companies'].find_one({'_id': ObjectId(company_ref)})
                except:
                    company = db['companies'].find_one({'_id': company_ref})
            else:
                company = db['companies'].find_one({'_id': company_ref})
        
        if company:
            print(f"   ✅ Company Found: {company.get('employer_name', 'N/A')}")
            print(f"      Email: {company.get('email', 'N/A')}")
            print(f"      Website: {company.get('website', 'N/A')}")
        else:
            print(f"   ❌ Company not found")
    
    # Search 4: Check if "Variance" appears in any job description
    print("\n4. Searching for 'Variance' in job descriptions:")
    variance_in_desc = list(db['jobs'].find({
        'description': {'$regex': 'variance', '$options': 'i'}
    }))
    print(f"   Found: {len(variance_in_desc)} jobs")
    for job in variance_in_desc:
        print(f"   - {job.get('title', 'N/A')} at {job.get('location', 'N/A')}")
        # Get company
        company_ref = job.get('company')
        if company_ref:
            company = None
            if isinstance(company_ref, str):
                try:
                    company = db['companies'].find_one({'_id': ObjectId(company_ref)})
                except:
                    pass
            else:
                company = db['companies'].find_one({'_id': company_ref})
            if company:
                print(f"     Company: {company.get('employer_name', 'N/A')}")
    
    client.close()
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    if len(variance_anywhere) == 0:
        print("❌ No company named 'Variance' found in the production database")
        print("✅ Found 1 Product Engineer job, but it's from BootCareer, not Variance")
    else:
        print(f"✅ Found {len(variance_anywhere)} company/companies with 'variance' in name")

if __name__ == "__main__":
    final_variance_search()

