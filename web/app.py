from flask import Flask, render_template, request, jsonify
import os
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import subprocess
import json
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Path to store schedule information
SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), 'schedule.json')

def load_schedule():
    """Load saved schedule from file"""
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading schedule: {e}")
    return {'enabled': False, 'schedule': {}}

def save_schedule(schedule_data):
    """Save schedule to file"""
    try:
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(schedule_data, f)
    except Exception as e:
        logger.error(f"Error saving schedule: {e}")

def run_blog_generator():
    """Run the main.py script"""
    try:
        logger.info("Starting blog generation...")
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'main.py')
        result = subprocess.run(['python', script_path], capture_output=True, text=True)
        logger.info(f"Blog generation completed with return code {result.returncode}")
        if result.returncode != 0:
            logger.error(f"Error: {result.stderr}")
    except Exception as e:
        logger.error(f"Error running blog generator: {e}")

# Initialize scheduler from saved state
def init_scheduler():
    schedule_data = load_schedule()
    if schedule_data['enabled']:
        schedule = schedule_data['schedule']
        if schedule.get('type') == 'interval':
            hours = int(schedule.get('hours', 24))
            scheduler.add_job(
                run_blog_generator, 
                'interval', 
                hours=hours, 
                id='blog_generator',
                replace_existing=True
            )
        elif schedule.get('type') == 'cron':
            scheduler.add_job(
                run_blog_generator, 
                'cron', 
                day_of_week=schedule.get('day_of_week', '*'),
                hour=schedule.get('hour', 0),
                minute=schedule.get('minute', 0),
                id='blog_generator',
                replace_existing=True
            )

# Initialize the scheduler
init_scheduler()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Get the current schedule"""
    return jsonify(load_schedule())

@app.route('/api/schedule', methods=['POST'])
def set_schedule():
    """Set a new schedule"""
    data = request.json
    
    # Clear existing job if it exists
    if scheduler.get_job('blog_generator'):
        scheduler.remove_job('blog_generator')
    
    schedule_data = {'enabled': data.get('enabled', False), 'schedule': {}}
    
    if schedule_data['enabled']:
        schedule_type = data.get('type', 'interval')
        schedule_data['schedule']['type'] = schedule_type
        
        if schedule_type == 'interval':
            hours = int(data.get('hours', 24))
            schedule_data['schedule']['hours'] = hours
            
            scheduler.add_job(
                run_blog_generator, 
                'interval', 
                hours=hours, 
                id='blog_generator'
            )
            
        elif schedule_type == 'cron':
            day_of_week = data.get('day_of_week', '*')
            hour = int(data.get('hour', 0))
            minute = int(data.get('minute', 0))
            
            schedule_data['schedule']['day_of_week'] = day_of_week
            schedule_data['schedule']['hour'] = hour
            schedule_data['schedule']['minute'] = minute
            
            scheduler.add_job(
                run_blog_generator, 
                'cron', 
                day_of_week=day_of_week,
                hour=hour,
                minute=minute,
                id='blog_generator'
            )
    
    save_schedule(schedule_data)
    return jsonify({'status': 'success', 'schedule': schedule_data})

@app.route('/api/run-now', methods=['POST'])
def run_now():
    """Run the blog generator immediately"""
    run_blog_generator()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)