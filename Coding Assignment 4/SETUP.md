# WSJ Sentiment Analysis Pipeline - Setup Instructions

## Overview
This pipeline collects Wall Street Journal articles, analyzes sentiment using OpenAI's LLM, stores structured data in Supabase, and displays insights through a Streamlit dashboard deployed on Modal.

## Quick Start

### 1. Install Dependencies
```bash
cd "Coding Assignment 4"
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Edit `config/.env` with your credentials:
```env
# OpenAI API (provided)
OPENAI_ENDPOINT=https://cdong1--azure-proxy-web-app.modal.run
OPENAI_API_KEY=supersecretkey
OPENAI_DEPLOYMENT=gpt-4o

# Supabase (you need to create these)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Modal (for deployment)
MODAL_TOKEN_ID=your_modal_token_id
MODAL_TOKEN_SECRET=your_modal_token_secret
```

### 3. Set Up Supabase Database

1. Create a new Supabase project at https://supabase.com
2. In the SQL Editor, run the table creation script from `src/schema.py`:

```sql
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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_wsj_articles_sentiment ON wsj_articles(sentiment);
CREATE INDEX IF NOT EXISTS idx_wsj_articles_extracted_at ON wsj_articles(extracted_at);
CREATE INDEX IF NOT EXISTS idx_wsj_articles_market_impact ON wsj_articles(market_impact);
```

3. Get your Supabase URL and anon/service key from Project Settings → API

### 4. Run the Pipeline

#### Test Components First:
```bash
python pipeline.py test
```

#### Run Full Pipeline:
```bash
python pipeline.py run 5  # Collect 5 articles
```

#### Run Streamlit Locally:
```bash
streamlit run src/streamlit_app.py
```

## Pipeline Components

### 1. **Collector** (`src/collector.py`)
- Scrapes WSJ business section
- Extracts article titles and content
- Saves raw text blob to `data/raw_blob.txt`
- Falls back to sample content if scraping fails

### 2. **Structurer** (`src/structurer.py`)
- Sends raw text to OpenAI LLM
- Extracts structured JSON with sentiment analysis
- Schema includes: title, summary, sentiment, topics, market impact
- Saves to `data/structured_articles.json`

### 3. **Loader** (`src/loader.py`)
- Converts JSON to pandas DataFrame
- Upserts data to Supabase database
- Falls back to CSV if database unavailable

### 4. **UI** (`src/streamlit_app.py`)
- Interactive dashboard with sentiment visualizations
- Filters by date, sentiment, market impact
- Card and table views for articles
- Real-time data from Supabase

## Modal Deployment

### 1. Install Modal CLI
```bash
pip install modal
modal setup
```

### 2. Create Modal Secrets
```bash
# Create OpenAI secret
modal secret create openai-secret \
  OPENAI_ENDPOINT=https://cdong1--azure-proxy-web-app.modal.run \
  OPENAI_API_KEY=supersecretkey \
  OPENAI_DEPLOYMENT=gpt-4o

# Create Supabase secret  
modal secret create supabase-secret \
  SUPABASE_URL=your_supabase_url \
  SUPABASE_KEY=your_supabase_key
```

### 3. Deploy to Modal
```bash
modal deploy modal_app.py
```

## Troubleshooting

### Common Issues:

1. **Web Scraping Fails**
   - WSJ has anti-bot protection
   - Pipeline falls back to sample content
   - Sample content still demonstrates LLM structuring

2. **LLM API Errors**
   - Check API key in `.env`
   - Verify endpoint is accessible
   - Check rate limits

3. **Supabase Connection Issues**
   - Verify URL and key in `.env`
   - Check table exists with correct schema
   - Pipeline saves to CSV backup if DB fails

4. **Import Errors**
   - Install requirements: `pip install -r requirements.txt`
   - Check Python path includes `src/` directory

### Data Flow Verification:
```bash
# Check each step
ls data/                    # Should have raw_blob.txt
cat data/raw_blob.txt      # Check collected content
ls data/                    # Should have structured_articles.json
python -c "import json; print(len(json.load(open('data/structured_articles.json'))['articles']))"
```

## Project Structure
```
├── src/
│   ├── llm_client.py       # OpenAI client wrapper
│   ├── collector.py        # WSJ web scraper
│   ├── structurer.py       # LLM text → JSON converter
│   ├── loader.py           # JSON → DataFrame → Supabase
│   ├── streamlit_app.py    # UI dashboard
│   └── schema.py           # Data schema definitions
├── data/                   # Generated data files
├── config/
│   └── .env               # Environment variables
├── pipeline.py            # Main orchestrator
├── modal_app.py           # Modal deployment config
├── requirements.txt       # Dependencies
└── README.md
```

## Expected Output

1. **Raw Articles**: 3-5 WSJ articles saved as text blob
2. **Structured Data**: JSON with sentiment analysis for each article
3. **Database**: Articles stored in Supabase with timestamps
4. **Dashboard**: Interactive Streamlit app showing:
   - Sentiment distribution charts
   - Market impact analysis
   - Article cards with summaries
   - Filtering and search capabilities

## Why LLM for This Task?

LLMs excel at this use case because they can:
- **Understand Context**: Financial sentiment isn't just positive/negative words
- **Extract Structure**: Convert messy article text to clean JSON
- **Domain Knowledge**: Understand business/financial implications
- **Consistency**: Apply the same analysis framework across articles
- **Topics Extraction**: Identify key themes without predefined categories

Traditional NLP would struggle with the nuanced financial context and structured output requirements.

## Assignment Deliverables Checklist

- **LLM Client**: OpenAI integration with provided endpoint
- **Collector**: WSJ web scraper with BeautifulSoup  
- **Structurer**: LLM converts text to JSON with sentiment
- **Loader**: JSON to DataFrame to Supabase with upsert
- **UI**: Streamlit dashboard with visualizations
- **Modal Deployment**: Cloud deployment configuration
- **GitHub Ready**: Code without API keys
- **Report**: This documentation explaining the approach