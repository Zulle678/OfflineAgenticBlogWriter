import unittest
import requests
import os
from dotenv import load_dotenv, find_dotenv
import sys
import time
import json

class OllamaConnectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n🔧 Loading configuration from .env file...")
        
        # Clear existing OLLAMA environment variables
        ollama_vars = [key for key in os.environ if key.startswith('OLLAMA_')]
        print("\n🧹 Clearing existing OLLAMA environment variables:")
        for key in ollama_vars:
            print(f"   Removing {key}={os.environ[key]}")
            del os.environ[key]
        
        # Print the .env file path and contents
        dotenv_path = find_dotenv()
        print(f"\n📂 Loading .env from: {dotenv_path}")
        print("📄 .env file contents (OLLAMA-related):")
        with open(dotenv_path) as f:
            for line in f:
                if line.strip() and line.startswith('OLLAMA_'):
                    print(f"   {line.strip()}")
        
        # Load and verify immediate env var value
        load_dotenv(override=True)
        raw_model = os.getenv('OLLAMA_MODEL')
        print(f"\n🔍 Raw OLLAMA_MODEL from env after loading: {raw_model}")
        
        cls.config = {
            'host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            'model': os.getenv('OLLAMA_MODEL'),
            'timeout': int(os.getenv('OLLAMA_TIMEOUT', '300'))
        }
        print(f"📝 Using configuration:\n" + \
              f"   - Host: {cls.config['host']}\n" + \
              f"   - Model: {cls.config['model']}\n" + \
              f"   - Timeout: {cls.config['timeout']}s")

    def test_ollama_server_connection(self):
        """Test if Ollama server is accessible"""
        print("\n🔄 Testing connection to Ollama server...")
        try:
            response = requests.get(f"{self.config['host']}/api/tags")
            self.assertEqual(response.status_code, 200, "Failed to connect to Ollama server")
            print("✅ Successfully connected to Ollama server")
        except requests.exceptions.RequestException as e:
            print("❌ Failed to connect to Ollama server")
            self.fail(f"Could not connect to Ollama server: {str(e)}")

    def test_ollama_model_availability(self):
        """Test if specified model is available on Ollama server"""
        print(f"\n🔄 Checking if model '{self.config['model']}' is available...")
        try:
            response = requests.get(f"{self.config['host']}/api/tags")
            self.assertEqual(response.status_code, 200)
            
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            self.assertIn(self.config['model'], model_names,
                         f"Model {self.config['model']} not found on server")
            print(f"✅ Model '{self.config['model']}' found on server")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error checking model availability")
            self.fail(f"Error checking model availability: {str(e)}")

    def test_ollama_generate_response(self):
        """Test if model can generate a response and measure performance"""
        print("\n🔄 Testing model response generation...")
        try:
            # Get model info first
            model_response = requests.post(
                f"{self.config['host']}/api/show",
                json={"name": self.config['model']}
            )
            model_info = model_response.json()
            
            # Performance test with response generation
            test_prompt = "Test message: reply with 'ok' if you can read this."
            start_time = time.time()
            
            response = requests.post(
                f"{self.config['host']}/api/generate",
                json={
                    "model": self.config['model'],
                    "prompt": test_prompt,
                    "stream": False
                },
                timeout=self.config['timeout']
            )
            
            end_time = time.time()
            
            # Validate response
            self.assertEqual(response.status_code, 200, "Failed to generate response")
            result = response.json()
            self.assertIn('response', result, "No response field in result")
            self.assertGreater(len(result['response'].strip()), 0, "Empty response from model")
            
            # Calculate and display metrics
            prompt_tokens = len(test_prompt.split())
            response_tokens = len(result['response'].split())
            total_time = end_time - start_time
            tokens_per_second = (prompt_tokens + response_tokens) / total_time
            
            print("✅ Successfully generated response")
            print(f"\n📈 Model Information:")
            print(f"   - Parameter Count: {model_info.get('parameters', 'N/A')} parameters")
            print(f"   - Model Template: {model_info.get('template', 'N/A')}")
            print(f"   - License: {model_info.get('license', 'N/A')}")
            
            print(f"\n⚡ Performance Metrics:")
            print(f"   - Processing time: {total_time:.2f} seconds")
            print(f"   - Input tokens: {prompt_tokens}")
            print(f"   - Output tokens: {response_tokens}")
            print(f"   - Tokens per second: {tokens_per_second:.2f}")
            
            if 'total_duration' in result:
                print(f"   - Model processing time: {result['total_duration']:.2f}ms")
            if 'load_duration' in result:
                print(f"   - Model load time: {result['load_duration']:.2f}ms")
            
            print(f"\n📝 Model response: {result['response'].strip()}")
            
        except requests.exceptions.RequestException as e:
            print("❌ Failed to generate response")
            self.fail(f"Error testing model generation: {str(e)}")

    def test_server_metrics(self):
        """Test server configuration and performance metrics"""
        print("\n📊 Checking server metrics and configuration...")
        try:
            # Get model info
            response = requests.post(
                f"{self.config['host']}/api/show",
                json={"name": self.config['model']}
            )
            self.assertEqual(response.status_code, 200)
            model_info = response.json()
            
            print(f"\n📈 Model Information:")
            print(f"   - Parameter Count: {model_info.get('parameters', 'N/A')} parameters")
            print(f"   - Model Template: {model_info.get('template', 'N/A')}")
            print(f"   - Model License: {model_info.get('license', 'N/A')}")
            print(f"   - Model Format: {model_info.get('format', 'N/A')}")
            
            # Performance test
            print("\n⚡ Running performance test...")
            test_prompt = "Generate a short story about a robot in exactly 100 words."
            
            start_time = time.time()
            response = requests.post(
                f"{self.config['host']}/api/generate",
                json={
                    "model": self.config['model'],
                    "prompt": test_prompt,
                    "stream": False
                }
            )
            end_time = time.time()
            
            result = response.json()
            
            # Calculate metrics
            prompt_tokens = len(test_prompt.split())
            response_tokens = len(result['response'].split())
            total_time = end_time - start_time
            tokens_per_second = (prompt_tokens + response_tokens) / total_time
            
            print(f"\n🔍 Performance Metrics:")
            print(f"   - Total processing time: {total_time:.2f} seconds")
            print(f"   - Input tokens: {prompt_tokens}")
            print(f"   - Output tokens: {response_tokens}")
            print(f"   - Tokens per second: {tokens_per_second:.2f}")
            
            # Memory usage if available
            if 'total_duration' in result:
                print(f"   - Model processing time: {result['total_duration']:.2f}ms")
            if 'load_duration' in result:
                print(f"   - Model load time: {result['load_duration']:.2f}ms")
            
        except requests.exceptions.RequestException as e:
            print("❌ Failed to retrieve server metrics")
            self.fail(f"Error getting server metrics: {str(e)}")

if __name__ == '__main__':
    print("🚀 Starting Ollama Connection Tests")
    unittest.main(verbosity=2)