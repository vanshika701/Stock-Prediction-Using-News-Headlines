-- database/schema.sql
-- Database schema for news scraper

-- Table 1: Articles
-- Stores all scraped news articles
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    body TEXT,
    source VARCHAR(200),
    source_api VARCHAR(50),
    source_priority INTEGER DEFAULT 1,
    url TEXT UNIQUE,
    author VARCHAR(200),
    published_at TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ticker VARCHAR(10),
    raw_text TEXT,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(20),
    image TEXT,
    category VARCHAR(50),
    is_duplicate BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index on ticker for fast lookups
CREATE INDEX IF NOT EXISTS idx_articles_ticker ON articles(ticker);

-- Index on published_at for date range queries
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC);

-- Index on source_api to filter by source
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source_api);

-- Index on article_id for duplicate checking
CREATE INDEX IF NOT EXISTS idx_articles_article_id ON articles(article_id);

-- Composite index for ticker + date queries (most common)
CREATE INDEX IF NOT EXISTS idx_articles_ticker_date ON articles(ticker, published_at DESC);


-- Table 2: Stock Tickers Metadata
-- Stores information about stocks we're tracking
CREATE TABLE IF NOT EXISTS stock_tickers (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(200),
    sector VARCHAR(100),
    market_cap BIGINT,
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scraped TIMESTAMP
);

-- Index on ticker
CREATE INDEX IF NOT EXISTS idx_tickers_ticker ON stock_tickers(ticker);

-- Index on priority for prioritizing which stocks to scrape
CREATE INDEX IF NOT EXISTS idx_tickers_priority ON stock_tickers(priority DESC);


-- Table 3: Scraping Logs
-- Tracks all scraping activities for monitoring
CREATE TABLE IF NOT EXISTS scraping_logs (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10),
    source_api VARCHAR(50),
    status VARCHAR(20),
    articles_found INTEGER DEFAULT 0,
    error_message TEXT,
    execution_time FLOAT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index on scraped_at for recent logs
CREATE INDEX IF NOT EXISTS idx_logs_scraped_at ON scraping_logs(scraped_at DESC);

-- Index on status to filter errors
CREATE INDEX IF NOT EXISTS idx_logs_status ON scraping_logs(status);

-- Index on ticker to see logs for specific stock
CREATE INDEX IF NOT EXISTS idx_logs_ticker ON scraping_logs(ticker);


-- Create a view for easy article retrieval with all info
CREATE OR REPLACE VIEW article_summary AS
SELECT 
    a.article_id,
    a.title,
    a.source,
    a.source_api,
    a.ticker,
    a.published_at,
    a.sentiment_score,
    a.sentiment_label,
    a.url,
    st.company_name
FROM articles a
LEFT JOIN stock_tickers st ON a.ticker = st.ticker
ORDER BY a.published_at DESC;


-- Function to check if article exists (by URL or article_id)
CREATE OR REPLACE FUNCTION article_exists(
    p_url TEXT DEFAULT NULL,
    p_article_id VARCHAR(50) DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM articles 
        WHERE url = p_url OR article_id = p_article_id
    );
END;
$$ LANGUAGE plpgsql;


-- Insert some sample tickers
INSERT INTO stock_tickers (ticker, company_name, sector, priority) VALUES
    ('AAPL', 'Apple Inc.', 'Technology', 3),
    ('TSLA', 'Tesla Inc.', 'Automotive', 3),
    ('GOOGL', 'Alphabet Inc.', 'Technology', 3),
    ('MSFT', 'Microsoft Corporation', 'Technology', 3),
    ('AMZN', 'Amazon.com Inc.', 'E-commerce', 3),
    ('NVDA', 'NVIDIA Corporation', 'Technology', 2),
    ('META', 'Meta Platforms Inc.', 'Technology', 2),
    ('NFLX', 'Netflix Inc.', 'Entertainment', 2),
    ('AMD', 'Advanced Micro Devices', 'Technology', 2),
    ('INTC', 'Intel Corporation', 'Technology', 2)
ON CONFLICT (ticker) DO NOTHING;

-- Success message
SELECT 'Database schema created successfully!' AS message;