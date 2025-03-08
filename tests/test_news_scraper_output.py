import sys
import os
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.news_scraper import NewsScraper
from dotenv import load_dotenv

def test_news_scraper_output():
    # Load environment variables
    load_dotenv()
    
    # Initialize the scraper
    scraper = NewsScraper()
    
    print("\n=== Testing News Scraper Output ===\n")
    
    # Test get_news with custom keywords
    print("Testing get_news() with custom keywords:")
    print("-" * 50)
    custom_articles = scraper.get_news(use_custom_keywords=True)
    print(f"Retrieved {len(custom_articles)} articles using custom keywords")
    print("\nSample of the data structure (custom keywords):")
    if custom_articles:
        print(json.dumps(custom_articles[0], indent=2))
    
    print("\n" + "=" * 50 + "\n")
    
    # Test get_news with predefined terms
    print("Testing get_news() with predefined terms:")
    print("-" * 50)
    predefined_articles = scraper.get_news(use_custom_keywords=False)
    print(f"Retrieved {len(predefined_articles)} articles using predefined terms")
    print("\nSample of the data structure (predefined terms):")
    if predefined_articles:
        print(json.dumps(predefined_articles[0], indent=2))

if __name__ == "__main__":
    test_news_scraper_output()