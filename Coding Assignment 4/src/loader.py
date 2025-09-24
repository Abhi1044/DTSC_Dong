"""
Loader: Converts JSON to DataFrame and loads into Supabase
Handles the database operations for storing structured article data
"""

import pandas as pd
import json
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env')

class SupabaseLoader:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("Warning: Supabase credentials not found in environment variables")
            print("Please set SUPABASE_URL and SUPABASE_KEY in config/.env")
            self.supabase = None
        else:
            try:
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
                print("Connected to Supabase successfully")
            except Exception as e:
                print(f"Error connecting to Supabase: {e}")
                self.supabase = None
    
    def json_to_dataframe(self, structured_data):
        """
        Convert structured JSON data to pandas DataFrame
        
        Args:
            structured_data: Dict containing articles data
            
        Returns:
            pandas DataFrame
        """
        if not structured_data or 'articles' not in structured_data:
            print("No articles found in structured data")
            return pd.DataFrame()
        
        articles = structured_data['articles']
        
        # Convert to DataFrame
        df = pd.DataFrame(articles)
        
        # Ensure all required columns exist
        required_columns = [
            'id', 'title', 'summary', 'sentiment', 'sentiment_score', 
            'key_topics', 'market_impact', 'source_url', 'extracted_at'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                if col == 'sentiment_score':
                    df[col] = 0.0
                elif col == 'key_topics':
                    df[col] = [['unknown'] for _ in range(len(df))]
                else:
                    df[col] = 'unknown'
        
        # Convert extracted_at to datetime
        df['extracted_at'] = pd.to_datetime(df['extracted_at'])
        
        # Add updated_at timestamp
        df['updated_at'] = datetime.now()
        
        print(f"Created DataFrame with {len(df)} articles")
        return df
    
    def create_table_if_not_exists(self):
        """
        Create the Supabase table if it doesn't exist
        Note: This requires database admin privileges
        """
        if not self.supabase:
            print("No Supabase connection available")
            return False
        
        # The table creation should be done in Supabase dashboard or via SQL editor
        # Here we'll just check if we can query the table
        try:
            result = self.supabase.table('wsj_articles').select('id').limit(1).execute()
            print("Table 'wsj_articles' exists and is accessible")
            return True
        except Exception as e:
            print(f"Table 'wsj_articles' may not exist: {e}")
            print("Please create the table using the SQL in schema.py")
            return False
    
    def upsert_articles(self, df):
        """
        Upsert articles into Supabase table
        
        Args:
            df: pandas DataFrame with article data
            
        Returns:
            Boolean indicating success
        """
        if not self.supabase:
            print("No Supabase connection - saving to local file instead")
            return self.save_to_csv(df)
        
        if df.empty:
            print("No data to upsert")
            return False
        
        try:
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Convert datetime objects to ISO strings for JSON serialization
            for record in records:
                for key, value in record.items():
                    if isinstance(value, pd.Timestamp):
                        record[key] = value.isoformat()
                    elif isinstance(value, datetime):
                        record[key] = value.isoformat()
            
            # Upsert into Supabase
            result = self.supabase.table('wsj_articles').upsert(records).execute()
            
            if result.data:
                print(f"Successfully upserted {len(result.data)} articles")
                return True
            else:
                print("Upsert completed but no data returned")
                return True
                
        except Exception as e:
            print(f"Error upserting to Supabase: {e}")
            print("Falling back to CSV save...")
            return self.save_to_csv(df)
    
    def save_to_csv(self, df, filename="data/articles_backup.csv"):
        """
        Save DataFrame to CSV as backup when Supabase is not available
        
        Args:
            df: pandas DataFrame
            filename: Output CSV filename
        """
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            df.to_csv(filename, index=False)
            print(f"Data saved to CSV backup: {filename}")
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
    
    def query_recent_articles(self, limit=10):
        """
        Query recent articles from Supabase
        
        Args:
            limit: Number of articles to retrieve
            
        Returns:
            List of article dictionaries or None
        """
        if not self.supabase:
            print("No Supabase connection available")
            return None
        
        try:
            result = self.supabase.table('wsj_articles')\
                .select('*')\
                .order('extracted_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
        except Exception as e:
            print(f"Error querying articles: {e}")
            return None
    
    def get_sentiment_summary(self):
        """
        Get sentiment distribution summary
        
        Returns:
            Dict with sentiment counts or None
        """
        if not self.supabase:
            print("No Supabase connection available")
            return None
        
        try:
            # Get all articles and count by sentiment
            result = self.supabase.table('wsj_articles')\
                .select('sentiment')\
                .execute()
            
            if result.data:
                df = pd.DataFrame(result.data)
                sentiment_counts = df['sentiment'].value_counts().to_dict()
                return sentiment_counts
            
            return {}
        except Exception as e:
            print(f"Error getting sentiment summary: {e}")
            return None

def load_from_json_file(json_file="data/structured_articles.json"):
    """
    Load structured data from JSON file
    
    Args:
        json_file: Path to JSON file
        
    Returns:
        Dict with structured data or None
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"JSON file not found: {json_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

if __name__ == "__main__":
    # Test the loader
    loader = SupabaseLoader()
    
    # Load structured data
    structured_data = load_from_json_file()
    
    if structured_data:
        # Convert to DataFrame
        df = loader.json_to_dataframe(structured_data)
        
        if not df.empty:
            print("\\nDataFrame created:")
            print(df[['title', 'sentiment', 'sentiment_score', 'market_impact']].head())
            
            # Check table exists
            if loader.create_table_if_not_exists():
                # Upsert to Supabase
                success = loader.upsert_articles(df)
                
                if success:
                    print("\\nData loading complete!")
                    
                    # Test query
                    recent = loader.query_recent_articles(3)
                    if recent:
                        print(f"Found {len(recent)} recent articles in database")
                else:
                    print("Data loading failed")
            else:
                print("Please set up Supabase table first")
                # Save as backup
                loader.save_to_csv(df)
        else:
            print("No data to load")
    else:
        print("No structured data found. Please run collector.py and structurer.py first.")