# Job-Candidate Matching System

A comprehensive search and ranking algorithm to match job descriptions with candidate profiles using MongoDB.

## Features

- **Multi-factor Matching**: Combines skills, experience, job role, and text similarity
- **Weighted Scoring**: Configurable weights for different matching factors
- **Bidirectional Search**: Find candidates for jobs OR jobs for candidates
- **Ranked Results**: Results sorted by match score
- **Detailed Score Breakdown**: See why candidates match

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## Matching Algorithm

The system uses a weighted scoring approach with the following factors:

1. **Skills Match (30% weight)**: Compares required job skills with candidate skills
2. **Job Role Match (25% weight)**: Matches job title with candidate's job role
3. **Text Similarity (25% weight)**: Uses TF-IDF and cosine similarity to compare job descriptions with candidate profiles
4. **Experience Match (20% weight)**: Matches candidate experience level with job requirements

### Score Calculation

```
Overall Score = (Skills × 0.30) + (Experience × 0.20) + (Job Role × 0.25) + (Text Similarity × 0.25)
```

## Usage

### Basic Usage

```python
from job_candidate_matcher import JobCandidateMatcher

# Initialize matcher
matcher = JobCandidateMatcher()

# Find candidates for a job
matches = matcher.find_matching_candidates(
    job_id='5e46204dc316f5002e5e661b',
    limit=10,
    min_score=0.3  # Minimum 30% match
)

# Find jobs for a candidate
matches = matcher.search_jobs_for_candidate(
    candidate_id='5db72b98c7ca390017b96404',
    limit=10,
    min_score=0.3
)

# Close connection
matcher.close()
```

### Demo Scripts

1. **Find candidates for a job:**
```bash
python match_demo.py job
```

2. **Find jobs for a candidate:**
```bash
python match_demo.py candidate
```

3. **Interactive mode:**
```bash
python match_demo.py interactive
```

4. **Run both demos:**
```bash
python match_demo.py
```

## Example Output

```
Match #1 - Score: 85.50%
Candidate: John Doe
Job Role: DATA ANALYST
Skills: SQL, Python, Tableau
Years of Experience: 5.0

Score Breakdown:
  - Skills Match: 90.00%
  - Experience Match: 100.00%
  - Job Role Match: 100.00%
  - Text Similarity: 75.00%
```

## Customization

You can customize the matching weights in `job_candidate_matcher.py`:

```python
weights = {
    'skills_match': 0.30,      # Adjust based on importance
    'experience_match': 0.20,
    'job_role_match': 0.25,
    'text_similarity': 0.25
}
```

## Database Collections

- **jobs**: Job postings with title, description, skills, location
- **candidates**: Basic candidate information
- **candidatedatas**: Detailed candidate data with education, employment history

## Files

- `job_candidate_matcher.py`: Main matching algorithm
- `match_demo.py`: Demo and interactive scripts
- `config.py`: MongoDB connection configuration
- `connect.py`: Database connection utilities
- `explore_db.py`: Database exploration tools
- `quick_view.py`: Quick collection viewing

## Notes

- The system filters out rejected candidates and only considers active job seekers
- Minimum score threshold can be adjusted to filter low-quality matches
- Text similarity uses TF-IDF vectorization with n-grams for better matching
- Skills are extracted and normalized for comparison

