"""
Task Manager Application
A simple Flask web application for managing tasks with MongoDB backend.
Demonstrates stateless application architecture on Kubernetes.
"""
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
# from flask_wtf.csrf import CSRFProtect  # Disabled for demo - enable in production
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security configuration
# Use SECRET_KEY from environment, or generate a default for development
# In production, always set SECRET_KEY environment variable
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    logger.warning("SECRET_KEY not set, using insecure default for development")
    SECRET_KEY = 'dev-insecure-key-change-in-production'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
# csrf = CSRFProtect(app)  # Disabled for demo - enable in production

# MongoDB Configuration from environment variables
# Supports two methods (in priority order):
# 1. Individual variables: MONGODB_USERNAME, MONGODB_PASSWORD, MONGODB_HOSTNAME, MONGODB_PORT, MONGODB_DBNAME (recommended)
# 2. MONGODB_URI: Full connection string (fallback for backward compatibility)
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', '')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', '')
MONGODB_HOSTNAME = os.getenv('MONGODB_HOSTNAME', os.getenv('MONGODB_HOST', 'localhost'))  # Support both new and old names
MONGODB_PORT = int(os.getenv('MONGODB_PORT', '27017'))
MONGODB_DBNAME = os.getenv('MONGODB_DBNAME', os.getenv('MONGODB_DATABASE', 'taskdb'))  # Support both new and old names
MONGODB_URI = os.getenv('MONGODB_URI', '')  # Fallback for backward compatibility

# Pod information for load balancing demonstration
POD_NAME = os.getenv('HOSTNAME', 'local')
POD_IP = os.getenv('POD_IP', 'localhost')

# MongoDB connection
def get_db_connection():
    """
    Create and return MongoDB connection.
    Supports two configuration methods (in priority order):
    1. Individual variables: MONGODB_USERNAME, MONGODB_PASSWORD, MONGODB_HOSTNAME, MONGODB_PORT, MONGODB_DBNAME (recommended)
    2. MONGODB_URI environment variable (fallback for backward compatibility)
    """
    try:
        # Method 1: Build connection string from individual variables (new primary method)
        if MONGODB_USERNAME and MONGODB_PASSWORD and MONGODB_HOSTNAME:
            connection_string = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOSTNAME}:{MONGODB_PORT}/{MONGODB_DBNAME}?authSource=admin"
            logger.info(f"Using individual variables for authenticated connection to {MONGODB_HOSTNAME}:{MONGODB_PORT}")
        # Method 2: Use MONGODB_URI if provided and no individual variables (backward compatibility)
        elif MONGODB_URI:
            connection_string = MONGODB_URI
            logger.info("Using MONGODB_URI for connection (backward compatibility)")
        # Method 3: Non-authenticated connection using hostname only (local development)
        elif MONGODB_HOSTNAME:
            connection_string = f"mongodb://{MONGODB_HOSTNAME}:{MONGODB_PORT}/{MONGODB_DBNAME}"
            logger.info(f"Using non-authenticated connection to {MONGODB_HOSTNAME}:{MONGODB_PORT}")
        else:
            raise Exception("No MongoDB connection configuration found. Please set either individual variables (MONGODB_USERNAME, MONGODB_PASSWORD, MONGODB_HOSTNAME) or MONGODB_URI")
        
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB")
        return client[MONGODB_DBNAME]
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise

# Initialize database connection
try:
    db = get_db_connection()
    tasks_collection = db.tasks
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    db = None
    tasks_collection = None

@app.route('/')
def index():
    """Main page - display all tasks"""
    try:
        if tasks_collection is None:
            return render_template('error.html', 
                                 error='Database not available',
                                 pod_name=POD_NAME), 503
        
        # Get all tasks sorted by creation date (newest first)
        tasks = list(tasks_collection.find({}).sort('created_at', -1))
        
        # Count statistics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.get('completed', False))
        pending_tasks = total_tasks - completed_tasks
        
        return render_template('index.html',
                             tasks=tasks,
                             total_tasks=total_tasks,
                             completed_tasks=completed_tasks,
                             pending_tasks=pending_tasks,
                             pod_name=POD_NAME,
                             pod_ip=POD_IP)
    except Exception as e:
        logger.error(f"Error loading tasks: {e}")
        return render_template('error.html',
                             error='Unable to load tasks',
                             pod_name=POD_NAME), 500

@app.route('/create', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        if tasks_collection is None:
            return jsonify({'error': 'Database not available'}), 503
        
        title = request.form.get('title', '').strip()
        if not title:
            return redirect(url_for('index'))
        
        task = {
            'title': title,
            'completed': False,
            'created_at': datetime.utcnow(),
            'created_by_pod': POD_NAME
        }
        
        result = tasks_collection.insert_one(task)
        logger.info(f"Task created: {result.inserted_id} by pod {POD_NAME}")
        
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return render_template('error.html',
                             error='Unable to create task',
                             pod_name=POD_NAME), 500

@app.route('/complete/<task_id>', methods=['POST'])
def complete_task(task_id):
    """Toggle task completion status"""
    try:
        if tasks_collection is None:
            return jsonify({'error': 'Database not available'}), 503
        
        # Get current task
        task = tasks_collection.find_one({'_id': ObjectId(task_id)})
        if not task:
            return redirect(url_for('index'))
        
        # Toggle completed status
        new_status = not task.get('completed', False)
        
        tasks_collection.update_one(
            {'_id': ObjectId(task_id)},
            {
                '$set': {
                    'completed': new_status,
                    'updated_at': datetime.utcnow(),
                    'updated_by_pod': POD_NAME
                }
            }
        )
        
        logger.info(f"Task {task_id} marked as {'completed' if new_status else 'pending'} by pod {POD_NAME}")
        
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return render_template('error.html',
                             error='Unable to update task',
                             pod_name=POD_NAME), 500

@app.route('/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    """Delete a task"""
    try:
        if tasks_collection is None:
            return jsonify({'error': 'Database not available'}), 503
        
        result = tasks_collection.delete_one({'_id': ObjectId(task_id)})
        
        if result.deleted_count > 0:
            logger.info(f"Task {task_id} deleted by pod {POD_NAME}")
        
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return render_template('error.html',
                             error='Unable to delete task',
                             pod_name=POD_NAME), 500

@app.route('/delete-all', methods=['POST'])
def delete_all_tasks():
    """Delete all completed tasks"""
    try:
        if tasks_collection is None:
            return jsonify({'error': 'Database not available'}), 503
        
        result = tasks_collection.delete_many({'completed': True})
        logger.info(f"All completed tasks deleted ({result.deleted_count} tasks) by pod {POD_NAME}")
        
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error deleting completed tasks: {e}")
        return render_template('error.html',
                             error='Unable to delete tasks',
                             pod_name=POD_NAME), 500

@app.route('/health')
def health():
    """Health check endpoint for Kubernetes liveness probe"""
    return jsonify({
        'status': 'healthy',
        'pod': POD_NAME,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/ready')
def ready():
    """Readiness check endpoint for Kubernetes readiness probe"""
    try:
        if db is None:
            raise Exception("Database not initialized")
        # Test database connection
        db.command('ping')
        return jsonify({
            'status': 'ready',
            'pod': POD_NAME,
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            'status': 'not ready',
            'pod': POD_NAME,
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html',
                         error='Page not found',
                         pod_name=POD_NAME), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html',
                         error='Internal server error',
                         pod_name=POD_NAME), 500

if __name__ == '__main__':
    # For development only - use gunicorn in production
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=True)
