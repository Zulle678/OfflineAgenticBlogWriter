from typing import Optional, Dict, List
import logging
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from src.utils.llm_logger import LLMLogger
from .content_enhancer import ContentEnhancer
import requests
from .base_agent import BaseAgent
import json
import re

class BlogWriter(BaseAgent):
    def __init__(self, llm_logger: LLMLogger, ollama_host: str, ollama_model: str, num_ctx: int, **kwargs):
        super().__init__(**kwargs)
        self.llm_logger = llm_logger
        self.logger = logging.getLogger(__name__)
        self.ollama_host = ollama_host
        self.ollama_model = ollama_model
        self.num_ctx = num_ctx
        
        # Use provided logger or create a new one
        self.llm_logger = llm_logger
        
        self.content_enhancer = ContentEnhancer(
            llm_logger=self.llm_logger,
            ollama_host=self.ollama_host,
            ollama_model=self.ollama_model
        )
        
        self.local_blog = os.getenv('LOCAL_BLOG', 'false').lower() == 'true'
        self.local_blog_path = Path(os.getenv('LOCAL_BLOG_PATH', './posts'))
        self.logger.info(f"BlogWriter initialized with model: {self.ollama_model}")
        self.posts_dir = Path(__file__).parent.parent.parent / 'posts'
        self.output_dir = Path(__file__).parent.parent.parent / "output" / "posts"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.system_prompt = """You are a professional blog writer who creates engaging, 
technical content from news articles while maintaining accuracy and readability."""

    def generate_blog_post(self, story: Dict, skip_selection: bool = False) -> Optional[Dict]:
        """
        Generate a blog post from a story.
        
        Args:
            story: Dictionary containing the story data
            skip_selection: If True, assumes story is already selected/enhanced
        """
        try:
            if not skip_selection:
                # self.llm_logger.warning("Story selection should be handled by ContentEnhancer")
                pass
                
            prompt = self._create_blog_prompt(story)
            response = self._call_llm(prompt, system_prompt=self.system_prompt)
            
            if not response:
                self.logger.error("Failed to generate blog content")
                return None

            # Create filename from title and date
            safe_title = re.sub(r'[^\w\s-]', '', story['title'])
            safe_title = re.sub(r'[-\s]+', '-', safe_title).strip('-')
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f"{date_str}-{safe_title[:50]}.md"
            
            filepath = self.output_dir / filename
            
            # Save content to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response)
                
            return str(filepath)
            
        except Exception as e:
            self.llm_logger.error(f"Failed to generate blog post: {str(e)}")
            return None

    def _create_blog_prompt(self, story):
        return f"""Create a technical blog post based on this news story:

Title: {story['title']}
Description: {story['description']}
URL: {story['url']}

Requirements:
1. Write in a professional, technical tone
2. Include specific technical details and explanations
3. Structure with clear headings and paragraphs
4. Add technical insights and analysis
5. Include relevant examples or use cases
6. Maintain accuracy of information
7. End with a References section that includes:
   - The original source URL as: "[Title]({story['url']})"
   - Any additional relevant technical sources

Generate the complete blog post content:"""

    def _get_llm_response(self, prompt: str) -> Optional[str]:
        """Get response from Ollama API with increased context size"""
        try:
            api_url = f"{self.ollama_host.rstrip('/')}/api/generate"
            
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "options": {
                    "num_ctx": self.num_ctx
                }
            }
            
            self.llm_logger.debug(f"Sending request with num_ctx: {self.num_ctx}")
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response")
            
        except Exception as e:
            self.llm_logger.error(f"LLM request failed: {str(e)}")
            return None

    def _get_empty_post(self) -> Dict:
        return {
            'title': 'No Content Available',
            'content': 'Unable to generate content',
            'source_link': '',
            'publication_date': '',
            'source': ''
        }

    def _save_as_typescript(self, post: Dict) -> Dict:
        try:
            post_id = self._get_next_post_id()
            file_path = self.local_blog_path / f'post{post_id}.ts'
            
            try:
                self.local_blog_path.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                self.logger.error(f"Permission error: {e}")
                raise
                
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self._generate_typescript_content(post))
            except IOError as e:
                self.logger.error(f"File write error: {e}")
                raise
                
            return {**post, 'file_path': str(file_path)}
            
        except Exception as e:
            self.logger.error(f"Post save failed: {e}")
            return post

    def _get_next_post_id(self) -> int:
        """Get the next available post ID."""
        existing_posts = list(self.posts_dir.glob('post*.ts'))
        if not existing_posts:
            return 1
        
        # Extract numbers from filenames and find max
        post_nums = [int(p.stem.replace('post', '')) for p in existing_posts]
        return max(post_nums) + 1

    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format."""
        return datetime.now().strftime('%Y-%m-%d')

    def _estimate_read_time(self, content: str) -> int:
        """
        Estimate reading time in minutes based on content length.
        Assumes average reading speed of 200 words per minute.
        """
        word_count = len(content.split())
        minutes = max(1, round(word_count / 200))
        return minutes

    def _determine_category(self, title: str, content: str) -> str:
        categories = os.getenv('BLOG_CATEGORIES', '').split(',')
        return categories[0]  # Default to first category for now

    def write_blog(self, story):
        prompt = self._create_writing_prompt(story)
        response = self._call_llm(prompt)
        if response:
            return self._parse_blog(response)
        return None