# Production Database Connection

## Quick Start

To connect to the production MongoDB database:

```bash
python connect_prod.py
```

## Using in Your Code

### Option 1: Use the production connection script directly

```python
from connect_prod import get_database, MONGODB_URI
from pymongo import MongoClient

# Get database connection
db, client = get_database('db')

# Use the database
collection = db['jobs']
jobs = list(collection.find().limit(10))

# Close connection
client.close()
```

### Option 2: Use MongoClient directly

```python
from connect_prod import MONGODB_URI
from pymongo import MongoClient

client = MongoClient(MONGODB_URI)
db = client['db']

# Your code here

client.close()
```

## Production Database Info

- **Cluster**: careerscrossroad-prod.rkx86.mongodb.net
- **Database**: db
- **Collections**: 
  - companies (10,507 documents)
  - users (110,733 documents)
  - jobs (98 documents)
  - candidates (111,936 documents)
  - candidatedatas (32,606 documents)
  - And more...

## Security Note

The production credentials are stored in `connect_prod.py` and `config_prod.py`. These files are excluded from git via `.gitignore` to protect sensitive information.

## Switching Between Staging and Production

- **Staging**: Use `connect.py` (uses `config.py`)
- **Production**: Use `connect_prod.py` (uses production credentials)

