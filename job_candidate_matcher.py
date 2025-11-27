from pymongo import MongoClient
from config import MONGODB_URI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Dict, Tuple
import numpy as np

class JobCandidateMatcher:
    """
    A comprehensive job-candidate matching and ranking system
    """
    
    def __init__(self, db_name='db'):
        """Initialize the matcher with database connection"""
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[db_name]
        self.jobs_collection = self.db['jobs']
        self.candidates_collection = self.db['candidates']
        self.candidatedatas_collection = self.db['candidatedatas']
        
    def normalize_text(self, text: str) -> str:
        """Normalize text for processing"""
        if not text:
            return ""
        # Convert to lowercase and remove extra whitespace
        text = str(text).lower().strip()
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def extract_skills(self, skills_text: str) -> List[str]:
        """Extract skills from a comma-separated or space-separated string"""
        if not skills_text:
            return []
        
        # Split by comma, semicolon, or space
        skills = re.split(r'[,;]|\s+', str(skills_text))
        # Clean and filter
        skills = [self.normalize_text(skill) for skill in skills if skill.strip()]
        return skills
    
    def calculate_skills_match(self, job_skills: List[str], candidate_skills: List[str]) -> float:
        """Calculate skills matching score (0-1)"""
        if not job_skills or not candidate_skills:
            return 0.0
        
        job_skills_set = set(job_skills)
        candidate_skills_set = set(candidate_skills)
        
        if not job_skills_set:
            return 0.0
        
        # Calculate intersection
        matched_skills = job_skills_set.intersection(candidate_skills_set)
        
        # Score based on matched skills / required skills
        match_score = len(matched_skills) / len(job_skills_set)
        
        # Bonus for having additional relevant skills
        if len(candidate_skills_set) > len(job_skills_set):
            bonus = min(0.1, len(candidate_skills_set - job_skills_set) * 0.01)
            match_score = min(1.0, match_score + bonus)
        
        return match_score
    
    def calculate_experience_match(self, job_description: str, candidate_years: float) -> float:
        """Calculate experience level matching score"""
        if candidate_years is None or candidate_years < 0:
            return 0.0
        
        # Extract experience requirements from job description
        desc_lower = self.normalize_text(job_description)
        
        # Look for experience keywords
        if any(word in desc_lower for word in ['entry level', 'junior', '0-2', '0 to 2']):
            required_years = 1.0
        elif any(word in desc_lower for word in ['senior', 'lead', '10+', '10 or more']):
            required_years = 10.0
        elif any(word in desc_lower for word in ['5+', '5 or more', '5 years']):
            required_years = 5.0
        elif any(word in desc_lower for word in ['3+', '3 or more', '3 years']):
            required_years = 3.0
        else:
            # Default: assume mid-level (3-5 years)
            required_years = 3.0
        
        # Calculate match score
        if candidate_years >= required_years:
            return 1.0
        elif candidate_years >= required_years * 0.7:
            return 0.7
        elif candidate_years >= required_years * 0.5:
            return 0.5
        else:
            return max(0.0, candidate_years / required_years)
    
    def calculate_text_similarity(self, job_text: str, candidate_text: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""
        if not job_text or not candidate_text:
            return 0.0
        
        # Combine texts for vectorization
        texts = [self.normalize_text(job_text), self.normalize_text(candidate_text)]
        
        # Use TF-IDF vectorizer
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def calculate_job_role_match(self, job_title: str, candidate_job_role: str) -> float:
        """Calculate job role/title matching score"""
        if not job_title or not candidate_job_role:
            return 0.0
        
        job_title_norm = self.normalize_text(job_title)
        candidate_role_norm = self.normalize_text(candidate_job_role)
        
        # Exact match
        if job_title_norm == candidate_role_norm:
            return 1.0
        
        # Check if job title contains candidate role or vice versa
        if candidate_role_norm in job_title_norm or job_title_norm in candidate_role_norm:
            return 0.8
        
        # Check for keyword overlap
        job_keywords = set(job_title_norm.split())
        candidate_keywords = set(candidate_role_norm.split())
        
        if job_keywords and candidate_keywords:
            overlap = len(job_keywords.intersection(candidate_keywords))
            total_unique = len(job_keywords.union(candidate_keywords))
            if total_unique > 0:
                return overlap / total_unique
        
        return 0.0
    
    def build_candidate_profile_text(self, candidate: Dict, candidatedata: Dict = None) -> str:
        """Build a comprehensive text profile from candidate data"""
        profile_parts = []
        
        # From candidates collection
        if candidate.get('about'):
            profile_parts.append(candidate.get('about', ''))
        if candidate.get('skills'):
            profile_parts.append(candidate.get('skills', ''))
        if candidate.get('job_role'):
            profile_parts.append(candidate.get('job_role', ''))
        if candidate.get('biggest_achievement'):
            profile_parts.append(candidate.get('biggest_achievement', ''))
        if candidate.get('job_expectations'):
            profile_parts.append(candidate.get('job_expectations', ''))
        
        # From candidatedatas collection (more detailed)
        if candidatedata:
            if candidatedata.get('skills'):
                profile_parts.append(candidatedata.get('skills', ''))
            if candidatedata.get('job_role'):
                profile_parts.append(candidatedata.get('job_role', ''))
            
            # Add education summaries
            if candidatedata.get('education'):
                for edu in candidatedata.get('education', []):
                    if isinstance(edu, dict):
                        if edu.get('summary'):
                            profile_parts.append(edu.get('summary', ''))
                        if edu.get('major'):
                            profile_parts.append(edu.get('major', ''))
            
            # Add employment summaries
            if candidatedata.get('employment'):
                for emp in candidatedata.get('employment', []):
                    if isinstance(emp, dict):
                        if emp.get('summary'):
                            profile_parts.append(emp.get('summary', ''))
                        if emp.get('job_title'):
                            profile_parts.append(emp.get('job_title', ''))
        
        return ' '.join(profile_parts)
    
    def calculate_match_score(self, job: Dict, candidate: Dict, candidatedata: Dict = None) -> Dict:
        """Calculate comprehensive match score for a job-candidate pair"""
        
        # Extract job information
        job_title = job.get('title', '')
        job_description = job.get('description', '')
        job_skills_text = job.get('skills', '')
        job_skills = self.extract_skills(job_skills_text)
        
        # Extract candidate information
        candidate_skills_text = candidate.get('skills', '') or (candidatedata.get('skills', '') if candidatedata else '')
        candidate_skills = self.extract_skills(candidate_skills_text)
        candidate_years = candidate.get('years_of_experience') or (candidatedata.get('years_experience') if candidatedata else 0)
        candidate_job_role = candidate.get('job_role', '') or (candidatedata.get('job_role', '') if candidatedata else '')
        
        # Build candidate profile text
        candidate_profile_text = self.build_candidate_profile_text(candidate, candidatedata)
        
        # Calculate individual scores
        scores = {
            'skills_match': self.calculate_skills_match(job_skills, candidate_skills),
            'experience_match': self.calculate_experience_match(job_description, candidate_years),
            'job_role_match': self.calculate_job_role_match(job_title, candidate_job_role),
            'text_similarity': self.calculate_text_similarity(
                f"{job_title} {job_description}",
                candidate_profile_text
            )
        }
        
        # Weighted overall score
        weights = {
            'skills_match': 0.30,
            'experience_match': 0.20,
            'job_role_match': 0.25,
            'text_similarity': 0.25
        }
        
        overall_score = sum(scores[key] * weights[key] for key in scores)
        
        return {
            'overall_score': overall_score,
            'scores': scores,
            'weights': weights
        }
    
    def find_matching_candidates(self, job_id: str, limit: int = 10, min_score: float = 0.0) -> List[Dict]:
        """
        Find and rank candidates for a specific job
        
        Args:
            job_id: MongoDB ObjectId string or ObjectId of the job
            limit: Maximum number of candidates to return
            min_score: Minimum match score threshold
        
        Returns:
            List of candidate matches with scores, sorted by match score
        """
        from bson import ObjectId
        
        # Get job
        if isinstance(job_id, str):
            job_id = ObjectId(job_id)
        
        job = self.jobs_collection.find_one({'_id': job_id})
        if not job:
            return []
        
        # Get all candidates (you might want to add filters here)
        candidates = list(self.candidates_collection.find({
            'is_job_seeking': True,  # Only active job seekers
            'approval_status': {'$ne': 'rejected'}  # Exclude rejected candidates
        }))
        
        matches = []
        
        for candidate in candidates:
            # Try to get detailed candidate data
            candidatedata = self.candidatedatas_collection.find_one({
                'candidate': candidate['_id']
            })
            
            # Calculate match score
            match_result = self.calculate_match_score(job, candidate, candidatedata)
            
            if match_result['overall_score'] >= min_score:
                matches.append({
                    'candidate_id': str(candidate['_id']),
                    'candidate': candidate,
                    'candidatedata': candidatedata,
                    'match_score': match_result['overall_score'],
                    'score_breakdown': match_result['scores']
                })
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matches[:limit]
    
    def search_jobs_for_candidate(self, candidate_id: str, limit: int = 10, min_score: float = 0.0) -> List[Dict]:
        """
        Find and rank jobs for a specific candidate
        
        Args:
            candidate_id: MongoDB ObjectId string or ObjectId of the candidate
            limit: Maximum number of jobs to return
            min_score: Minimum match score threshold
        
        Returns:
            List of job matches with scores, sorted by match score
        """
        from bson import ObjectId
        
        # Get candidate
        if isinstance(candidate_id, str):
            candidate_id = ObjectId(candidate_id)
        
        candidate = self.candidates_collection.find_one({'_id': candidate_id})
        if not candidate:
            return []
        
        # Get detailed candidate data
        candidatedata = self.candidatedatas_collection.find_one({
            'candidate': candidate_id
        })
        
        # Get all jobs
        jobs = list(self.jobs_collection.find({}))
        
        matches = []
        
        for job in jobs:
            # Calculate match score
            match_result = self.calculate_match_score(job, candidate, candidatedata)
            
            if match_result['overall_score'] >= min_score:
                matches.append({
                    'job_id': str(job['_id']),
                    'job': job,
                    'match_score': match_result['overall_score'],
                    'score_breakdown': match_result['scores']
                })
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matches[:limit]
    
    def close(self):
        """Close database connection"""
        self.client.close()

