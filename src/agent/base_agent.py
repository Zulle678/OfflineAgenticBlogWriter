import requests
import logging

class BaseAgent:
    def __init__(self, llm_logger=None, ollama_host=None, ollama_model=None, num_ctx=4096, timeout=300):
        self.logger = llm_logger or logging.getLogger(__name__)
        self.ollama_host = ollama_host or "http://localhost:11434"
        self.ollama_model = ollama_model or "llama2"
        self.num_ctx = num_ctx
        self.timeout = timeout

    def _call_llm(self, prompt, system_prompt=None):
        headers = {'Content-Type': 'application/json'}
        data = {
            'model': self.ollama_model,
            'prompt': prompt,
            'system': system_prompt,
            'stream': False
        }
        
        try:
            response = requests.post(f"{self.ollama_host}/api/generate", 
                                   headers=headers,
                                   json=data,
                                   timeout=self.timeout)
            response.raise_for_status()
            raw_response = response.json()['response']
            
            # Clean the response by:
            # 1. Remove markdown code blocks
            # 2. Remove string concatenation
            # 3. Join multi-line strings
            cleaned_response = (raw_response
                              .replace('```json', '')
                              .replace('```', '')
                              .replace('" +', '"')
                              .replace('+ "', '"')
                              .strip())
            
            # If the response contains "Here is" or similar prefixes, try to extract just the content
            if "Here is" in cleaned_response:
                start = cleaned_response.find('{')
                end = cleaned_response.rfind('}') + 1
                if start >= 0 and end > 0:
                    cleaned_response = cleaned_response[start:end]
            
            return cleaned_response
            
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            self.logger.debug(f"Raw response: {raw_response}")
            return None