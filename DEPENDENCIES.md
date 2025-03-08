# Project Dependencies Documentation

## Agent Module Dependencies

### [`news_scraper.py`](src/agent/news_scraper.py)
**Dependencies:**
- External: `logging`, `os`, `requests`, `feedparser`, `pathlib`, `typing`
- Uses [`config/keywords.txt`](config/keywords.txt) for filtering

### [`content_enhancer.py`](src/agent/content_enhancer.py)
**Dependencies:**
- [`base_agent.py`](src/agent/base_agent.py)
- [`src/utils/llm_logger.py`](src/utils/llm_logger.py)
- [`src/utils/prompt_wrapper.py`](src/utils/prompt_wrapper.py)
- Imports from [`story_selector.py`](src/agent/story_selector.py) and [`blog_generator.py`](src/agent/blog_generator.py)

### [`blog_generator.py`](src/agent/blog_generator.py)
**Dependencies:**
- [`src/prompts/generation_prompt.py`](src/prompts/generation_prompt.py)
- [`src/utils/llm_logger.py`](src/utils/llm_logger.py)
- [`src/utils/prompt_wrapper.py`](src/utils/prompt_wrapper.py)
- External: `requests`, `json`, `datetime`

### [`story_selector.py`](src/agent/story_selector.py)
**Dependencies:**
- [`base_agent.py`](src/agent/base_agent.py)
- [`src/prompts/selection_prompt.py`](src/prompts/selection_prompt.py)
- [`src/utils/llm_logger.py`](src/utils/llm_logger.py)
- External: `requests`, `json`, `re`, `datetime`

### [`blog_writer.py`](src/agent/blog_writer.py)
**Dependencies:**
- [`base_agent.py`](src/agent/base_agent.py)
- [`content_enhancer.py`](src/agent/content_enhancer.py)
- [`src/utils/llm_logger.py`](src/utils/llm_logger.py)
- External: `pathlib`, `datetime`, `requests`, `re`

### [`base_agent.py`](src/agent/base_agent.py)
**Dependencies:**
- External: `requests`, `logging`
- Core class that other agents inherit from

## Utils Module Dependencies

### [`llm_logger.py`](src/utils/llm_logger.py)
**Dependencies:**
- External: `logging`, `json`, `datetime`, `pathlib`, `typing`

### [`prompt_wrapper.py`](src/utils/prompt_wrapper.py)
**Dependencies:**
- External: `typing`

## Prompts Module Dependencies

### [`generation_prompt.py`](src/prompts/generation_prompt.py)
**Dependencies:**
- External: `typing`
- Contains template for blog generation

### [`selection_prompt.py`](src/prompts/selection_prompt.py)
**Dependencies:**
- External: `typing`, `re`
- Contains template for story selection

## Main Program Dependencies

### [`main.py`](src/main.py)
**Dependencies:**
- All agent modules
- [`src/utils/llm_logger.py`](src/utils/llm_logger.py)
- External: `os`, `sys`, `pathlib`, `dotenv`, `logging`, `yaml`, `json`

## Test Dependencies

### [`test_llm_connection.py`](tests/test_llm_connection.py)
**Dependencies:**
- External: `unittest`, `requests`, `os`, `dotenv`, `sys`, `time`, `json`

### [`test_news_scraper_output.py`](tests/test_news_scraper_output.py)
**Dependencies:**
- [`src/agent/news_scraper.py`](src/agent/news_scraper.py)
- External: `json`, `pathlib`, `dotenv`

## Configuration Files
- [`.env`](.env) - Required by multiple modules
- [`config/keywords.txt`](config/keywords.txt) - Used by [`news_scraper.py`](src/agent/news_scraper.py)
- [`config/enhance_prompt.txt`](config/enhance_prompt.txt) - Used by [`content_enhancer.py`](src/agent/content_enhancer.py)

## Output Dependencies
- [`output/posts/`](output/posts/) - Directory for generated blog posts
- [`logs/llm_interactions.log`](logs/llm_interactions.log) - LLM interaction logging

## Key External Dependencies
From [`requirements.txt`](requirements.txt):
- `requests>=2.31.0`
- `python-dotenv>=1.0.0`
- `PyYAML>=6.0`
- `beautifulsoup4==4.13.3`
- `GoogleNews==1.6.12`

## Circular Dependencies Warning
Potential circular imports between:
1. [`content_enhancer.py`](src/agent/content_enhancer.py) ↔ [`story_selector.py`](src/agent/story_selector.py)
2. [`content_enhancer.py`](src/agent/content_enhancer.py) ↔ [`blog_generator.py`](src/agent/blog_generator.py)

These should be refactored to improve code maintainability.