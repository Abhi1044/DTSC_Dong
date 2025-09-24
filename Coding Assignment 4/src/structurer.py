"""
Structurer: Converts raw text blob to structured JSON using LLM
Uses OpenAI to analyze WSJ articles and extract structured data with sentiment
"""

import json
import hashlib
from datetime import datetime
from llm_client import LLMClient
from schema import ARTICLE_SCHEMA, EXAMPLE_OUTPUT

class WSJStructurer:
    def __init__(self):
        self.llm_client = LLMClient()
        
    def create_analysis_prompt(self, raw_text_blob):
        """
        Create a prompt for the LLM to analyze the text blob
        
        Args:
            raw_text_blob: Raw text containing multiple articles
            
        Returns:
            List of messages for the LLM
        """
        
        system_prompt = """You are a financial news analyst specializing in Wall Street Journal articles. Your task is to analyze news articles and extract structured information with sentiment analysis.

INSTRUCTIONS:
1. Parse each article from the provided text blob
2. For each article, extract the required information according to the JSON schema
3. Analyze sentiment from a financial/market perspective
4. Identify key topics and market impact
5. Return ONLY valid JSON - no additional text or formatting

SENTIMENT GUIDELINES:
- very_positive (0.7 to 1.0): Exceptionally bullish news, major positive developments
- positive (0.3 to 0.7): Generally good news, positive market indicators
- neutral (-0.3 to 0.3): Balanced reporting, mixed signals, factual updates
- negative (-0.7 to -0.3): Concerning developments, bearish indicators
- very_negative (-1.0 to -0.7): Major negative events, market crashes, severe problems

MARKET IMPACT:
- bullish: Likely to drive markets/stocks higher
- bearish: Likely to drive markets/stocks lower  
- neutral: Minimal expected market impact
- mixed: Could have both positive and negative effects

REQUIRED JSON STRUCTURE:
{
    "articles": [
        {
            "id": "generated-unique-id",
            "title": "Clean article title",
            "summary": "2-3 sentence summary focusing on key financial/business points",
            "sentiment": "positive|negative|neutral|very_positive|very_negative",
            "sentiment_score": 0.5,
            "key_topics": ["topic1", "topic2", "topic3"],
            "market_impact": "bullish|bearish|neutral|mixed",
            "source_url": "original URL from text",
            "extracted_at": "2025-09-24T12:00:00"
        }
    ]
}"""

        user_prompt = f"""Analyze the following Wall Street Journal articles and return structured JSON:

{raw_text_blob}

Remember: Return ONLY the JSON structure, no additional text."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def generate_article_id(self, title, url):
        """Generate a unique ID for an article based on title and URL"""
        content = f"{title}_{url}".encode('utf-8')
        return hashlib.md5(content).hexdigest()[:16]
    
    def process_blob(self, raw_text_blob):
        """
        Process the raw text blob and return structured JSON
        
        Args:
            raw_text_blob: String containing raw article text
            
        Returns:
            Dict containing structured article data or None if failed
        """
        try:
            # Create the prompt
            messages = self.create_analysis_prompt(raw_text_blob)
            
            # Get LLM response
            print("Sending text to LLM for analysis...")
            response = self.llm_client.generate_completion(
                messages=messages,
                max_tokens=3000,
                temperature=0.2  # Low temperature for consistent structured output
            )
            
            if not response:
                print("No response from LLM")
                return None
            
            print("Received response from LLM")
            
            # Try to parse the JSON response
            try:
                # Clean the response - remove any markdown formatting
                cleaned_response = response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                structured_data = json.loads(cleaned_response)
                
                # Validate and enhance the data
                if 'articles' in structured_data:
                    for article in structured_data['articles']:
                        # Generate ID if not present or invalid
                        if not article.get('id') or len(article['id']) < 5:
                            article['id'] = self.generate_article_id(
                                article.get('title', ''), 
                                article.get('source_url', '')
                            )
                        
                        # Ensure extracted_at is present
                        if not article.get('extracted_at'):
                            article['extracted_at'] = datetime.now().isoformat()
                
                print(f"Successfully structured {len(structured_data.get('articles', []))} articles")
                return structured_data
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Response was: {response[:500]}...")
                
                # Try to create a fallback structure
                return self.create_fallback_structure(raw_text_blob)
        
        except Exception as e:
            print(f"Error processing blob: {e}")
            return self.create_fallback_structure(raw_text_blob)
    
    def create_fallback_structure(self, raw_text_blob):
        """
        Create a basic structure if LLM processing fails
        
        Args:
            raw_text_blob: Raw text blob
            
        Returns:
            Basic structured data
        """
        print("Creating fallback structure...")
        
        # Try to extract basic info from the blob
        articles = []
        sections = raw_text_blob.split('=== ARTICLE')
        
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            try:
                lines = section.strip().split('\\n')
                title = "Unknown Article"
                url = "unknown"
                
                # Extract title and URL
                for line in lines[:10]:  # Check first 10 lines
                    if line.startswith('TITLE:'):
                        title = line.replace('TITLE:', '').strip()
                    elif line.startswith('URL:'):
                        url = line.replace('URL:', '').strip()
                
                # Create basic article structure
                article = {
                    "id": self.generate_article_id(title, url),
                    "title": title,
                    "summary": f"Article summary not available - LLM processing failed for: {title}",
                    "sentiment": "neutral",
                    "sentiment_score": 0.0,
                    "key_topics": ["news", "finance"],
                    "market_impact": "neutral",
                    "source_url": url,
                    "extracted_at": datetime.now().isoformat()
                }
                
                articles.append(article)
                
            except Exception as e:
                print(f"Error creating fallback for section {i}: {e}")
                continue
        
        return {"articles": articles}
    
    def save_structured_data(self, structured_data, output_file="data/structured_articles.json"):
        """
        Save structured data to JSON file
        
        Args:
            structured_data: Dict containing article data
            output_file: Path to save the JSON file
        """
        import os
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"Structured data saved to {output_file}")
        return output_file

if __name__ == "__main__":
    # Test the structurer
    structurer = WSJStructurer()
    
    # Load the raw blob
    try:
        with open('data/raw_blob.txt', 'r', encoding='utf-8') as f:
            raw_blob = f.read()
        
        print("Processing raw blob...")
        structured_data = structurer.process_blob(raw_blob)
        
        if structured_data:
            # Save structured data
            output_file = structurer.save_structured_data(structured_data)
            
            # Print summary
            articles = structured_data.get('articles', [])
            print(f"\\nStructuring complete!")
            print(f"Processed {len(articles)} articles")
            
            for article in articles[:2]:  # Show first 2 articles
                print(f"\\n- {article['title']}")
                print(f"  Sentiment: {article['sentiment']} ({article['sentiment_score']})")
                print(f"  Topics: {', '.join(article['key_topics'])}")
                print(f"  Market Impact: {article['market_impact']}")
        else:
            print("Failed to structure the data")
            
    except FileNotFoundError:
        print("Raw blob file not found. Please run collector.py first.")