# Agentic Blog Writer
Peronal note: I know its likely messy code and will have people laugh, cry or whatever; I'm not an engineer, just a guy equipped with an AI. 


## Overview
An AI-powered blog automation system that scrapes technology news, analyzes relevance using keywords, generates blog posts using LLM (Ollama), and creates TypeScript blog posts. The system focuses on AI, technology, and digital transformation topics.

LLMs successfully tested:
   - Llama2
   - Llama3.1
   - Llama3.2
   - phi3
   - phi4
   - deepseek-r1

## System Architecture

### Core Components

1. **Base Agent** (`src/agent/base_agent.py`)
   - Handles common Ollama API calls
   - Manages logging and error handling
   - Provides foundation for all agent classes

2. **News Scraper** (`src/agent/news_scraper.py`)
   - Fetches news from configured sources
   - Filters based on keywords from `config/keywords.txt`
   - Deduplicates and sanitizes content

3. **Story Selector** (`src/agent/story_selector.py`)
   - Evaluates and ranks news stories
   - Uses LLM for intelligent story selection
   - Returns structured selection data

4. **Blog Writer** (`src/agent/blog_writer.py`)
   - Generates blog content using LLM
   - Creates markdown files with proper citations
   - Manages file operations and metadata

5. **Content Enhancer** (`src/agent/content_enhancer.py`)
   - Enriches content with additional context
   - Manages technical depth and readability
   - Improves overall content quality

## Project Structure
```
agentic-blog-writer/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── news_scraper.py
│   │   ├── story_selector.py
│   │   ├── content_enhancer.py
│   │   └── blog_writer.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── llm_logger.py
│   └── main.py
├── output/
│   └── posts/
├── config/
│   ├── config.yml
│   └── keywords.txt
├── requirements.txt
├── .env
└── README.md
```

## Features
- **News Scraping**: Automated fetching of latest technology news
- **Story Selection**: AI-powered selection of relevant stories
- **Blog Generation**: LLM-based blog post creation with proper citations
- **Content Enhancement**: Automated content improvement and enrichment

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Navigate to the project directory:
```bash
cd agentic-blog-writer
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create and configure `.env` file:
```ini
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=your_model_name_here
OLLAMA_TIMEOUT=300
NEWS_SOURCE=https://news.google.com
NEWS_LANGUAGE=en
NEWS_PERIOD=1d
NEWS_NUM_STORIES=10
```

## Configuration

### Keywords
Update `config/keywords.txt` with relevant keywords for news filtering:
- AI and ML related terms
- Tech industry keywords
- Business transformation topics

### YAML Configuration
Update `config/config.yml` with your settings:
```yaml
ollama:
  host: http://localhost:11434
  model: llama3.2:latest
  num_ctx: 4096
  timeout: 300
```

### Prompt Files
The application uses two prompt configuration files that need to be set up:

1. Copy the example prompt files:
```bash
cp src/prompts/generation_prompt.py.example src/prompts/generation_prompt.py
cp src/prompts/selection_prompt.py.example src/prompts/selection_prompt.py
```

2. Edit the files and replace the placeholder values:
- In `generation_prompt.py`: Replace [COMPANY_NAME] with your company name
- In `selection_prompt.py`: Configure your selection criteria

### Prompt Configuration

The selection prompt (`selection_prompt.py`) requires the following placeholders to be replaced:

- `[ORGANIZATION_NAME]`: Your organization name
- `[ORGANIZATION_DESCRIPTION]`: A brief description of your organization's focus
- `[CRITERION_1]`: First selection criterion
- `[CRITERION_2]`: Second selection criterion
- `[CRITERION_3]`: Third selection criterion

Example configuration:
```python
ORGANIZATION_NAME = "Example Corp"
ORGANIZATION_DESCRIPTION = "We focus on developing AI solutions..."
CRITERION_1 = "Technical depth and innovation"
CRITERION_2 = "Business impact and market relevance"
CRITERION_3 = "Current technological trends"
```

## Usage

### Standard Usage

Run the application:
```bash
python src/main.py
```

The system will:
1. Fetch news articles based on keywords
2. Select the most relevant story
3. Generate a blog post with citations
4. Save the post to `output/posts/`

### Docker Usage

This project supports Docker deployment with a web interface for scheduling:

```bash
docker compose up -d
```

Then access the web interface at `http://localhost:5000`

For detailed Docker instructions, see [DOCKER.md](DOCKER.md)

## Error Handling

The system includes comprehensive error handling:
- LLM connection issues
- News fetching failures
- Content generation errors
- File operation problems

All errors are logged via the `LLMLogger` for debugging.

## Dependencies

Key requirements:
- `requests>=2.31.0`
- `python-dotenv>=1.0.0`
- `PyYAML>=6.0`

## Testing
To run the tests:
```bash
pytest tests/
```

## License
MIT License

## Acknowledgments
- Google News for providing news articles
- Ollama for LLM capabilities
- Key open-source libraries:
  - requests by Kenneth Reitz
  - python-dotenv by Saurabh Kumar
  - PyYAML by Kirill Simonov
  - feedparser by Kurt McKee

