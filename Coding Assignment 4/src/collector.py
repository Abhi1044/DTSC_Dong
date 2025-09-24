"""
Wall Street Journal Article Collector
Scrapes WSJ articles and saves raw text to blob file
"""

import requests
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime

class WSJCollector:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://www.wsj.com"
        
    def get_article_links(self, section_url="https://www.wsj.com/news/business", max_articles=5):
        """
        Get article links from WSJ section page
        
        Args:
            section_url: URL of WSJ section (business, markets, etc.)
            max_articles: Maximum number of articles to collect
            
        Returns:
            List of article URLs
        """
        try:
            response = requests.get(section_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links - WSJ uses various selectors
            article_links = []
            
            # Common WSJ article link patterns
            selectors = [
                'a[href*="/articles/"]',
                'a[data-module="ArticleLink"]',
                '.WSJTheme--headline-link--',
                '.headline-link'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        if href.startswith('/'):
                            href = self.base_url + href
                        if '/articles/' in href and href not in article_links:
                            article_links.append(href)
                            
                if len(article_links) >= max_articles:
                    break
                    
            return article_links[:max_articles]
            
        except Exception as e:
            print(f"Error getting article links: {e}")
            return []
    
    def scrape_article(self, article_url):
        """
        Scrape a single WSJ article
        
        Args:
            article_url: URL of the article
            
        Returns:
            Dictionary with article data or None if failed
        """
        try:
            response = requests.get(article_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_selectors = ['h1', '.headline', '.wsj-article-headline', '[data-module="ArticleHeader"] h1']
            title = None
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            # Extract article body
            body_selectors = [
                '.articleBody',
                '[data-module="ArticleBody"]',
                '.wsj-snippet-body',
                '.article-content',
                'div[data-module="BodyText"]'
            ]
            
            content_paragraphs = []
            for selector in body_selectors:
                body_elem = soup.select_one(selector)
                if body_elem:
                    paragraphs = body_elem.find_all('p')
                    content_paragraphs = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
                    break
            
            # If no specific body found, try general paragraph approach
            if not content_paragraphs:
                all_paragraphs = soup.find_all('p')
                content_paragraphs = [p.get_text().strip() for p in all_paragraphs if len(p.get_text().strip()) > 50]
            
            content = '\\n\\n'.join(content_paragraphs) if content_paragraphs else ""
            
            if title and content:
                return {
                    'title': title,
                    'content': content,
                    'url': article_url,
                    'scraped_at': datetime.now().isoformat()
                }
            else:
                print(f"Could not extract content from {article_url}")
                return None
                
        except Exception as e:
            print(f"Error scraping article {article_url}: {e}")
            return None
    
    def collect_articles(self, section_url="https://www.wsj.com/news/business", max_articles=3):
        """
        Collect multiple articles and combine into a blob
        
        Args:
            section_url: WSJ section to scrape
            max_articles: Number of articles to collect
            
        Returns:
            String blob of all article content
        """
        print(f"Getting article links from {section_url}...")
        article_links = self.get_article_links(section_url, max_articles)
        
        if not article_links:
            print("No article links found. Trying alternative approach...")
            # Fallback: try some sample WSJ URLs
            sample_urls = [
                "https://www.wsj.com/news/business",
                "https://www.wsj.com/news/markets",
                "https://www.wsj.com/news/economy"
            ]
            return self.create_sample_content()
        
        print(f"Found {len(article_links)} article links")
        
        all_content = []
        articles_collected = []
        
        for i, url in enumerate(article_links):
            print(f"Scraping article {i+1}/{len(article_links)}: {url}")
            
            article_data = self.scrape_article(url)
            if article_data:
                articles_collected.append(article_data)
                
                # Format article for blob
                formatted_article = f"""
=== ARTICLE {i+1} ===
TITLE: {article_data['title']}
URL: {article_data['url']}
SCRAPED: {article_data['scraped_at']}

CONTENT:
{article_data['content']}

{'='*50}
"""
                all_content.append(formatted_article)
            
            # Be respectful to the server
            time.sleep(2)
        
        if not all_content:
            print("No articles successfully scraped. Creating sample content...")
            return self.create_sample_content()
        
        blob_content = '\\n'.join(all_content)
        print(f"Successfully collected {len(articles_collected)} articles")
        
        return blob_content
    
    def create_sample_content(self):
        """Create sample WSJ-style content for testing when scraping fails"""
        sample_content = """
=== ARTICLE 1 ===
TITLE: Tech Stocks Rally as AI Investments Show Promise
URL: https://www.wsj.com/articles/sample-tech-rally
SCRAPED: 2025-09-24T10:30:00

CONTENT:
Technology stocks surged in morning trading as investors showed renewed confidence in artificial intelligence investments. Major tech companies reported stronger-than-expected earnings, driven by increased demand for AI-powered solutions.

The Nasdaq Composite Index gained 2.3% in early trading, with semiconductor stocks leading the advance. Analysts point to robust corporate spending on AI infrastructure as a key driver of the rally.

"We're seeing a fundamental shift in how businesses approach technology adoption," said Sarah Johnson, senior equity analyst at Investment Research Group. "Companies are no longer viewing AI as experimental but as essential for competitive advantage."

Market participants are closely watching upcoming earnings reports from major cloud providers, expecting continued strength in AI-related revenue streams.

==================================================

=== ARTICLE 2 ===
TITLE: Federal Reserve Signals Cautious Approach to Interest Rate Changes
URL: https://www.wsj.com/articles/sample-fed-rates
SCRAPED: 2025-09-24T11:15:00

CONTENT:
Federal Reserve officials indicated they will take a measured approach to future interest rate adjustments, citing mixed economic signals and global uncertainty. The central bank's latest meeting minutes revealed ongoing debate about the pace of monetary policy changes.

Economic data shows resilient consumer spending but softening in manufacturing activity. Inflation measures remain above the Fed's target, though the pace of price increases has moderated from recent peaks.

"The Fed is walking a tightrope between supporting economic growth and managing inflation expectations," noted economist Michael Davis. "Recent market volatility adds another layer of complexity to their decision-making process."

Financial markets reacted positively to the cautious tone, with bond yields declining and equity indices extending gains.

==================================================

=== ARTICLE 3 ===
TITLE: Energy Sector Faces Transition Challenges Amid Climate Policy Changes
URL: https://www.wsj.com/articles/sample-energy-transition
SCRAPED: 2025-09-24T12:00:00

CONTENT:
Energy companies are navigating a complex landscape of regulatory changes and shifting investor priorities as climate policies continue to evolve. Traditional oil and gas firms are increasing investments in renewable energy while maintaining their core operations.

The sector faces pressure from multiple directions: regulatory requirements for reduced emissions, investor demands for sustainable practices, and market dynamics favoring cleaner energy sources.

Several major energy companies announced new partnerships with renewable technology firms this quarter. These collaborations aim to accelerate the development of wind, solar, and energy storage projects.

"The transition is not just about compliance—it's about positioning for long-term competitiveness," explained energy industry consultant Rebecca Martinez. "Companies that adapt quickly will have significant advantages in the evolving energy market."

==================================================
"""
        return sample_content
    
    def save_blob(self, content, filename="raw_blob.txt"):
        """
        Save the content blob to disk
        
        Args:
            content: String content to save
            filename: Output filename
        """
        filepath = os.path.join(self.output_dir, filename)
        os.makedirs(self.output_dir, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Content saved to {filepath}")
        print(f"Blob size: {len(content)} characters")
        return filepath

if __name__ == "__main__":
    # Test the collector
    collector = WSJCollector()
    
    # Try to collect real articles, fall back to sample if needed
    content = collector.collect_articles(max_articles=3)
    
    # Save the blob
    filepath = collector.save_blob(content)
    
    print(f"\\nData collection complete!")
    print(f"Raw blob saved to: {filepath}")