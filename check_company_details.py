from connect_prod import get_database
from bson import ObjectId
from pprint import pprint

def check_company_details():
    """Check details of the company for the Product Engineer job"""
    db, client = get_database('db')
    
    # Product Engineer job ID
    job_id = ObjectId('690d21b9ad2c58386a769756')
    company_id = ObjectId('6091fc3aaf0cbf002eae7ac1')
    
    # Get the job
    job = db['jobs'].find_one({'_id': job_id})
    print("="*80)
    print("PRODUCT ENGINEER JOB DETAILS")
    print("="*80)
    print(f"Title: {job.get('title', 'N/A')}")
    print(f"Location: {job.get('location', 'N/A')}")
    print(f"Company ID: {job.get('company', 'N/A')}")
    print()
    
    # Get the company
    company = db['companies'].find_one({'_id': company_id})
    print("="*80)
    print("COMPANY DETAILS")
    print("="*80)
    if company:
        print("Full company record:")
        pprint(company)
        print()
        print(f"Company Name: {company.get('employer_name', 'N/A')}")
        print(f"Email: {company.get('email', 'N/A')}")
        print(f"Contact: {company.get('contact_person', 'N/A')}")
        print(f"Website: {company.get('website', 'N/A')}")
    else:
        print("❌ Company not found with that ID")
        print(f"   Searching for company ID: {company_id}")
        
        # Try to find any company with similar characteristics
        print("\nChecking if company ID exists in any format...")
        all_companies = list(db['companies'].find({'_id': company_id}))
        print(f"Found {len(all_companies)} companies with that ID")
    
    # Check job description for company name
    print("\n" + "="*80)
    print("SEARCHING JOB DESCRIPTION FOR COMPANY NAME")
    print("="*80)
    desc = str(job.get('description', '')).lower()
    if 'variance' in desc:
        idx = desc.find('variance')
        print(f"✅ Found 'variance' in description at position {idx}")
        print(f"Context: ...{desc[max(0, idx-150):idx+150]}...")
    else:
        print("❌ No 'variance' found in job description")
    
    # Search all companies for similar names
    print("\n" + "="*80)
    print("SEARCHING ALL COMPANIES FOR VARIATIONS")
    print("="*80)
    
    # Try various search terms
    search_terms = ['variance', 'varian', 'var', 'vari']
    for term in search_terms:
        companies = list(db['companies'].find({
            'employer_name': {'$regex': term, '$options': 'i'}
        }))
        if companies:
            print(f"\nCompanies with '{term}' in name: {len(companies)}")
            for c in companies[:5]:
                print(f"  - {c.get('employer_name', 'N/A')} (ID: {c.get('_id')})")
    
    # Check all jobs from this company
    print("\n" + "="*80)
    print("ALL JOBS FROM THIS COMPANY")
    print("="*80)
    if company_id:
        all_company_jobs = list(db['jobs'].find({'company': company_id}))
        print(f"Found {len(all_company_jobs)} jobs from this company:")
        for j in all_company_jobs:
            print(f"  - {j.get('title', 'N/A')} at {j.get('location', 'N/A')}")
    
    client.close()

if __name__ == "__main__":
    check_company_details()

