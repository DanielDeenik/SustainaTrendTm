from flask import Flask, request, jsonify
from services.ai_analysis import analyze_sustainability
from services.monetization import monetize_data
from services.strategy_ai import apa_ai_consultant

app = Flask(__name__)

@app.route('/api/sustainability-analysis', methods=['POST'])
def sustainability_analysis():
    data = request.json
    company_name = data.get('company_name', '')
    industry = data.get('industry', '')
    return jsonify(analyze_sustainability(company_name, industry))

@app.route('/api/monetization-strategy', methods=['POST'])
def monetization_strategy():
    data = request.json
    company_name = data.get('company_name', '')
    return jsonify(monetize_data(company_name))

@app.route('/api/apa-strategy', methods=['POST'])
def apa_strategy():
    data = request.json
    company_name = data.get('company_name', '')
    return jsonify(apa_ai_consultant(company_name))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
