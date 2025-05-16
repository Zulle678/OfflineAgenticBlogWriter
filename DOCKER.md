# Docker Support for Agentic Blog Writer

This project includes Docker support for easy deployment and operation. The Docker setup includes a web interface for scheduling blog generation jobs.

## Features

- Containerized application with all dependencies
- Integrated Ollama LLM service
- Web interface for scheduling
- Volume mounts for persistent data

## Prerequisites

- Docker and Docker Compose installed
- (Optional) NVIDIA GPU for accelerated LLM inference

## Quick Start

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <repository-url>
   cd agentic-blog-writer
   ```

2. Start the application using Docker Compose:
   ```bash
   docker compose up -d
   ```

3. Access the web interface at:
   ```
   http://localhost:5000
   ```

## Configuration

### Environment Variables

The Docker Compose file includes default environment variables, which you can modify either in a `.env` file or by setting environment variables before running docker-compose:

- `OLLAMA_HOST`: URL for the Ollama server (default: http://ollama:11434)
- `OLLAMA_MODEL`: LLM model to use (default: llama2)
- `OLLAMA_TIMEOUT`: Timeout in seconds (default: 300)
- `OLLAMA_NUM_CTX`: Context size for LLM (default: 4096)
- `NEWS_SOURCE`: News source URL (default: https://news.google.com)
- `NEWS_LANGUAGE`: News language (default: en)
- `NEWS_PERIOD`: News period to fetch (default: 7d)
- `NEWS_NUM_STORIES`: Number of stories to fetch (default: 10)
- Additional blog configuration options (see `.env.example`)

### Persistent Data

The Docker setup uses volumes for persistent data, which can all be customized using environment variables:

- `${POSTS_DIR:-./output}:/app/output`: Blog posts output directory
- `${LOGS_DIR:-./logs}:/app/logs`: Application logs
- `${CONFIG_DIR:-./config}:/app/config`: Configuration files
- `ollama_data`: Ollama models and data

#### Customizing Volume Paths

You can specify custom paths for your blog posts, logs, and configuration by setting environment variables:

1. Create a `.env` file (you can copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. Modify the paths in the `.env` file:
   ```
   # Use absolute paths for better reliability
   POSTS_DIR=/path/to/your/blog/posts
   LOGS_DIR=/path/to/your/logs
   CONFIG_DIR=/path/to/your/config
   ```

3. Or specify them directly when running:
   ```bash
   POSTS_DIR=/path/to/custom/posts docker compose up -d
   ```

## Web Interface

The web interface allows you to:

1. **Schedule Blog Generation**:
   - Set up interval-based schedules (run every X hours)
   - Set up cron-based schedules (run on specific days/times)
   - Enable/disable the schedule

2. **Manual Execution**:
   - Run the blog generator immediately with the "Run Now" button

## Customization

### Using a Different LLM Model

By default, the setup uses the `llama2` model. To use a different model:

1. Update the `OLLAMA_MODEL` environment variable in `docker-compose.yml`
2. Pull the model in the Ollama container:
   ```bash
   docker compose exec ollama ollama pull <model-name>
   ```

### GPU Acceleration

The Docker Compose file includes NVIDIA GPU support. If you don't have a GPU or don't want to use GPU acceleration:

1. Remove or comment out the `deploy` section in the `ollama` service in `docker-compose.yml`

## Troubleshooting

### Logs

To view logs:

```bash
# View web application logs
docker compose logs webapp

# View Ollama logs
docker compose logs ollama

# Follow logs in real-time
docker compose logs -f
```

### Common Issues

1. **Ollama Connection Issues**:
   - Ensure the Ollama service is running: `docker compose ps`
   - Check that the model is downloaded: `docker compose exec ollama ollama list`

2. **Web Interface Not Accessible**:
   - Ensure port 5000 is not in use by another application
   - Check the container is running: `docker compose ps`

## Updating

To update the application:

```bash
git pull
docker compose build --no-cache
docker compose up -d
```