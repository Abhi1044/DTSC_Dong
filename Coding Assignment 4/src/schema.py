"""
JSON Schema Definition for WSJ Article Analysis
Defines the structure for LLM output with sentiment analysis
"""

# Expected JSON Schema for each article
ARTICLE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "description": "Unique identifier for the article (generated from title hash)"
        },
        "title": {
            "type": "string", 
            "description": "Clean article title"
        },
        "summary": {
            "type": "string",
            "description": "2-3 sentence summary of the article content"
        },
        "sentiment": {
            "type": "string",
            "enum": ["very_positive", "positive", "neutral", "negative", "very_negative"],
            "description": "Overall sentiment of the article"
        },
        "sentiment_score": {
            "type": "number",
            "minimum": -1.0,
            "maximum": 1.0,
            "description": "Numerical sentiment score (-1 to 1, where -1 is very negative, 1 is very positive)"
        },
        "key_topics": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-5 main topics or themes covered in the article"
        },
        "market_impact": {
            "type": "string",
            "enum": ["bullish", "bearish", "neutral", "mixed"],
            "description": "Potential market sentiment impact"
        },
        "source_url": {
            "type": "string",
            "description": "Original article URL"
        },
        "extracted_at": {
            "type": "string",
            "format": "date-time",
            "description": "When the article was processed"
        }
    },
    "required": ["id", "title", "summary", "sentiment", "sentiment_score", "key_topics", "market_impact", "source_url", "extracted_at"]
}

# Example expected output structure
EXAMPLE_OUTPUT = {
    "articles": [
        {
            "id": "tech-rally-ai-investments-2025-09-24",
            "title": "Tech Stocks Rally as AI Investments Show Promise",
            "summary": "Technology stocks surged as investors showed renewed confidence in AI investments. Major tech companies reported stronger earnings driven by AI demand, with the Nasdaq gaining 2.3%.",
            "sentiment": "positive",
            "sentiment_score": 0.7,
            "key_topics": ["artificial intelligence", "tech stocks", "earnings", "nasdaq", "investment"],
            "market_impact": "bullish",
            "source_url": "https://www.wsj.com/articles/sample-tech-rally",
            "extracted_at": "2025-09-24T10:30:00"
        }
    ]
}

# Supabase table schema (SQL)
SUPABASE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS wsj_articles (
    id VARCHAR PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('very_positive', 'positive', 'neutral', 'negative', 'very_negative')),
    sentiment_score DECIMAL(3,2) NOT NULL CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0),
    key_topics TEXT[] NOT NULL,
    market_impact VARCHAR(10) NOT NULL CHECK (market_impact IN ('bullish', 'bearish', 'neutral', 'mixed')),
    source_url TEXT NOT NULL,
    extracted_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for common queries
CREATE INDEX IF NOT EXISTS idx_wsj_articles_sentiment ON wsj_articles(sentiment);
CREATE INDEX IF NOT EXISTS idx_wsj_articles_extracted_at ON wsj_articles(extracted_at);
CREATE INDEX IF NOT EXISTS idx_wsj_articles_market_impact ON wsj_articles(market_impact);
"""