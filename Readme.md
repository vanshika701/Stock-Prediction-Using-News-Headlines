
# 📰 Stock News Scraper & Analysis System

A comprehensive financial news scraping, processing, and analysis system that collects news from multiple sources, detects stock tickers, processes text using NLP, and provides REST APIs for sentiment analysis and UI integration.

---

## 🎯 Project Overview

This system automatically:
- Scrapes financial news from 4+ sources (NewsAPI, Alpha Vantage, Finnhub, RSS)
- Detects stock tickers mentioned in articles (97 tickers tracked)
- Cleans and preprocesses text using NLP techniques
- Stores data in PostgreSQL with Redis caching
- Provides REST APIs for team integration
- Runs automatically every 15 minutes

---

## 📊 System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    NEWS SCRAPING SYSTEM                      │
└─────────────────────────────────────────────────────────────┘

Data Sources:
├── NewsAPI          → Financial news articles
├── Alpha Vantage    → Market news with sentiment
├── Finnhub          → Company-specific news
└── RSS Feeds        → Yahoo Finance, Reuters, etc.
                ↓
           Unified Scraper
                ↓
        ┌───────────────────┐
        │ Text Preprocessing│
        │  - Clean HTML     │
        │  - Tokenize       │
        │  - Lemmatize      │
        │  - Extract NER    │
        └───────────────────┘
                ↓
        ┌───────────────────┐
        │ Ticker Detection  │
        │  - Find $TICKER   │
        │  - Match companies│
        │  - Extract context│
        └───────────────────┘
                ↓
        ┌───────────────────┐
        │    Storage        │
        │  - PostgreSQL DB  │
        │  - Redis Cache    │
        └───────────────────┘
                ↓
        ┌───────────────────┐
        │    REST APIs      │
        │  - Output API     │
        │  - Input API      │
        └───────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Virtual environment

### Installation
```bash
# 1. Clone repository
cd ~/Desktop/Projects/Stock-Prediction-using-News-Headlines

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Set up database
psql -U postgres -d news_db -f database/schema.sql

# 6. Start Redis
redis-server

# 7. Test the system
python test_integration.py
```

### Running the System

**Option 1: Manual Scrape (One-time)**
```bash
python scrapers/master_scraper.py
```

**Option 2: Automated Scheduler (Continuous)**
```bash
python scheduler/scheduler.py
```

**Option 3: Start APIs for Team**
```bash
# Terminal 1: Output API for Person 2
python api/output_api.py

# Terminal 2: Input API for Person 3
python api/input_api.py
```

---

## 📁 Project Structure
```
Stock-Prediction-using-News-Headlines/
├── api/                           # REST APIs for team integration
│   ├── output_api.py             # API for Person 2 (Sentiment Analysis)
│   └── input_api.py              # API for Person 3 (UI/Frontend)
│
├── scrapers/                      # News source scrapers
│   ├── newsapi_scraper.py        # NewsAPI integration
│   ├── alphavantage_scraper.py   # Alpha Vantage integration
│   ├── finnhub_scraper.py        # Finnhub integration
│   ├── rss_scraper.py            # RSS feed parser
│   └── master_scraper.py         # Unified scraper
│
├── preprocessor/                  # Text preprocessing pipeline
│   ├── text_cleaner.py           # HTML removal, normalization
│   ├── tokenizer.py              # Word/sentence tokenization
│   ├── stop_words.py             # Stop word removal
│   ├── lemmatizer.py             # Lemmatization
│   ├── feature_extractor.py      # NER, keywords, dates
│   └── duplicate_detector.py     # Duplicate detection
│
├── utils/                         # Utility modules
│   ├── ticker_database.py        # Stock ticker database
│   ├── ticker_extractor.py       # Ticker detection algorithm
│   └── context_extractor.py      # Context extraction
│
├── database/                      # Database management
│   ├── db_manager.py             # PostgreSQL operations
│   ├── cache_manager.py          # Redis caching
│   └── schema.sql                # Database schema
│
├── scheduler/                     # Automated scheduling
│   ├── scheduler.py              # Main scheduler
│   ├── error_handler.py          # Error recovery
│   └── rate_limiter.py           # API rate limiting
│
├── config/                        # Configuration
│   └── settings.py               # Settings loader
│
├── logs/                          # Log files
├── .env                          # Environment variables (not in git)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🔑 Environment Variables

Create a `.env` file with:
```bash
# API Keys
NEWSAPI_KEY=your_newsapi_key_here
ALPHAVANTAGE_KEY=your_alphavantage_key_here
FINNHUB_KEY=your_finnhub_key_here

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/news_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Settings
FETCH_INTERVAL=900  # 15 minutes in seconds
```

---

## 📊 System Statistics

- **Total Articles:** 832 unique articles
- **Data Sources:** 4 (NewsAPI, Alpha Vantage, Finnhub, RSS)
- **Stock Tickers:** 97 tracked
- **Deduplication Rate:** 17% (171 duplicates removed)
- **API Response Time:** 6-10ms
- **Processing Speed:** ~1-2 articles/second

---

## 🔗 API Endpoints

### Output API (Port 5000) - For Person 2

**Base URL:** `http://localhost:5000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/articles` | GET | Get all articles |
| `/api/articles/ticker/<ticker>` | GET | Get articles by ticker |
| `/api/articles/recent` | GET | Get recent articles (24h) |
| `/api/stream/latest` | GET | Real-time article stream |
| `/api/export/json` | GET | Export articles as JSON |

### Input API (Port 5001) - For Person 3

**Base URL:** `http://localhost:5001`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/watchlist` | GET/POST | Manage watchlist |
| `/api/priority` | GET/POST | Set ticker priorities |
| `/api/query` | POST | Submit search query |
| `/api/stats` | GET | Get system statistics |

---

## 🧪 Testing
```bash
# Run all tests
python test_integration.py

# Test individual components
python preprocessor/text_cleaner.py
python utils/ticker_extractor.py
python database/db_manager.py

# Test APIs (requires APIs to be running)
curl http://localhost:5000/api/health
curl http://localhost:5001/api/health
```

---

## 📈 Data Flow

1. **Scraping** → News articles collected from 4 sources
2. **Ticker Detection** → Stock symbols identified (97 tickers)
3. **Preprocessing** → Text cleaned, tokenized, lemmatized
4. **Storage** → Saved to PostgreSQL, cached in Redis
5. **API Access** → Available via REST APIs for team

---

## 🛠️ Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

**Common Issues:**

| Issue | Solution |
|-------|----------|
| Database connection failed | Check PostgreSQL is running: `psql -U postgres` |
| Redis connection failed | Start Redis: `redis-server` |
| API key invalid | Verify keys in `.env` file |
| Port already in use | Kill process: `lsof -ti:5000 \| xargs kill -9` |

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👥 Team

- **Vanshika** News Retrieval & Preprocessing
- **Navya** Sentiment Analysis & Investment Recommendations
- **Charvi:** UI/Frontend Development

---
