import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
ALPHAVANTAGE_KEY = os.getenv('ALPHAVANTAGE_KEY')
FINNHUB_KEY = os.getenv('FINNHUB_KEY')

# Database
DATABASE_URL = os.getenv('DATABASE_URL')

# Redis
REDIS_URL = os.getenv('REDIS_URL')

# Settings
FETCH_INTERVAL = 900  # 15 minutes in seconds
MAX_ARTICLES_PER_FETCH = 100