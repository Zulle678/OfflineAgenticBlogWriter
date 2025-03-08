import os
import sys
from pathlib import Path
import json
import logging
from dotenv import load_dotenv, find_dotenv
import yaml

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import local modules
from src.utils.llm_logger import LLMLogger
from src.agent.story_selector import StorySelector
from src.agent.news_scraper import NewsScraper
from src.agent.content_enhancer import ContentEnhancer
from src.agent.blog_writer import BlogWriter
from src.publish.web_publisher import WebPublisher

# Clear existing env vars
os.environ.clear()
# Reload .env file
load_dotenv(find_dotenv(), override=True)

def load_config():
    logger = logging.getLogger(__name__)
    
    # Helper function to safely convert string to boolean
    def str_to_bool(value, default=False):
        if value is None:
            return default
        return value.lower() == 'true'
    
    config = {
        'news_scraper': {
            'language': os.getenv('NEWS_LANGUAGE', 'en'),
            'period': os.getenv('NEWS_PERIOD', '7d'),
            'num_stories': int(os.getenv('NEWS_NUM_STORIES', '10')),
            'source': os.getenv('NEWS_SOURCE', 'newsapi')
        },
        'ollama': {
            'host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            'model': os.getenv('OLLAMA_MODEL', 'llama2'),
            'timeout': int(os.getenv('OLLAMA_TIMEOUT', '300')),
            'num_ctx': int(os.getenv('OLLAMA_NUM_CTX', '4096'))  # Add default if not set
        },
        'blog': {
            'url': os.getenv('BLOG_URL', 'http://localhost'),
            'title_length': int(os.getenv('BLOG_TITLE_LENGTH', '60')),
            'content_length': int(os.getenv('BLOG_CONTENT_LENGTH', '800')),
            'categories': os.getenv('BLOG_CATEGORIES', 'Technology').split(','),
            'min_paragraphs': int(os.getenv('BLOG_MIN_PARAGRAPHS', '3')),
            'max_paragraphs': int(os.getenv('BLOG_MAX_PARAGRAPHS', '10')),
            'keywords_per_post': int(os.getenv('BLOG_KEYWORDS_PER_POST', '5')),
            'include_references': str_to_bool(os.getenv('BLOG_INCLUDE_REFERENCES'), True),
            'enable_markdown': str_to_bool(os.getenv('BLOG_ENABLE_MARKDOWN'), True),
            'code_highlighting': str_to_bool(os.getenv('BLOG_CODE_HIGHLIGHTING'), True)
        }
    }
    
    # Single debug log with complete config
    logger.debug(f"Loaded configuration:\n{json.dumps(config, indent=2)}")
    return config

def main():
    # Configure root logger first
    logging.basicConfig(
        level=logging.INFO,  # This ensures warnings won't show
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Ensure we override any existing configuration
    )
    
    # Then create our specialized logger
    logger = logging.getLogger(__name__)
    llm_logger = LLMLogger()
    
    try:
        config = load_config()
        news_scraper = NewsScraper()
        stories = news_scraper.get_news()
        
        if not stories:
            logger.error("No stories found")
            return
            
        story_selector = StorySelector(
            llm_logger=llm_logger,
            ollama_host=config['ollama']['host'],
            ollama_model=config['ollama']['model'],
            num_ctx=config['ollama']['num_ctx']
        )
        
        selected_story = story_selector.select_story(stories)
        if not selected_story:
            logger.error("Story selection failed")
            return
            
        blog_writer = BlogWriter(
            llm_logger=llm_logger,
            ollama_host=config['ollama']['host'],
            ollama_model=config['ollama']['model'],
            num_ctx=config['ollama']['num_ctx']
        )
        result = blog_writer.generate_blog_post(selected_story)
        
        if not result:
            logger.error("Blog generation failed")
            return
            
        logger.info(f"Blog post created successfully at: {result}")
        
    except Exception as e:
        logger.error(f"Process failed: {e}")

if __name__ == "__main__":
    main()