from flask import Flask, jsonify
from app.routes.queue_routes import queue_bp
from app.routes.worker_routes import worker_bp
from app.routes.log_routes import log_bp

def create_app():
    app = Flask(__name__)
    
    # Register all blueprints with their URL prefixes
    app.register_blueprint(queue_bp, url_prefix='/queue')
    app.register_blueprint(worker_bp, url_prefix='/worker')
    app.register_blueprint(log_bp, url_prefix='/logs')
    
    @app.route("/")
    def index():
        return jsonify({
            "success": True,
            "message": "code hale che🚀🚀🚀🚀"
        }), 200


    
    return app
