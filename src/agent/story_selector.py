from datetime import datetime
from typing import List, Dict, Optional
import logging
import requests
import json
import re
from src.prompts.selection_prompt import build_selection_prompt
from src.utils.llm_logger import LLMLogger
from .base_agent import BaseAgent

class StorySelector(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.system_prompt = """You are a technical blog content curator. 
Respond with ONLY a JSON object in this exact format, with no additional text or explanations:
{
    "selected_index": <number>,
    "reason": "<explanation string>"
}"""

    def _create_selection_prompt(self, stories):
        stories_list = []
        for i, story in enumerate(stories):
            stories_list.append(f"""[{i}] Title: {story['title']}
Description: {story['description']}
URL: {story['url']}""")
            
        stories_text = "\n\n".join(stories_list)
        
        return f"""Please analyze these news stories and select the most interesting one for a technical blog post:

{stories_text}

Select the story that best matches these criteria:
- Technical relevance and depth
- Current importance
- Educational value
- Reader engagement potential

Respond with a JSON object containing:
1. selected_index: the index number of the chosen story
2. reason: brief explanation of why this story was chosen"""

    def _extract_json(self, text):
        """Extract JSON object from text that might contain markdown and explanations."""
        try:
            # Find JSON between the most relevant curly braces
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start == -1 or end == 0:
                return None
                
            potential_json = text[start:end]
            
            # Clean up any markdown backticks or extra whitespace
            cleaned_json = (potential_json
                          .replace('```json', '')
                          .replace('```', '')
                          .strip())
            
            # Parse and validate
            data = json.loads(cleaned_json)
            
            # Ensure required fields exist and are valid
            if not isinstance(data, dict):
                return None
                
            selected_index = int(str(data.get('selected_index', '-1')))
            reason = data.get('reason')
            
            if selected_index < 0 or not reason:
                return None
                
            return {
                'selected_index': selected_index,
                'reason': reason
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.debug(f"JSON extraction failed: {e}")
            return None

    def select_story(self, stories):
        """Select the most interesting story from the provided list."""
        prompt = self._create_selection_prompt(stories)
        response = self._call_llm(prompt, system_prompt=self.system_prompt)
        
        if not response:
            self.logger.error("No response from LLM")
            return None
            
        selection = self._extract_json(response)
        if not selection:
            self.logger.error("Failed to parse story selection")
            self.logger.debug(f"Raw response: {response}")
            return None
            
        try:
            selected_index = selection['selected_index']
            selected_story = stories[selected_index]
            selected_story['selection_reason'] = selection['reason']
            return selected_story
            
        except IndexError as e:
            self.logger.error(f"Invalid story index: {e}")
            return None

    def _get_llm_response(self, prompt: str) -> Optional[str]:
        """Get response from Ollama API with proper error handling"""
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
            
            # Log raw response for debugging
            self.llm_logger.debug(f"Raw response: {response.text}")
            
            try:
                result = response.json()
                if "response" in result:
                    return result["response"]
                else:
                    self.llm_logger.error(f"Missing 'response' key in: {result}")
                    return None
            except json.JSONDecodeError as je:
                self.llm_logger.error(f"JSON parse error: {str(je)}\nRaw response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.llm_logger.error(f"Request failed: {str(e)}")
            return None
        except Exception as e:
            self.llm_logger.error(f"Unexpected error: {str(e)}")
            return None

    def _interact_with_llm(self, prompt: str) -> Dict:
        """Interact with Ollama API with logging."""
        try:
            # Log the prompt
            self.llm_logger.log_prompt(
                model=self.ollama_model,
                prompt=prompt,
                metadata={
                    'host': self.ollama_host,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
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
            
            # Log the response
            self.llm_logger.log_response(
                model=self.ollama_model,
                response=response_text,
                metadata={
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
            )
            
            return {"success": True, "response": response_text}
            
        except Exception as e:
            self.llm_logger.log_response(
                model=self.ollama_model,
                response=f"Error: {str(e)}",
                metadata={'error': True}
            )
            return {"success": False, "error": str(e)}

    def _parse_selection_response(self, response: str) -> Optional[Dict]:
        """Parse LLM response to extract selection data with better error handling"""
        try:
            self.llm_logger.debug(f"Parsing LLM response:\n{response}")
            
            # Extract JSON from response
            json_match = re.search(r'{.*}', response, re.DOTALL)
            if not json_match:
                self.llm_logger.error("No JSON found in response")
                return None
                
            selection_data = json.loads(json_match.group())
            
            # Validate required fields
            required_fields = ['selected_index', 'title', 'reasoning']
            missing_fields = [field for field in required_fields if field not in selection_data]
            
            if missing_fields:
                self.llm_logger.error(f"Missing required fields: {', '.join(missing_fields)}")
                return None
                
            # Extract source URL from original story if not in response
            try:
                idx = int(selection_data['selected_index']) - 1
                if 'source_url' not in selection_data:
                    selection_data['source_url'] = stories[idx].get('url', '')
            except (ValueError, IndexError):
                self.llm_logger.error("Invalid story index in response")
                return None
                
            # Add default score if missing
            if 'relevance_score' not in selection_data:
                selection_data['relevance_score'] = 5
                
            return selection_data
            
        except json.JSONDecodeError as e:
            self.llm_logger.error(f"Failed to parse JSON response: {str(e)}")
            return None
        except Exception as e:
            self.llm_logger.error(f"Failed to parse selection response: {str(e)}")
            return None