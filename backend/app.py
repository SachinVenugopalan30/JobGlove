import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from routes.health import health_bp
from routes.resume import resume_bp
from config import Config
from utils.logger import app_logger
from database.db import init_db

app = Flask(__name__, static_folder=None)
CORS(app)

# Set static folder path manually (don't use Flask's built-in static serving)
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')

# Configure Flask
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# Register blueprints
app.register_blueprint(health_bp, url_prefix='/api')
app.register_blueprint(resume_bp, url_prefix='/api')

# Serve frontend static files in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend static files for SPA routing"""
    # Don't intercept API routes
    if path.startswith('api/'):
        return {'error': 'Endpoint not found'}, 404

    # If path points to an actual file, serve it
    file_path = os.path.join(STATIC_FOLDER, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(STATIC_FOLDER, path)

    # For all other routes (including /tailor), serve index.html for SPA routing
    return send_from_directory(STATIC_FOLDER, 'index.html')

@app.errorhandler(413)
def request_entity_too_large(error):
    app_logger.warning(f"Request entity too large: {error}")
    return {'error': 'File too large'}, 413

@app.errorhandler(404)
def not_found(error):
    app_logger.warning(f"Endpoint not found: {error}")
    return {'error': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    app_logger.error(f"Internal server error: {error}")
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    app_logger.info("=" * 50)
    app_logger.info("Starting JobGlove Application")

    # Initialize database
    init_db()
    app_logger.info("Database initialized")

    app_logger.info(f"Upload folder: {Config.UPLOAD_FOLDER}")
    app_logger.info(f"Output folder: {Config.OUTPUT_FOLDER}")
    app_logger.info(f"Max file size: {Config.MAX_FILE_SIZE / 1024 / 1024}MB")

    # Log available API keys
    available_apis = Config.check_api_availability()
    app_logger.info(f"Available APIs: {', '.join([k for k, v in available_apis.items() if v])}")
    app_logger.info("=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
