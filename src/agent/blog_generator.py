import requests
import json
from datetime import datetime
from typing import Dict, Optional
from src.prompts.generation_prompt import build_generation_prompt  # Changed to absolute import
from src.utils.llm_logger import LLMLogger
from src.utils.prompt_wrapper import wrap_prompt

class BlogGenerator:
    def __init__(self, llm_logger, ollama_host: str, ollama_model: str):
        self.llm_logger = LLMLogger()
        self.ollama_host = ollama_host
        self.ollama_model = ollama_model

    def generate_content(self, selected_story: Dict) -> Optional[Dict]:
        """
        Generate full blog content from selected story.
        Returns structured blog content.
        """
        try:
            expected_format = {
                "title": "string (max 60 chars)",
                "content": "markdown formatted text",
                "meta_description": "string (max 160 chars)",
                "keywords": "array of strings"
            }
            
            prompt = wrap_prompt(
                base_prompt=f"Generate a technical blog post based on:\nTitle: {selected_story['title']}\nContent: {selected_story['description']}",
                expected_format=expected_format,
                system_context="You are a technical blog writer creating engaging content."
            )
            
            response = self._interact_with_llm(prompt)
            if not response or not response.get('success'):
                return None
                
            return json.loads(response['response'])
            
        except Exception as e:
            self.llm_logger.error(f"Blog generation failed: {str(e)}")
            return None

    def _interact_with_llm(self, prompt: str) -> Dict:
        """Interact with Ollama API with comprehensive logging."""
        try:
            # Log the outgoing prompt
            self.llm_logger.log_prompt(
                model=self.ollama_model,
                prompt=prompt,
                metadata={
                    'component': 'BlogGenerator',
                    'host': self.ollama_host,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Make the API call
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            response_text = response.json()["response"]
            
            # Log the incoming response
            self.llm_logger.log_response(
                model=self.ollama_model,
                response=response_text,
                metadata={
                    'component': 'BlogGenerator',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
            )
            
            return {"success": True, "response": response_text}
            
        except Exception as e:
            # Log error response
            self.llm_logger.log_response(
                model=self.ollama_model,
                response=f"Error: {str(e)}",
                metadata={
                    'component': 'BlogGenerator',
                    'error': True,
                    'error_type': type(e).__name__
                }
            )
            return {"success": False, "error": str(e)}