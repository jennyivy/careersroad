from connect_prod import get_database, MONGODB_URI
from pymongo import MongoClient
from job_candidate_matcher import JobCandidateMatcher
from bson import ObjectId
from pprint import pprint

class ProductionJobCandidateMatcher(JobCandidateMatcher):
    """Job-Candidate Matcher for Production Database"""
    
    def __init__(self):
        """Initialize with production database connection"""
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client['db']
        self.jobs_collection = self.db['jobs']
        self.candidates_collection = self.db['candidates']
        self.candidatedatas_collection = self.db['candidatedatas']

def find_top_candidates_for_dqa():
    """Find top 10 candidates for the Data Quality Analyst job in Palo Alto"""
    
    print("="*80)
    print("FINDING TOP 10 CANDIDATES FOR DATA QUALITY ANALYST POSITION")
    print("="*80)
    
    # Initialize matcher with production database
    matcher = ProductionJobCandidateMatcher()
    
    # Data Quality Analyst job ID in Palo Alto
    job_id = ObjectId('690d2287ad2c58386a7697a2')
    
    # Get the job
    job = matcher.jobs_collection.find_one({'_id': job_id})
    if not job:
        print(f"❌ Job not found with ID: {job_id}")
        return
    
    print(f"\n📋 Job Details:")
    print(f"   Title: {job.get('title', 'N/A')}")
    print(f"   Location: {job.get('location', 'N/A')}")
    print(f"   Skills: {job.get('skills', 'N/A')}")
    print(f"   Description: {job.get('description', '')[:200]}...")
    
    # Get company info
    if job.get('company'):
        from connect_prod import get_database
        db, _ = get_database('db')
        company = db['companies'].find_one({'_id': job['company']})
        if company:
            print(f"   Company: {company.get('employer_name', 'N/A')}")
    
    print(f"\n🔍 Searching for matching candidates...")
    print(f"   This may take a moment as we analyze all candidates...\n")
    
    # Get candidates with relevant skills or job roles (more targeted search)
    print("   Step 1: Finding candidates with relevant skills/roles...")
    
    relevant_candidates = list(matcher.candidates_collection.find({
        '$or': [
            {'skills': {'$regex': 'data|sql|quality|analyst|qa|crm|analysis', '$options': 'i'}},
            {'job_role': {'$regex': 'data|analyst|quality|qa', '$options': 'i'}},
            {'is_job_seeking': True}
        ],
        'approval_status': {'$ne': 'rejected'}
    }).limit(2000))  # Limit to 2000 most relevant candidates
    
    print(f"   Found {len(relevant_candidates)} potentially relevant candidates")
    print("   Step 2: Calculating match scores...")
    
    matches = []
    
    for i, candidate in enumerate(relevant_candidates):
        if (i + 1) % 200 == 0:
            print(f"      Processed {i + 1}/{len(relevant_candidates)} candidates... (Found {len(matches)} matches so far)")
        
        # Try to get detailed candidate data
        candidatedata = matcher.candidatedatas_collection.find_one({
            'candidate': candidate['_id']
        })
        
        # Calculate match score
        try:
            match_result = matcher.calculate_match_score(job, candidate, candidatedata)
            
            if match_result['overall_score'] >= 0.05:  # Minimum 5% match
                matches.append({
                    'candidate_id': str(candidate['_id']),
                    'candidate': candidate,
                    'candidatedata': candidatedata,
                    'match_score': match_result['overall_score'],
                    'score_breakdown': match_result['scores']
                })
        except Exception as e:
            # Skip candidates that cause errors
            continue
    
    # Sort by match score (descending)
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Get top 10
    matches = matches[:10]
    
    if not matches:
        print("❌ No matching candidates found.")
        matcher.close()
        return
    
    print("="*80)
    print(f"TOP {len(matches)} MATCHING CANDIDATES")
    print("="*80)
    
    for i, match in enumerate(matches, 1):
        candidate = match['candidate']
        candidatedata = match.get('candidatedata')
        score = match['match_score']
        breakdown = match['score_breakdown']
        
        print(f"\n{'='*80}")
        print(f"#{i} - Match Score: {score:.1%}")
        print(f"{'='*80}")
        
        # Candidate basic info
        first_name = candidate.get('first_name', '')
        last_name = candidate.get('last_name', '')
        name = f"{first_name} {last_name}".strip() or "N/A"
        print(f"👤 Candidate: {name}")
        print(f"   Candidate ID: {match['candidate_id']}")
        print(f"   Email: {candidate.get('email', 'N/A')}")
        print(f"   Location: {candidate.get('city', 'N/A')}")
        
        # Job role and experience
        job_role = candidate.get('job_role') or (candidatedata.get('job_role') if candidatedata else None)
        years_exp = candidate.get('years_of_experience') or (candidatedata.get('years_experience') if candidatedata else None)
        print(f"   Job Role: {job_role or 'N/A'}")
        print(f"   Years of Experience: {years_exp or 'N/A'}")
        
        # Skills
        skills = candidate.get('skills') or (candidatedata.get('skills') if candidatedata else None)
        print(f"   Skills: {skills or 'N/A'}")
        
        # Score breakdown
        print(f"\n   📊 Score Breakdown:")
        print(f"      • Skills Match: {breakdown['skills_match']:.1%}")
        print(f"      • Experience Match: {breakdown['experience_match']:.1%}")
        print(f"      • Job Role Match: {breakdown['job_role_match']:.1%}")
        print(f"      • Text Similarity: {breakdown['text_similarity']:.1%}")
        
        # Additional info if available
        if candidate.get('about'):
            about = candidate.get('about', '')[:150]
            print(f"\n   📝 About: {about}...")
        
        if candidate.get('is_availabletointerview'):
            print(f"   ✅ Available for interview")
        if candidate.get('is_job_seeking'):
            print(f"   🔍 Actively job seeking")
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print("="*80)
    print(f"✅ Found {len(matches)} top matching candidates")
    if matches:
        print(f"📊 Score range: {matches[-1]['match_score']:.1%} - {matches[0]['match_score']:.1%}")
    print(f"\n💡 These candidates are ranked by overall match score, which considers:")
    print(f"   • Skills compatibility (30% weight)")
    print(f"   • Experience level (20% weight)")
    print(f"   • Job role alignment (25% weight)")
    print(f"   • Profile text similarity (25% weight)")
    
    matcher.close()

if __name__ == "__main__":
    find_top_candidates_for_dqa()


