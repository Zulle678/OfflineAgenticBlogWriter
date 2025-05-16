FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask apscheduler gunicorn

# Copy the application code
COPY . .

# Create prompt files from examples if they don't exist
RUN if [ ! -f "src/prompts/selection_prompt.py" ]; then cp src/prompts/selection_prompt.py.example src/prompts/selection_prompt.py; fi
RUN if [ ! -f "src/prompts/generation_prompt.py" ]; then cp src/prompts/generation_prompt.py.example src/prompts/generation_prompt.py; fi

# Create necessary directories
RUN mkdir -p logs output/posts

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the web interface port
EXPOSE 5000

# Run the web application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "web.app:app"]