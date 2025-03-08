import logging
import os
from pathlib import Path
import requests
import feedparser
from typing import List, Dict

class NewsScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_keywords()
        self.news_source = os.getenv('NEWS_SOURCE', 'https://news.google.com')
        self.language = os.getenv('NEWS_LANGUAGE', 'en')
        self.period = os.getenv('NEWS_PERIOD', '7d')
        self.num_stories = int(os.getenv('NEWS_NUM_STORIES', '10'))

    def _load_keywords(self):
        """Load keywords from config file"""
        try:
            keywords_path = Path(__file__).parent.parent.parent / 'config' / 'keywords.txt'
            self.logger.info(f"Loading keywords from: {keywords_path}")
            with open(keywords_path, 'r') as f:
                self.keywords = [line.strip() for line in f if line.strip()]
            self.logger.info(f"Loaded {len(self.keywords)} keywords")
        except Exception as e:
            self.logger.error(f"Failed to load keywords: {str(e)}")
            self.keywords = ['technology', 'AI', 'software']

    def get_news(self, use_custom_keywords: bool = True) -> List[Dict]:
        """
        Fetch news articles using either custom keywords or predefined search terms.
        
        Args:
            use_custom_keywords (bool): If True, uses keywords from config file.
                                      If False, uses predefined tech search terms.
        
        Returns:
            List[Dict]: List of news articles
        """
        self.logger.info(f"Fetching news articles (limit: {self.num_stories})...")
        
        search_terms = (
            self.keywords if use_custom_keywords 
            else ['technology', 'tech', 'AI', 'software', 'digital']
        )
        
        try:
            articles = []
            seen_titles = set()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            for term in search_terms:
                if len(articles) >= self.num_stories:
                    break
                    
                try:
                    response = requests.get(
                        f"{self.news_source}/news/rss/search?q={term}&hl={self.language}",
                        headers=headers
                    )
                    response.raise_for_status()
                    feed = feedparser.parse(response.content)
                    
                    for entry in feed.entries:
                        title = entry.get('title', '')
                        if title in seen_titles:
                            continue
                            
                        desc = entry.get('summary', '')
                        if use_custom_keywords and not (self._contains_keywords(title) or 
                                                      self._contains_keywords(desc)):
                            continue
                            
                        seen_titles.add(title)
                        articles.append({
                            'title': title or 'No Title',
                            'description': desc or 'No Description',
                            'url': entry.get('link', ''),
                            'published_at': entry.get('published', ''),
                            'source': entry.get('source', {}).get('title', 'Unknown')
                        })
                        
                        if len(articles) >= self.num_stories:
                            break
                
                except Exception as e:
                    self.logger.error(f"Failed to fetch news for term '{term}': {str(e)}")
                    continue
            
            self.logger.info(f"Fetched {len(articles)} unique articles")
            return articles[:self.num_stories]
            
        except Exception as e:
            self.logger.error(f"Failed to fetch news: {str(e)}")
            return []

    def _contains_keywords(self, text: str) -> bool:
        """Check if text contains any of our target keywords"""
        if not text:  # Handle None or empty string
            return False
        return any(keyword.lower() in text.lower() for keyword in self.keywords)

    def get_top_stories(self, num_stories: int = None) -> List[Dict]:
        """
        Alternative method to get top stories using direct RSS feeds.
        This is a simplified version of get_news that uses predefined search terms.
        
        Args:
            num_stories (int, optional): Number of stories to return. Defaults to class value.
            
        Returns:
            List[Dict]: List of news stories
        """
        if num_stories is None:
            num_stories = self.num_stories
            
        self.logger.info(f"Fetching top stories (limit: {num_stories})...")
        
        try:
            stories = []
            seen_titles = set()
            
            # Try different search terms to get more relevant stories
            search_terms = ['technology', 'tech', 'AI', 'software', 'digital']
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            for term in search_terms:
                if len(stories) >= num_stories:
                    break
                
                try:
                    url = f"{self.news_source}/news/rss/search?q={term}&hl={self.language}"
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    
                    feed = feedparser.parse(response.content)
                    
                    self.logger.info(f"Retrieved {len(feed.entries)} stories for term '{term}'")
                    
                    for entry in feed.entries:
                        title = entry.get('title', '')
                        
                        # Skip if we've seen this title before
                        if title in seen_titles:
                            continue
                            
                        desc = entry.get('summary', '')
                        
                        if self._contains_keywords(title) or self._contains_keywords(desc):
                            seen_titles.add(title)
                            
                            stories.append({
                                'title': title or 'No Title',
                                'description': desc or 'No Description',
                                'url': entry.get('link', ''),
                                'published_at': entry.get('published', ''),
                                'source': entry.get('source', {}).get('title', 'Unknown')
                            })
                            
                            if len(stories) >= num_stories:
                                break
                
                except Exception as e:
                    self.logger.error(f"Failed to fetch news for term '{term}': {str(e)}")
                    continue

            self.logger.info(f"Found {len(stories)} relevant stories after filtering")
            return stories[:num_stories]  # Ensure we don't exceed the limit

        except Exception as e:
            self.logger.error(f"Error fetching top stories: {str(e)}")
            return []