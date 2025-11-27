from job_candidate_matcher import JobCandidateMatcher
from pymongo import MongoClient
from config import MONGODB_URI
from pprint import pprint

def demo_find_candidates_for_job():
    """Demo: Find matching candidates for a specific job"""
    print("="*80)
    print("DEMO: Finding Candidates for a Job")
    print("="*80)
    
    matcher = JobCandidateMatcher()
    
    # Get a sample job
    jobs = list(matcher.jobs_collection.find().limit(1))
    if not jobs:
        print("No jobs found in database.")
        return
    
    job = jobs[0]
    print(f"\nJob: {job.get('title', 'N/A')}")
    print(f"Description: {job.get('description', '')[:200]}...")
    print(f"Skills: {job.get('skills', 'N/A')}")
    print(f"\nSearching for matching candidates...\n")
    
    # Find matching candidates
    matches = matcher.find_matching_candidates(
        job['_id'],
        limit=5,
        min_score=0.1  # Minimum 10% match
    )
    
    print(f"Found {len(matches)} matching candidates:\n")
    
    for i, match in enumerate(matches, 1):
        candidate = match['candidate']
        score = match['match_score']
        breakdown = match['score_breakdown']
        
        print(f"{'='*80}")
        print(f"Match #{i} - Score: {score:.2%}")
        print(f"{'='*80}")
        print(f"Candidate ID: {match['candidate_id']}")
        print(f"Name: {candidate.get('first_name', '')} {candidate.get('last_name', '')}")
        print(f"Job Role: {candidate.get('job_role', 'N/A')}")
        print(f"Skills: {candidate.get('skills', 'N/A')}")
        print(f"Years of Experience: {candidate.get('years_of_experience', 'N/A')}")
        print(f"\nScore Breakdown:")
        print(f"  - Skills Match: {breakdown['skills_match']:.2%}")
        print(f"  - Experience Match: {breakdown['experience_match']:.2%}")
        print(f"  - Job Role Match: {breakdown['job_role_match']:.2%}")
        print(f"  - Text Similarity: {breakdown['text_similarity']:.2%}")
        print()
    
    matcher.close()

def demo_find_jobs_for_candidate():
    """Demo: Find matching jobs for a specific candidate"""
    print("="*80)
    print("DEMO: Finding Jobs for a Candidate")
    print("="*80)
    
    matcher = JobCandidateMatcher()
    
    # Get a sample candidate with good data
    candidates = list(matcher.candidates_collection.find({
        'is_job_seeking': True,
        'skills': {'$ne': ''},
        'job_role': {'$ne': ''}
    }).limit(1))
    
    if not candidates:
        print("No suitable candidates found in database.")
        return
    
    candidate = candidates[0]
    print(f"\nCandidate: {candidate.get('first_name', '')} {candidate.get('last_name', '')}")
    print(f"Job Role: {candidate.get('job_role', 'N/A')}")
    print(f"Skills: {candidate.get('skills', 'N/A')}")
    print(f"Years of Experience: {candidate.get('years_of_experience', 'N/A')}")
    print(f"\nSearching for matching jobs...\n")
    
    # Find matching jobs
    matches = matcher.search_jobs_for_candidate(
        candidate['_id'],
        limit=5,
        min_score=0.1  # Minimum 10% match
    )
    
    print(f"Found {len(matches)} matching jobs:\n")
    
    for i, match in enumerate(matches, 1):
        job = match['job']
        score = match['match_score']
        breakdown = match['score_breakdown']
        
        print(f"{'='*80}")
        print(f"Match #{i} - Score: {score:.2%}")
        print(f"{'='*80}")
        print(f"Job ID: {match['job_id']}")
        print(f"Title: {job.get('title', 'N/A')}")
        print(f"Location: {job.get('location', 'N/A')}")
        print(f"Skills: {job.get('skills', 'N/A')}")
        print(f"Description: {job.get('description', '')[:200]}...")
        print(f"\nScore Breakdown:")
        print(f"  - Skills Match: {breakdown['skills_match']:.2%}")
        print(f"  - Experience Match: {breakdown['experience_match']:.2%}")
        print(f"  - Job Role Match: {breakdown['job_role_match']:.2%}")
        print(f"  - Text Similarity: {breakdown['text_similarity']:.2%}")
        print()
    
    matcher.close()

def interactive_search():
    """Interactive search interface"""
    matcher = JobCandidateMatcher()
    
    print("="*80)
    print("Interactive Job-Candidate Matching")
    print("="*80)
    print("\nOptions:")
    print("1. Find candidates for a job")
    print("2. Find jobs for a candidate")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            # List available jobs
            jobs = list(matcher.jobs_collection.find({}, {'title': 1, '_id': 1}).limit(10))
            print("\nAvailable Jobs:")
            for i, job in enumerate(jobs, 1):
                print(f"{i}. {job.get('title', 'N/A')} (ID: {job['_id']})")
            
            job_choice = input("\nEnter job number or job ID: ").strip()
            try:
                if job_choice.isdigit():
                    job_id = jobs[int(job_choice) - 1]['_id']
                else:
                    from bson import ObjectId
                    job_id = ObjectId(job_choice)
                
                limit = input("How many candidates to show? (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                
                matches = matcher.find_matching_candidates(job_id, limit=limit)
                
                print(f"\nFound {len(matches)} matching candidates:\n")
                for i, match in enumerate(matches, 1):
                    candidate = match['candidate']
                    print(f"{i}. {candidate.get('first_name', '')} {candidate.get('last_name', '')} "
                          f"- Score: {match['match_score']:.2%} "
                          f"(Role: {candidate.get('job_role', 'N/A')})")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '2':
            # List available candidates
            candidates = list(matcher.candidates_collection.find(
                {'is_job_seeking': True},
                {'first_name': 1, 'last_name': 1, 'job_role': 1, '_id': 1}
            ).limit(10))
            
            print("\nAvailable Candidates:")
            for i, candidate in enumerate(candidates, 1):
                name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}"
                role = candidate.get('job_role', 'N/A')
                print(f"{i}. {name} - {role} (ID: {candidate['_id']})")
            
            candidate_choice = input("\nEnter candidate number or candidate ID: ").strip()
            try:
                if candidate_choice.isdigit():
                    candidate_id = candidates[int(candidate_choice) - 1]['_id']
                else:
                    from bson import ObjectId
                    candidate_id = ObjectId(candidate_choice)
                
                limit = input("How many jobs to show? (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                
                matches = matcher.search_jobs_for_candidate(candidate_id, limit=limit)
                
                print(f"\nFound {len(matches)} matching jobs:\n")
                for i, match in enumerate(matches, 1):
                    job = match['job']
                    print(f"{i}. {job.get('title', 'N/A')} "
                          f"- Score: {match['match_score']:.2%} "
                          f"(Location: {job.get('location', 'N/A')})")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    matcher.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == 'job':
            demo_find_candidates_for_job()
        elif mode == 'candidate':
            demo_find_jobs_for_candidate()
        elif mode == 'interactive':
            interactive_search()
        else:
            print("Usage: python match_demo.py [job|candidate|interactive]")
    else:
        # Run both demos
        demo_find_candidates_for_job()
        print("\n\n")
        demo_find_jobs_for_candidate()

