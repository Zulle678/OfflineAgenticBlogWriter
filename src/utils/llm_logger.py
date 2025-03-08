import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

class LLMLogger:
    def __init__(self, log_file: Optional[str] = None):
        self.logger = logging.getLogger('llm')
        self.logger.propagate = False
        
        if not self.logger.handlers:
            self.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        
        if log_file:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def debug(self, message):
        self.logger.debug(message)
        
    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def critical(self, message):
        self.logger.critical(message)

    def log_llm_interaction(self, direction: str, model: str, content: str) -> None:
        message = f"[{model}] {direction}:\n{content}"
        self.logger.info(message)

    def log_prompt(self, model: str, prompt: str, metadata: dict = None):
        extra = {
            'model': model,
            'direction': 'TO_LLM',
            'content_type': 'prompt'
        }
        self.debug(prompt, extra=extra)
        self.logger.info(f"[{model}] Sending prompt:\n{prompt}\n")

    def log_response(self, model: str, response: str, metadata: dict = None):
        extra = {
            'model': model,
            'direction': 'FROM_LLM',
            'content_type': 'response'
        }
        if metadata:
            response = f"{response}\nMetadata: {json.dumps(metadata, indent=2)}"
        self.debug(response, extra=extra)
        self.logger.info(f"[{model}] Received response:\n{response}\n")

    def log_interaction(self, prompt, response, metadata=None):
        # Log the interaction between the prompt and response
        self.log_prompt(model="default_model", prompt=prompt, metadata=metadata)
        self.log_response(model="default_model", response=response, metadata=metadata)

class ContentEnhancer:
    def __init__(self, llm_logger, ollama_host: str, ollama_model: str):
        self.llm_logger = llm_logger
        self.ollama_host = ollama_host
        self.ollama_model = ollama_model

    def enhance_story(self, story: Dict) -> Dict:
        try:
            prompt = wrap_prompt(
                base_prompt=self._build_enhancement_prompt(story),
                expected_format={
                    "enhanced_title": "string",
                    "enhanced_content": "string",
                    "additional_context": "string",
                    "technical_depth": "number (1-5)"
                }
            )
            
            response = self._interact_with_llm(prompt)
            if not response or not response.get('success'):
                return story
                
            enhanced = json.loads(response['response'])
            return {**story, **enhanced}
            
        except Exception as e:
            self.llm_logger.error(f"Enhancement failed: {str(e)}")
            return story