from flask import Flask
from flask_cors import CORS
from routes.upload import upload_bp

def create_app() -> Flask:
    """
    Factory function to initialize the Flask application,
    configure CORS, and register blueprints.
    """
    app = Flask(__name__)
    
    # Configure CORS to accept requests from the Angular development server
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
    
    # Register routes
    app.register_blueprint(upload_bp, url_prefix='/api')
    
    return app

app = create_app()

if __name__ == '__main__':
    # Start server locally on port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
