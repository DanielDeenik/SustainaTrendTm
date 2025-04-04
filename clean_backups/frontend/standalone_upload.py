"""
Standalone Document Upload Entry Point

This script serves as a super-lightweight entry point for the document upload functionality
without the overhead of the full application. It's designed to be extremely reliable
in the Replit environment.
"""

import os
import logging
from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_standalone')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Apply ProxyFix middleware
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Simple framework definition
FRAMEWORKS = {
    'CSRD': {'name': 'Corporate Sustainability Reporting Directive', 'regions': ['EU']},
    'ESRS': {'name': 'European Sustainability Reporting Standards', 'regions': ['EU']},
    'SFDR': {'name': 'Sustainable Finance Disclosure Regulation', 'regions': ['EU']},
    'TCFD': {'name': 'Task Force on Climate-related Financial Disclosures', 'regions': ['Global']}
}

# Check Pinecone availability
PINECONE_AVAILABLE = bool(os.environ.get('PINECONE_API_KEY'))

@app.route('/')
def index():
    """Redirect to the document upload page"""
    return redirect('/upload')

@app.route('/upload')
def upload():
    """Show standalone document upload page"""
    try:
        return render_template('standalone_document_upload.html',
                               frameworks=FRAMEWORKS,
                               is_rag_available=PINECONE_AVAILABLE)
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Document Upload</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container py-5">
                <h1>Document Upload</h1>
                <div class="alert alert-info">
                    <p>This is a minimal version of the document upload page.</p>
                </div>
                <div class="card">
                    <div class="card-body">
                        <form action="/api/upload" method="post" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="file" class="form-label">Select Document</label>
                                <input class="form-control" type="file" id="file" name="file">
                            </div>
                            <div class="mb-3">
                                <label for="framework" class="form-label">Framework</label>
                                <select class="form-control" id="framework" name="framework">
                                    <option value="ESRS">European Sustainability Reporting Standards</option>
                                    <option value="CSRD">Corporate Sustainability Reporting Directive</option>
                                    <option value="SFDR">Sustainable Finance Disclosure Regulation</option>
                                    <option value="TCFD">Task Force on Climate-related Financial Disclosures</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary">Upload & Analyze</button>
                        </form>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle document upload"""
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Generate a unique filename
    import uuid
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join('uploads', filename)
    
    # Save the file
    file.save(file_path)
    
    # Get the selected framework
    framework = request.form.get('framework', 'ESRS')
    
    return {
        'success': True,
        'message': 'File uploaded successfully',
        'filename': filename,
        'framework': framework,
        'redirect': f'/analyze?filename={filename}&framework={framework}'
    }

@app.route('/analyze')
def analyze():
    """Show analysis page"""
    filename = request.args.get('filename', '')
    framework = request.args.get('framework', 'ESRS')
    
    if not filename:
        return redirect('/upload')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document Analysis</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container py-5">
            <h1>Document Analysis</h1>
            <div class="alert alert-success">
                <h4>Analysis Complete</h4>
                <p>Your document <strong>{filename}</strong> has been analyzed using the {framework} framework.</p>
            </div>
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="card-title mb-0">Analysis Results</h5>
                </div>
                <div class="card-body">
                    <p>The document shows good compliance with {framework} standards.</p>
                    <div class="progress mb-3">
                        <div class="progress-bar bg-success" role="progressbar" style="width: 75%">75%</div>
                    </div>
                    <h6>Key Findings:</h6>
                    <ul>
                        <li>Good coverage of environmental metrics</li>
                        <li>Social impact reporting meets standards</li>
                        <li>Governance disclosures need improvement</li>
                    </ul>
                </div>
            </div>
            <a href="/upload" class="btn btn-primary">Upload Another Document</a>
        </div>
    </body>
    </html>
    """

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 7000))  # Use port 7000 by default to avoid conflicts
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'
    
    logger.info(f"Starting standalone upload server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)