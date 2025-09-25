# WSJ Sentiment Analysis Pipeline

## Assignment Overview

This project implements a complete data pipeline that:
1. **Collects** Wall Street Journal articles via web scraping
2. **Structures** raw text using OpenAI LLM for sentiment analysis  
3. **Loads** structured data into databases (Supabase/CSV)
4. **Visualizes** insights through interactive Streamlit dashboard
5. **Deploys** on Modal cloud platform

## Quick Start Guide

### Installation and Execution
```bash
pip install -r requirements.txt
python3 pipeline.py run 3        # Collect 3 articles
streamlit run src/streamlit_app.py  # View dashboard
```

### Dashboard Access
- **Local Development**: http://localhost:8501
- **Cloud Deployment**: Available via Modal deployment

## Expected Outputs

### Generated Data Files:
- **Raw Articles**: Text blob saved to `data/raw_blob.txt`
- **Structured JSON**: Sentiment analysis in `data/structured_articles.json`
- **Database Backup**: CSV file in `data/articles_backup.csv`

### Dashboard Functionality:
- **Sentiment Distribution Charts**: Visual breakdown of article sentiment
- **Market Impact Analysis**: Categorization as bullish/bearish/neutral/mixed
- **Timeline Visualization**: Sentiment trends over time
- **Interactive Filtering**: Date range, sentiment type, and topic filters
- **Article Display**: Individual cards with summaries and sentiment scores

## LLM Integration Analysis

### Rationale for LLM Implementation:

**Limitations of Traditional NLP Approaches:**
- Insufficient understanding of financial context versus general sentiment
- Inability to convert unstructured text to consistent structured output
- Limited domain knowledge for nuanced market implications
- Requires predefined categories for topic extraction

**LLM Advantages Demonstrated:**
- Analysis of sentiment from financial and market perspective
- Consistent structuring of articles into standardized JSON schema
- Understanding of business terminology and market relationships
- Generation of numerical sentiment scores with contextual reasoning

### Sample LLM Output:
**Raw Input**: "Tech stocks surged as AI investments showed promise..."

**LLM Output**:
```json
{
  "sentiment": "very_positive",
  "sentiment_score": 0.8,
  "market_impact": "bullish",
  "key_topics": ["AI investments", "tech earnings", "Nasdaq rally"],
  "summary": "Technology stocks rose on strong AI investment news..."
}
```

## Technical Architecture

### Component Breakdown:
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Collector** | `requests` + `BeautifulSoup` | Scrape WSJ articles |
| **Structurer** | `OpenAI GPT-4` | Raw text → JSON sentiment |
| **Loader** | `pandas` + `Supabase` | Store structured data |
| **Dashboard** | `Streamlit` + `Plotly` | Interactive visualizations |
| **Deployment** | `Modal` | Cloud hosting |

### Data Schema:
```json
{
  "id": "unique-identifier",
  "title": "Article headline",
  "summary": "Business-focused 2-3 sentences", 
  "sentiment": "very_positive|positive|neutral|negative|very_negative",
  "sentiment_score": 0.7,
  "key_topics": ["topic1", "topic2"],
  "market_impact": "bullish|bearish|neutral|mixed",
  "source_url": "original URL",
  "extracted_at": "2025-09-24T12:00:00"
}
```

## Implementation Features

### Error Handling and Reliability:
- **Web scraping fallback**: Sample content when WSJ access is restricted
- **API resilience**: Graceful degradation with alternative processing methods
- **Database backup**: CSV file generation when primary database is unavailable
- **Data validation**: Schema validation for LLM-generated outputs

### System Design Considerations:
- **Modular architecture**: Independent component scaling capability
- **Cloud deployment**: Concurrent user support via Modal platform
- **Performance optimization**: Streamlit caching for database operations
- **Security practices**: Environment-based credential management

## Results Achieved

### Sample Pipeline Run:
```
Articles processed: 3
Sentiment breakdown:
  very_positive: 1 (AI/tech rally)
  positive: 1 (Fed policy)
  neutral: 1 (energy transition)

Market impact:
  bullish: 2 articles
  mixed: 1 article

Top topics: AI investments, Federal Reserve, tech earnings
```

### Business Value:
- **Automation**: Replace hours of manual sentiment analysis
- **Consistency**: Standardized scoring across all articles
- **Insights**: Interactive visualizations reveal market patterns
- **Speed**: Real-time processing vs. manual analysis
- **Scalability**: Cloud deployment supports organization-wide use

## Deployment Instructions

### For Modal Deployment:
1. **Install Modal**: `pip install modal`
2. **Setup**: `modal setup` (requires Modal account)
3. **Create secrets** for OpenAI and Supabase credentials
4. **Deploy**: `modal deploy modal_app.py`

### For Local Development:
```bash
# Test everything works
python3 pipeline.py test

# Run full pipeline  
python3 pipeline.py run 5

# Launch dashboard
streamlit run src/streamlit_app.py
```

## Assignment Deliverables

### Core Components Implemented:
- **LLM Client**: OpenAI integration using provided endpoint configuration
- **Collector**: Web scraper implementation using requests and BeautifulSoup libraries
- **Structurer**: LLM-based conversion of unstructured text to structured JSON format
- **Loader**: Data pipeline from JSON to DataFrame to Supabase database with upsert functionality
- **User Interface**: Streamlit dashboard with interactive data visualizations
- **Cloud Deployment**: Modal platform deployment configuration
- **Documentation**: Complete technical documentation and setup instructions

### Repository Contents:
- Complete source code with modular architecture
- Sample data outputs and processing results  
- Environment configuration templates
- Comprehensive documentation

## Technical Learning Outcomes

This implementation demonstrates:
1. **Large Language Model Integration**: Practical application of LLMs for domain-specific text analysis
2. **Data Pipeline Architecture**: End-to-end ETL process with comprehensive error handling
3. **Web Scraping and Data Collection**: Automated data acquisition with fallback mechanisms
4. **Interactive Data Visualization**: Development of user-facing analytical dashboards
5. **Cloud Platform Integration**: Deployment strategies for scalable data science applications

## Repository Information

- **Source Code Repository**: Complete implementation available on GitHub
- **Cloud Deployment**: Configuration provided for Modal platform deployment
- **Technical Documentation**: Detailed analysis available in PROJECT_REPORT.md

## Conclusion

This pipeline demonstrates the application of modern natural language processing techniques to financial text analysis, providing a framework for automated sentiment analysis of financial news content.