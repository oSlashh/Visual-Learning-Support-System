from flask import Blueprint, jsonify

# Create a blueprint for note-processing routes
upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint to verify backend status 
    and connection connectivity.
    """
    response_data = {
        "status": "healthy",
        "service": "SmartNotes AI Backend",
        "version": "1.0.0"
    }
    return jsonify(response_data), 200
