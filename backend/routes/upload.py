import os
import uuid
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

# Create a blueprint for note-processing routes
upload_bp = Blueprint('upload', __name__)

# Resolve uploads directory relative to this folder (backend/uploads/incoming)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_INCOMING_DIR = os.path.join(BACKEND_DIR, 'uploads', 'incoming')

# Ensure incoming directory exists
os.makedirs(UPLOAD_INCOMING_DIR, exist_ok=True)

def allowed_file(filename: str) -> bool:
    """Helper to check if the file extension is strictly PDF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

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

@upload_bp.route('/upload', methods=['POST'])
def upload_pdf():
    """
    Handles PDF file uploading. Validates the file payload, generates
    a unique UUID filename, saves it under uploads/incoming/, and returns metadata.
    """
    # 1. Check if the file is part of the request payload
    if 'pdf' not in request.files:
        return jsonify({
            "status": "error",
            "message": "No file part in the request payload. Please upload a file as 'pdf'."
        }), 400
        
    file = request.files['pdf']
    
    # 2. Check if a file was actually selected
    if file.filename == '':
        return jsonify({
            "status": "error",
            "message": "No file selected."
        }), 400
        
    # 3. Check if the file is a PDF
    if not allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": "Invalid file format. Only PDF documents are allowed."
        }), 400
        
    try:
        # Sanitize original name
        original_name = secure_filename(file.filename)
        
        # Generate unique UUID filename to prevent naming collisions
        stored_name = f"{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(UPLOAD_INCOMING_DIR, stored_name)
        
        # Save the file to the local incoming directory
        file.save(filepath)
        
        # 4. Return success metadata response per Phase 2 requirements
        return jsonify({
            "status": "success",
            "original_filename": original_name,
            "stored_filename": stored_name,
            "pages": None,
            "message": "PDF uploaded successfully."
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to save file: {str(e)}"
        }), 500

@upload_bp.route('/process', methods=['POST'])
def process_pdf():
    """
    Locates the uploaded PDF using stored_filename, extracts text page-by-page,
    counts pages/words, generates a 500-character preview, and caches text locally.
    """
    data = request.get_json()
    if not data or 'stored_filename' not in data:
        return jsonify({
            "status": "error",
            "message": "Missing 'stored_filename' in the request payload."
        }), 400
        
    stored_filename = data['stored_filename']
    filepath = os.path.join(UPLOAD_INCOMING_DIR, stored_filename)
    
    try:
        from modules.document_processor import extract_pdf_text
        result = extract_pdf_text(filepath)
        
        return jsonify({
            "status": "success",
            "pages": result["pages"],
            "wordCount": result["wordCount"],
            "preview": result["preview"]
        }), 200
        
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": "The requested document could not be found on the server."
        }), 404
    except ValueError as val_err:
        return jsonify({
            "status": "error",
            "message": str(val_err)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"An error occurred during processing: {str(e)}"
        }), 500

@upload_bp.route('/preprocess', methods=['POST'])
def preprocess_pdf():
    """
    Triggers NLTK preprocessing on the cached raw text of the document.
    Saves JSON tokens to cache/ and returns token count metrics.
    """
    data = request.get_json()
    if not data or 'stored_filename' not in data:
        return jsonify({
            "status": "error",
            "message": "Missing 'stored_filename' in the request payload."
        }), 400
        
    stored_filename = data['stored_filename']
    
    try:
        from modules.nlp_processor import preprocess_text_cache
        result = preprocess_text_cache(stored_filename)
        
        return jsonify({
            "status": "success",
            "totalWords": result["totalWords"],
            "meaningfulWords": result["meaningfulWords"],
            "removedStopwords": result["removedStopwords"]
        }), 200
        
    except FileNotFoundError as fnf_err:
        return jsonify({
            "status": "error",
            "message": str(fnf_err)
        }), 404
    except ValueError as val_err:
        return jsonify({
            "status": "error",
            "message": str(val_err)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to preprocess document: {str(e)}"
        }), 500

@upload_bp.route('/concepts', methods=['POST'])
def discover_document_concepts():
    """
    Identifies the most frequent academic terms/concepts inside the document,
    ranks them by importance, caches results, and returns them to the client.
    """
    data = request.get_json()
    if not data or 'stored_filename' not in data:
        return jsonify({
            "status": "error",
            "message": "Missing 'stored_filename' in the request payload."
        }), 400
        
    stored_filename = data['stored_filename']
    
    try:
        from modules.concept_extractor import discover_concepts
        result = discover_concepts(stored_filename)
        
        return jsonify({
            "status": "success",
            "concepts": result["concepts"]
        }), 200
        
    except FileNotFoundError as fnf_err:
        return jsonify({
            "status": "error",
            "message": str(fnf_err)
        }), 404
    except ValueError as val_err:
        return jsonify({
            "status": "error",
            "message": str(val_err)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to discover concepts: {str(e)}"
        }), 500

@upload_bp.route('/summary', methods=['POST'])
def generate_document_summary():
    """
    Ranks document sentences based on concept density, generates an overview
    and key points, caches them, and returns them to the client.
    """
    data = request.get_json()
    if not data or 'stored_filename' not in data:
        return jsonify({
            "status": "error",
            "message": "Missing 'stored_filename' in the request payload."
        }), 400
        
    stored_filename = data['stored_filename']
    
    try:
        from modules.summary_generator import generate_summary
        result = generate_summary(stored_filename)
        
        return jsonify({
            "status": "success",
            "summary": result["summary"]
        }), 200
        
    except FileNotFoundError as fnf_err:
        return jsonify({
            "status": "error",
            "message": str(fnf_err)
        }), 404
    except ValueError as val_err:
        return jsonify({
            "status": "error",
            "message": str(val_err)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to generate summary: {str(e)}"
        }), 500





