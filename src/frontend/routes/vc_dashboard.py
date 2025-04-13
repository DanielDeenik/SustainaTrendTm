from flask import Blueprint, render_template, jsonify, request, current_app
import logging

logger = logging.getLogger(__name__)

vc_dashboard_bp = Blueprint('vc_dashboard', __name__)

@vc_dashboard_bp.route('/vc-dashboard')
def vc_dashboard():
    """
    Render the VC dashboard with portfolio data, metrics, and company information.
    """
    try:
        # For demo purposes, we'll use mock data
        portfolio_data = {
            "total_companies": 35,
            "growth_rate": 15,
            "avg_esg_score": 82.5,
            "esg_score_percentage": 82,
            "carbon_intensity": 125.4,
            "carbon_reduction": 12.3,
            "top_sector": "Clean Energy",
            "sector_market_share": 28.5,
            "companies": [
                {
                    "name": "EcoTech Solutions",
                    "ticker": "ECTS",
                    "logo_url": "/static/img/company-logos/default.png",
                    "sector": "Clean Energy",
                    "esg_score": 85,
                    "esg_score_percentage": 85,
                    "carbon_intensity": 45.2,
                    "lifecycle_phase": "Growth",
                    "supply_chain_risk": "Low"
                },
                {
                    "name": "GreenMobile",
                    "ticker": "GRMB",
                    "logo_url": "/static/img/company-logos/default.png",
                    "sector": "Transportation",
                    "esg_score": 78,
                    "esg_score_percentage": 78,
                    "carbon_intensity": 62.8,
                    "lifecycle_phase": "Early",
                    "supply_chain_risk": "Medium"
                }
            ],
            "pagination": {
                "start": 1,
                "end": 2,
                "total": 2
            }
        }
        
        funds = [
            {"id": "1", "name": "Sustainability Fund I", "aum": "$50M", "portfolio_count": 12},
            {"id": "2", "name": "Green Tech Fund II", "aum": "$75M", "portfolio_count": 8},
            {"id": "3", "name": "Climate Innovation Fund", "aum": "$100M", "portfolio_count": 15}
        ]
        
        gpt_score = 85
        gpt_metrics = {
            "market_fit": 90,
            "sustainability_impact": 85,
            "financial_potential": 80
        }
        
        # Render the template with all the data
        return render_template(
            'vc_dashboard.html',
            user={"name": "Demo User"},
            portfolio=portfolio_data,
            funds=funds,
            selected_fund=funds[0],
            gpt_score=gpt_score,
            gpt_metrics=gpt_metrics
        )
    
    except Exception as e:
        logger.error(f"Error rendering VC dashboard: {str(e)}")
        return render_template('error.html', message="An error occurred while loading the dashboard"), 500

@vc_dashboard_bp.route('/api/vc-dashboard/upload-report', methods=['POST'])
def upload_report():
    """
    Handle PDF report uploads for analysis.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # For demo purposes, we'll just return a success message
        return jsonify({
            "success": True,
            "message": "Report uploaded successfully",
            "analysis": {
                "esg_score": 82,
                "carbon_intensity": 1.2,
                "sustainability_metrics": {
                    "environmental": 85,
                    "social": 80,
                    "governance": 81
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Error uploading report: {str(e)}")
        return jsonify({"error": "An error occurred while processing the report"}), 500

@vc_dashboard_bp.route('/api/vc-dashboard/generate-strategy', methods=['POST'])
def generate_strategy():
    """
    Generate a GPT-powered investment strategy based on portfolio data.
    """
    try:
        # For demo purposes, we'll return mock data
        return jsonify({
            "success": True,
            "strategy": {
                "summary": "Based on current portfolio analysis, we recommend focusing on renewable energy storage solutions and sustainable agriculture technologies.",
                "recommendations": [
                    "Increase allocation to energy storage startups by 15%",
                    "Reduce exposure to traditional manufacturing by 10%",
                    "Explore 3-5 new opportunities in sustainable agriculture",
                    "Consider divesting from companies with high carbon intensity"
                ],
                "metrics": {
                    "market_fit": 90,
                    "sustainability_impact": 85,
                    "financial_potential": 80,
                    "overall_score": 85
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Error generating strategy: {str(e)}")
        return jsonify({"error": "An error occurred while generating the strategy"}), 500 