"""
Quick diagnostic script to test route rendering
"""

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def test_index():
    """Test index route"""
    return "Route test working properly"

@app.route('/test-dashboard')
def test_dashboard():
    """Test dashboard rendering"""
    try:
        return render_template('regulatory/dashboard_refactored.html',
            active_nav='regulatory-ai-refactored',
            page_title="Test Regulatory AI Dashboard",
            stats={
                'documents_count': 12,
                'document_growth': '24%',
                'frameworks_count': 7,
                'recent_framework': 'EU CSRD',
                'avg_compliance': '74%',
                'analysis_count': 48,
                'analysis_growth': '18%'
            },
            recent_documents=[],
            recent_activity=[]
        )
    except Exception as e:
        return f"Error rendering template: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)