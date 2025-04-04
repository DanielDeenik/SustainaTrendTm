"""
Direct Document Upload Module for SustainaTrend™

This standalone script serves as a direct entry point for the document upload features
without depending on the full application structure. It's optimized for Replit deployment.
"""

import os
import sys
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Configure secrets and environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_document_upload')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size

# Configure Replit proxy fix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import regulatory_ai_agent module
try:
    import regulatory_ai_agent
    logger.info("Successfully imported regulatory_ai_agent module")
    
    # Check if the module has the required functions
    has_get_frameworks = hasattr(regulatory_ai_agent, 'get_frameworks')
    has_is_rag_available = hasattr(regulatory_ai_agent, 'is_rag_available')
    logger.info(f"Module has required functions: get_frameworks={has_get_frameworks}, is_rag_available={has_is_rag_available}")
except ImportError as e:
    logger.error(f"Error importing regulatory_ai_agent: {e}")
    regulatory_ai_agent = None

# Simple mock functions if the real ones aren't available
def get_frameworks():
    if regulatory_ai_agent and hasattr(regulatory_ai_agent, 'get_frameworks'):
        return regulatory_ai_agent.get_frameworks()
    return {
        'CSRD': {'name': 'Corporate Sustainability Reporting Directive', 'regions': ['EU']},
        'ESRS': {'name': 'European Sustainability Reporting Standards', 'regions': ['EU']},
        'SFDR': {'name': 'Sustainable Finance Disclosure Regulation', 'regions': ['EU']},
        'TCFD': {'name': 'Task Force on Climate-related Financial Disclosures', 'regions': ['Global']}
    }

def is_rag_available():
    if regulatory_ai_agent and hasattr(regulatory_ai_agent, 'is_rag_available'):
        return regulatory_ai_agent.is_rag_available()
    
    # Check for Pinecone API key as a simple test
    return bool(os.environ.get('PINECONE_API_KEY'))

@app.route('/')
def index():
    """Redirect to document upload page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0;url=/document-upload">
        <title>Redirecting...</title>
    </head>
    <body>
        <p>Redirecting to document upload page...</p>
        <p><a href="/document-upload">Click here if not redirected</a></p>
    </body>
    </html>
    """

@app.route('/document-upload')
def document_upload():
    """Document Upload Page"""
    frameworks = get_frameworks()
    rag_system_available = is_rag_available()
    logger.info(f"Rendering document upload page with RAG available: {rag_system_available}")
    
    try:
        # First try the regular template
        return render_template('regulatory/document_upload.html',
                              frameworks=frameworks,
                              company='',
                              industry='',
                              is_rag_available=rag_system_available,
                              page_title="Document Upload & Analysis",
                              active_page="regulatory-ai")
    except Exception as e:
        logger.error(f"Error rendering regular template: {e}")
        try:
            # Try the standalone template
            return render_template('standalone_document_upload.html',
                                  frameworks=frameworks,
                                  is_rag_available=rag_system_available)
        except Exception as e2:
            logger.error(f"Error rendering standalone template: {e2}")
            # Fallback to basic HTML if template rendering fails
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Document Upload & Analysis</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <h1>Document Upload & Analysis</h1>
                    <div class="alert alert-info">
                        <p>This is a simplified fallback page for document uploads.</p>
                        <p>RAG system available: {rag_system_available}</p>
                    </div>
                    <form method="post" action="/api/upload" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="file" class="form-label">Select Document</label>
                            <input type="file" class="form-control" id="file" name="file">
                        </div>
                        <div class="mb-3">
                            <label for="framework" class="form-label">Regulatory Framework</label>
                            <select class="form-control" id="framework" name="framework">
                                {''.join(f'<option value="{k}">{v["name"]}</option>' for k, v in frameworks.items())}
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary">Upload & Analyze</button>
                    </form>
                </div>
            </body>
            </html>
            """

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        framework = request.form.get('framework', 'ESRS')
        
        return jsonify({
            "success": True,
            "message": "File uploaded successfully",
            "file_id": filename,
            "framework": framework,
            "redirect": f"/document-analysis?file_id={filename}&framework={framework}"
        })

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/document-analysis')
def document_analysis():
    """Document Analysis Page"""
    file_id = request.args.get('file_id', '')
    framework = request.args.get('framework', 'ESRS')
    
    if not file_id:
        return "File ID is required", 400
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document Analysis</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Document Analysis</h1>
            <div class="alert alert-success">
                <p>Your document (ID: {file_id}) is being analyzed using the {framework} framework.</p>
                <p>This is a simplified demonstration page. In the full application, this would show a real-time analysis.</p>
            </div>
            <a href="/document-upload" class="btn btn-primary">Back to Upload</a>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uuid
    # Get host and port from environment variables
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'
    
    logger.info(f"Starting direct document upload server on {host}:{port} with debug={debug}")
    app.run(host=host, port=port, debug=debug)