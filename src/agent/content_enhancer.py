# src/agent/content_enhancer.py
from datetime import datetime
from typing import Dict, List, Optional
import json
import requests
from src.utils.llm_logger import LLMLogger
from src.utils.prompt_wrapper import wrap_prompt
from src.agent.story_selector import StorySelector  # Changed to absolute import
from src.agent.blog_generator import BlogGenerator  # Changed to absolute import
from .base_agent import BaseAgent

class ContentEnhancer(BaseAgent):
    def __init__(self, **kwargs):
        # Remove ollama_config parameter and use BaseAgent's initialization
        super().__init__(**kwargs)
        self.system_prompt = """You are a content enhancement specialist.
Your role is to improve and enrich blog post content while maintaining accuracy and readability."""

    def enhance_content(self, content):
        """Enhance the given content with additional details and improvements."""
        prompt = self._create_enhancement_prompt(content)
        response = self._call_llm(prompt, system_prompt=self.system_prompt)
        
        if not response:
            self.logger.error("Failed to enhance content")
            return None
            
        return response

    def _create_enhancement_prompt(self, content):
        return f"""Please enhance this blog post content while maintaining its core message and technical accuracy.
Add relevant details, examples, and improve readability where needed.

Original content:
{content}

Guidelines:
- Maintain technical accuracy
- Improve clarity and flow
- Add relevant examples or context
- Keep the same overall tone
- Preserve any technical terms and concepts"""