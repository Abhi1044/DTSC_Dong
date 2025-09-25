"""
Main Pipeline Runner
Orchestrates the entire WSJ sentiment analysis pipeline
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from collector import WSJCollector
from structurer import WSJStructurer
from loader import SupabaseLoader

def run_pipeline(max_articles=3, section_url="https://www.wsj.com/news/business"):
    """
    Run the complete pipeline: Collect → Structure → Load
    
    Args:
        max_articles: Number of articles to collect
        section_url: WSJ section URL to scrape
    """
    print("="*60)
    print("WSJ SENTIMENT ANALYSIS PIPELINE")
    print(f"Started at: {datetime.now()}")
    print("="*60)
    
    # Step 1: Collect articles
    print("\\n1. COLLECTING ARTICLES...")
    collector = WSJCollector()
    
    try:
        raw_blob = collector.collect_articles(
            section_url=section_url, 
            max_articles=max_articles
        )
        
        if raw_blob:
            blob_file = collector.save_blob(raw_blob)
            print(f"Collection complete: {blob_file}")
        else:
            print("Collection failed")
            return False
            
    except Exception as e:
        print(f"Collection error: {e}")
        return False
    
    # Step 2: Structure the data
    print("\\n2. STRUCTURING DATA...")
    structurer = WSJStructurer()
    
    try:
        structured_data = structurer.process_blob(raw_blob)
        
        if structured_data and structured_data.get('articles'):
            json_file = structurer.save_structured_data(structured_data)
            article_count = len(structured_data['articles'])
            print(f"Structuring complete: {article_count} articles processed")
            print(f"   Saved to: {json_file}")
        else:
            print("Structuring failed")
            return False
            
    except Exception as e:
        print(f"Structuring error: {e}")
        return False
    
    # Step 3: Load to database
    print("\\n3. LOADING TO DATABASE...")
    loader = SupabaseLoader()
    
    try:
        # Convert to DataFrame
        df = loader.json_to_dataframe(structured_data)
        
        if not df.empty:
            # Attempt to load to Supabase
            success = loader.upsert_articles(df)
            
            if success:
                print("Loading complete")
                
                # Show summary
                print("\\n" + "="*60)
                print("PIPELINE SUMMARY")
                print("="*60)
                
                print(f"Articles processed: {len(df)}")
                print("\\nSentiment breakdown:")
                sentiment_counts = df.groupby('sentiment').size()
                for sentiment, count in sentiment_counts.items():
                    print(f"  {sentiment}: {count}")
                
                print("\\nMarket impact breakdown:")
                impact_counts = df.groupby('market_impact').size()
                for impact, count in impact_counts.items():
                    print(f"  {impact}: {count}")
                
                print("\\nTop topics:")
                all_topics = []
                for topics in df['key_topics']:
                    if isinstance(topics, list):
                        all_topics.extend(topics)
                
                from collections import Counter
                topic_counts = Counter(all_topics)
                for topic, count in topic_counts.most_common(5):
                    print(f"  {topic}: {count}")
                
                return True
            else:
                print("Loading failed")
                return False
        else:
            print("No data to load")
            return False
            
    except Exception as e:
        print(f"Loading error: {e}")
        return False

def test_components():
    """Test individual components"""
    print("TESTING COMPONENTS...")
    
    # Test LLM Client
    print("\\n1. Testing LLM Client...")
    try:
        from llm_client import LLMClient
        client = LLMClient()
        response = client.test_connection()
        if response:
            print(f"LLM Client working: {response[:50]}...")
        else:
            print("LLM Client failed")
    except Exception as e:
        print(f"LLM Client error: {e}")
    
    # Test Collector
    print("\\n2. Testing Collector...")
    try:
        collector = WSJCollector()
        # Create sample content instead of scraping
        sample_content = collector.create_sample_content()
        if len(sample_content) > 100:
            print("Collector working")
        else:
            print("Collector failed")
    except Exception as e:
        print(f"Collector error: {e}")
    
    # Test Supabase connection
    print("\\n3. Testing Supabase connection...")
    try:
        loader = SupabaseLoader()
        if loader.supabase:
            print("Supabase connected")
        else:
            print("WARNING: Supabase not configured (will use CSV backup)")
    except Exception as e:
        print(f"Supabase error: {e}")

if __name__ == "__main__":
    print("WSJ Sentiment Analysis Pipeline\\n")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_components()
        elif sys.argv[1] == "run":
            max_articles = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            success = run_pipeline(max_articles=max_articles)
            if success:
                print("\\nPipeline completed successfully!")
            else:
                print("\\nPipeline execution failed!")
        else:
            print("Usage: python pipeline.py [test|run] [max_articles]")
    else:
        # Default: run the full pipeline
        success = run_pipeline(max_articles=3)
        if success:
            print("\\nPipeline completed successfully!")
            print("\\nNext steps:")
            print("1. Set up your Supabase database (see schema.py)")
            print("2. Run the Streamlit app: streamlit run src/streamlit_app.py")
            print("3. Deploy on Modal")
        else:
            print("\\nPipeline execution failed!")
            print("\\nTroubleshooting:")
            print("1. Check your .env file has correct API keys")
            print("2. Run 'python pipeline.py test' to test components")
            print("3. Check internet connection for web scraping")