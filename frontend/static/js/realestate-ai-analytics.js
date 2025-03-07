/**
 * Real Estate Sustainability AI Analytics Module
 * Advanced AI-powered analytics and predictions for real estate sustainability
 */

// Create global namespace for the Real Estate AI module
window.realEstateAI = window.realEstateAI || {};

// Global variables for AI models and predictions
let aiModels = {
  predictive: null,
  sentiment: null,
  recommendation: null
};

// Configuration for AI models
const aiConfig = {
  predictionHorizon: 12, // months
  confidenceThreshold: 0.7,
  sentimentAnalysisEnabled: true,
  autoRecommendationEnabled: true,
  refreshInterval: 7 // days
};

/**
 * Initialize AI analytics module
 */
function initRealEstateAI() {
  console.log('Initializing Real Estate Sustainability AI Analytics...');
  
  // Load AI models
  loadAIModels();
  
  // Setup event listeners
  setupAIEventListeners();
  
  // Initialize the property portfolio analyzer
  initPropertyPortfolioAnalyzer();
  
  // Initialize the cross-filtering system
  initCrossFilteringSystem();
  
  // Initialize the sentiment analysis dashboard
  initSentimentAnalysisDashboard();
}

/**
 * Load AI models (simulated)
 */
function loadAIModels() {
  // In a production environment, this would load actual models
  // For now, we simulate model loading with a timeout
  
  // Show loading indicator
  document.getElementById('ai-status-indicator').classList.add('loading');
  document.getElementById('ai-status-text').textContent = 'Loading AI Models...';
  
  setTimeout(() => {
    // Simulate successful loading of models
    aiModels.predictive = {
      name: 'RealEstateTrend-GPT',
      version: '1.0.3',
      accuracy: 0.89,
      lastUpdated: new Date().toISOString()
    };
    
    aiModels.sentiment = {
      name: 'PropertySentiment-BERT',
      version: '2.1.0',
      accuracy: 0.92,
      lastUpdated: new Date().toISOString()
    };
    
    aiModels.recommendation = {
      name: 'SustainRecommender-XGBoost',
      version: '1.2.4',
      accuracy: 0.85,
      lastUpdated: new Date().toISOString()
    };
    
    // Update UI with model information
    document.getElementById('ai-status-indicator').classList.remove('loading');
    document.getElementById('ai-status-indicator').classList.add('active');
    document.getElementById('ai-status-text').textContent = 'AI Models Ready';
    
    // Update model info in UI
    updateModelInfoPanel();
    
    // Generate initial predictions
    generateAIPredictions();
  }, 1500);
}

/**
 * Update the model info panel with loaded model details
 */
function updateModelInfoPanel() {
  const modelInfoElement = document.getElementById('ai-model-info');
  if (!modelInfoElement) return;
  
  let html = '<div class="model-info-table">';
  
  for (const [key, model] of Object.entries(aiModels)) {
    if (!model) continue;
    
    html += `
      <div class="model-info-row">
        <div class="model-info-cell model-name">
          <strong>${model.name}</strong>
        </div>
        <div class="model-info-cell">
          <span class="model-badge">v${model.version}</span>
          <span class="model-accuracy">Acc: ${(model.accuracy * 100).toFixed(1)}%</span>
        </div>
      </div>
    `;
  }
  
  html += '</div>';
  modelInfoElement.innerHTML = html;
}

/**
 * Generate AI predictions for real estate sustainability trends
 */
function generateAIPredictions() {
  if (!aiModels.predictive) {
    console.warn('Predictive model not loaded. Cannot generate predictions.');
    return;
  }
  
  console.log('Generating AI predictions with horizon:', aiConfig.predictionHorizon, 'months');
  
  // Fetch current data to base predictions on
  fetchRealEstateTrendData()
    .then(data => {
      // Process data and generate predictions
      const predictions = generatePredictionsFromData(data);
      
      // Update UI with predictions
      updatePredictionCharts(predictions);
      
      // Generate insights from predictions
      const insights = generateInsightsFromPredictions(predictions);
      updateInsightsPanel(insights);
      
      // Show success message
      if (window.showNotification) {
        window.showNotification(
          'AI predictions successfully generated',
          'bi-graph-up-arrow',
          'success'
        );
      }
    })
    .catch(error => {
      console.error('Error generating AI predictions:', error);
      
      // Show error message
      if (window.showNotification) {
        window.showNotification(
          'Failed to generate AI predictions. Using fallback data.',
          'bi-exclamation-triangle',
          'warning'
        );
      }
      
      // Use fallback data
      const fallbackPredictions = generateFallbackPredictions();
      updatePredictionCharts(fallbackPredictions);
      
      const fallbackInsights = generateInsightsFromPredictions(fallbackPredictions);
      updateInsightsPanel(fallbackInsights);
    });
}

/**
 * Generate predictions from real estate trend data
 */
function generatePredictionsFromData(data) {
  // In a real implementation, this would use actual ML models
  // For now, we'll generate simulated predictions based on trend data if available
  
  const predictions = {
    energyEfficiency: [],
    carbonFootprint: [],
    greenFinancing: [],
    certifications: [],
    marketTrends: [],
    dates: []
  };
  
  // Get current date
  const now = new Date();
  
  // Initialize base values, either from data or defaults
  const baseValues = {
    energy_efficiency: 72,
    carbon_footprint: 65,
    green_financing: 78,
    certifications: 60,
    market_trends: 80
  };
  
  // Initialize growth rates for each category
  const growthRates = {
    energy_efficiency: 0.8,
    carbon_footprint: 1.2,
    green_financing: 0.6,
    certifications: 1.0,
    market_trends: 0.5
  };
  
  // If we have API data, use it to set actual base values and calculate better growth rates
  if (data && data.trends && Array.isArray(data.trends)) {
    // Log the trend data received
    console.log('Using trend data for generating predictions:', data);
    
    // Extract the latest values and calculate trend patterns
    data.trends.forEach(trend => {
      if (trend.category && trend.values && Array.isArray(trend.values)) {
        // Get the latest value as our base value
        const latestValue = trend.values[trend.values.length - 1];
        baseValues[trend.category] = latestValue;
        
        // Calculate growth rate from historical data if available
        if (trend.historical_values && trend.historical_values.length >= 2) {
          const first = trend.historical_values[0];
          const last = trend.historical_values[trend.historical_values.length - 1];
          
          // Calculate monthly growth rate
          if (first > 0 && trend.historical_values.length > 1) {
            const totalGrowth = last / first;
            const months = trend.historical_values.length - 1;
            const monthlyRate = Math.pow(totalGrowth, 1/months) - 1;
            
            // Apply some smoothing to avoid extreme projections
            growthRates[trend.category] = monthlyRate * 100 * 0.8; // Convert to percentage and dampen
          }
        }
      }
    });
    
    // If API provided dates, use them as the starting point for future predictions
    if (data.dates && Array.isArray(data.dates) && data.dates.length > 0) {
      const lastDateStr = data.dates[data.dates.length - 1];
      const lastDate = new Date(lastDateStr);
      if (!isNaN(lastDate.getTime())) {
        // Valid date, use it instead of current date
        now.setTime(lastDate.getTime());
      }
    }
  } else {
    console.log('No trend data available, using default values for predictions');
  }
  
  // Generate monthly predictions for the prediction horizon
  for (let i = 0; i < aiConfig.predictionHorizon; i++) {
    const date = new Date(now);
    date.setMonth(now.getMonth() + i + 1);
    
    // Format date as YYYY-MM
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const formattedDate = `${date.getFullYear()}-${month}`;
    predictions.dates.push(formattedDate);
    
    // Calculate confidence decay based on how far into the future we're predicting
    const confidenceDecay = i * 0.015; // more decay for further predictions
    
    // Generate prediction for each category with appropriate growth rates and volatility
    predictions.energyEfficiency.push({
      value: baseValues.energy_efficiency + (i * growthRates.energy_efficiency) + (Math.random() * 2 - 1),
      confidence: 0.92 - confidenceDecay
    });
    
    predictions.carbonFootprint.push({
      value: baseValues.carbon_footprint + (i * growthRates.carbon_footprint) + (Math.random() * 3 - 1.5),
      confidence: 0.87 - confidenceDecay
    });
    
    predictions.greenFinancing.push({
      value: baseValues.green_financing + (i * growthRates.green_financing) + (Math.random() * 1.5 - 0.75),
      confidence: 0.90 - confidenceDecay
    });
    
    predictions.certifications.push({
      value: baseValues.certifications + (i * growthRates.certifications) + (Math.random() * 2.5 - 1.25),
      confidence: 0.84 - confidenceDecay
    });
    
    predictions.marketTrends.push({
      value: baseValues.market_trends + (i * growthRates.market_trends) + (Math.random() * 2.2 - 1.1),
      confidence: 0.82 - confidenceDecay
    });
  }
  
  return predictions;
}

/**
 * Generate fallback predictions when real data is unavailable
 */
function generateFallbackPredictions() {
  return generatePredictionsFromData(null); // Use the same function with null data
}

/**
 * Fetch real estate trend data from the server
 * Returns a promise with the trend data
 */
function fetchRealEstateTrendData() {
  // Build URL with parameters
  let url = '/api/realestate-trends';
  
  // Return a promise that resolves with the fetched data
  return new Promise((resolve, reject) => {
    console.log('Fetching real estate trend data for AI analytics...');
    
    // Fetch data from API
    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error(`API request failed: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Successfully fetched trend data for AI analytics');
        resolve(data);
      })
      .catch(error => {
        console.error('Error fetching real estate trend data for AI analytics:', error);
        
        // Generate mock data as fallback
        const mockData = {
          trends: [
            { 
              category: 'energy_efficiency', 
              values: [68, 70, 71, 71.5, 72],
              historical_values: [65, 66, 67, 68, 69, 70, 71, 71.5, 72]
            },
            { 
              category: 'carbon_footprint', 
              values: [58, 60, 61, 63, 65],
              historical_values: [50, 52, 54, 56, 58, 60, 61, 63, 65]
            },
            { 
              category: 'green_financing', 
              values: [72, 73, 75, 76, 78],
              historical_values: [68, 69, 70, 71, 72, 73, 75, 76, 78]
            },
            { 
              category: 'certifications', 
              values: [55, 56, 57, 59, 60],
              historical_values: [48, 50, 52, 53, 55, 56, 57, 59, 60]
            },
            { 
              category: 'market_trends', 
              values: [76, 77, 78, 79, 80],
              historical_values: [72, 73, 74, 75, 76, 77, 78, 79, 80]
            }
          ],
          dates: ['2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12', '2025-01', '2025-02', '2025-03']
        };
        
        if (window.showNotification) {
          window.showNotification(
            'Using sample data for AI predictions',
            'bi-robot',
            'warning'
          );
        }
        
        resolve(mockData);
      });
  });
}

/**
 * Update prediction charts with AI-generated data
 */
function updatePredictionCharts(predictions) {
  const aiPredictionCanvas = document.getElementById('aiPredictionChart');
  if (!aiPredictionCanvas) return;
  
  // Prepare datasets for the chart
  const datasets = [
    {
      label: 'Energy Efficiency',
      data: predictions.energyEfficiency.map(p => p.value),
      borderColor: '#2E7D32',
      backgroundColor: 'rgba(46, 125, 50, 0.1)',
      tension: 0.4
    },
    {
      label: 'Carbon Footprint',
      data: predictions.carbonFootprint.map(p => p.value),
      borderColor: '#4CAF50',
      backgroundColor: 'rgba(76, 175, 80, 0.1)',
      tension: 0.4
    },
    {
      label: 'Green Financing',
      data: predictions.greenFinancing.map(p => p.value),
      borderColor: '#9c27b0',
      backgroundColor: 'rgba(156, 39, 176, 0.1)',
      tension: 0.4
    },
    {
      label: 'Certifications',
      data: predictions.certifications.map(p => p.value),
      borderColor: '#f1c40f',
      backgroundColor: 'rgba(241, 196, 15, 0.1)',
      tension: 0.4
    },
    {
      label: 'Market Trends',
      data: predictions.marketTrends.map(p => p.value),
      borderColor: '#e67e22',
      backgroundColor: 'rgba(230, 126, 34, 0.1)',
      tension: 0.4
    }
  ];
  
  // Create or update chart
  if (window.aiPredictionChart) {
    window.aiPredictionChart.data.labels = predictions.dates;
    window.aiPredictionChart.data.datasets = datasets;
    window.aiPredictionChart.update();
  } else {
    window.aiPredictionChart = new Chart(aiPredictionCanvas, {
      type: 'line',
      data: {
        labels: predictions.dates,
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'AI-Powered Sustainability Predictions',
            font: {
              size: 16
            }
          },
          legend: {
            position: 'top'
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              afterLabel: function(context) {
                // Add confidence level to tooltip
                const datasetIndex = context.datasetIndex;
                const dataIndex = context.dataIndex;
                const categoryKey = Object.keys(predictions)[datasetIndex];
                const confidence = predictions[categoryKey][dataIndex].confidence;
                return `Confidence: ${(confidence * 100).toFixed(1)}%`;
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Month'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Sustainability Score'
            },
            suggestedMin: 50,
            suggestedMax: 100
          }
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false
        }
      }
    });
  }
  
  // Update confidence indicators
  updateConfidenceIndicators(predictions);
}

/**
 * Update confidence indicators for predictions
 */
function updateConfidenceIndicators(predictions) {
  const confidenceElement = document.getElementById('prediction-confidence');
  if (!confidenceElement) return;
  
  // Calculate average confidence across all categories
  let totalConfidence = 0;
  let totalPredictions = 0;
  
  Object.keys(predictions).forEach(key => {
    if (key !== 'dates' && Array.isArray(predictions[key])) {
      predictions[key].forEach(prediction => {
        totalConfidence += prediction.confidence;
        totalPredictions++;
      });
    }
  });
  
  const avgConfidence = totalConfidence / totalPredictions;
  const confidencePercentage = (avgConfidence * 100).toFixed(1);
  
  // Update UI
  confidenceElement.innerHTML = `
    <div class="confidence-indicator ${getConfidenceClass(avgConfidence)}">
      <div class="confidence-value">${confidencePercentage}%</div>
      <div class="confidence-label">Average Confidence</div>
    </div>
  `;
}

/**
 * Get CSS class based on confidence level
 */
function getConfidenceClass(confidence) {
  if (confidence >= 0.8) return 'high';
  if (confidence >= 0.6) return 'medium';
  return 'low';
}

/**
 * Generate insights from AI predictions
 */
function generateInsightsFromPredictions(predictions) {
  // Extract trends from predictions
  const trends = {
    energyEfficiency: calculateTrend(predictions.energyEfficiency.map(p => p.value)),
    carbonFootprint: calculateTrend(predictions.carbonFootprint.map(p => p.value)),
    greenFinancing: calculateTrend(predictions.greenFinancing.map(p => p.value)),
    certifications: calculateTrend(predictions.certifications.map(p => p.value)),
    marketTrends: calculateTrend(predictions.marketTrends.map(p => p.value))
  };
  
  // Generate insights based on trends
  const insights = [
    {
      category: 'Energy Efficiency',
      trend: trends.energyEfficiency,
      insight: `Energy efficiency scores are projected to ${trends.energyEfficiency > 0 ? 'improve' : 'decline'} by ${Math.abs(trends.energyEfficiency * 100).toFixed(1)}% over the next ${aiConfig.predictionHorizon} months.`,
      recommendation: trends.energyEfficiency > 0 
        ? 'Continue investment in building insulation and smart energy management systems.'
        : 'Increase focus on energy efficiency upgrades and implement regular energy audits.',
      impact: trends.energyEfficiency > 0.5 ? 'high' : trends.energyEfficiency > 0 ? 'medium' : 'critical'
    },
    {
      category: 'Carbon Footprint',
      trend: trends.carbonFootprint,
      insight: `Carbon footprint is expected to ${trends.carbonFootprint > 0 ? 'improve' : 'worsen'} by ${Math.abs(trends.carbonFootprint * 100).toFixed(1)}% over the forecast period.`,
      recommendation: trends.carbonFootprint > 0
        ? 'Expand renewable energy adoption and evaluate carbon offset programs.'
        : 'Urgently implement carbon reduction strategies and increase renewable energy investment.',
      impact: trends.carbonFootprint > 0.5 ? 'high' : trends.carbonFootprint > 0 ? 'medium' : 'critical'
    },
    {
      category: 'Green Financing',
      trend: trends.greenFinancing,
      insight: `Green financing opportunities are projected to ${trends.greenFinancing > 0 ? 'increase' : 'decrease'} by ${Math.abs(trends.greenFinancing * 100).toFixed(1)}% over the next year.`,
      recommendation: trends.greenFinancing > 0
        ? 'Prepare portfolio for increased green financing eligibility and sustainability-linked loans.'
        : 'Enhance ESG reporting and develop strong green improvement plans to attract financing.',
      impact: trends.greenFinancing > 0.5 ? 'high' : trends.greenFinancing > 0 ? 'medium' : 'critical'
    },
    {
      category: 'Certifications',
      trend: trends.certifications,
      insight: `Sustainability certifications are predicted to ${trends.certifications > 0 ? 'grow' : 'decline'} by ${Math.abs(trends.certifications * 100).toFixed(1)}% in the coming months.`,
      recommendation: trends.certifications > 0
        ? 'Prepare for certification renewal processes and consider upgrading to higher certification levels.'
        : 'Develop a strategic plan to achieve and maintain key sustainability certifications.',
      impact: trends.certifications > 0.5 ? 'high' : trends.certifications > 0 ? 'medium' : 'critical'
    },
    {
      category: 'Market Trends',
      trend: trends.marketTrends,
      insight: `Market valuation premium for sustainable properties is forecasted to ${trends.marketTrends > 0 ? 'increase' : 'decrease'} by ${Math.abs(trends.marketTrends * 100).toFixed(1)}%.`,
      recommendation: trends.marketTrends > 0
        ? 'Position portfolio marketing to emphasize sustainability features and benefits.'
        : 'Focus on differentiating properties through sustainability innovations and tenant engagement.',
      impact: trends.marketTrends > 0.5 ? 'high' : trends.marketTrends > 0 ? 'medium' : 'critical'
    }
  ];
  
  return insights;
}

/**
 * Calculate trend percentage from array of values
 */
function calculateTrend(values) {
  if (!values || values.length < 2) return 0;
  
  const first = values[0];
  const last = values[values.length - 1];
  
  return (last - first) / first;
}

/**
 * Update insights panel with AI-generated insights
 */
function updateInsightsPanel(insights) {
  const insightsElement = document.getElementById('ai-insights');
  if (!insightsElement) return;
  
  let html = '';
  
  insights.forEach(insight => {
    html += `
      <div class="insight-card ${insight.impact}">
        <div class="insight-header">
          <h4>${insight.category}</h4>
          <span class="trend-indicator ${insight.trend > 0 ? 'positive' : 'negative'}">
            ${insight.trend > 0 ? '↑' : '↓'} ${Math.abs(insight.trend * 100).toFixed(1)}%
          </span>
        </div>
        <div class="insight-body">
          <p>${insight.insight}</p>
          <div class="recommendation">
            <strong>Recommendation:</strong> ${insight.recommendation}
          </div>
        </div>
      </div>
    `;
  });
  
  insightsElement.innerHTML = html;
}

/**
 * Setup event listeners for AI interactions
 */
function setupAIEventListeners() {
  // Refresh predictions button
  const refreshBtn = document.getElementById('refresh-predictions');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', function() {
      generateAIPredictions();
    });
  }
  
  // Show AI model info button
  const modelInfoBtn = document.getElementById('show-model-info');
  if (modelInfoBtn) {
    modelInfoBtn.addEventListener('click', function() {
      // Toggle AI model info panel
      const modelInfoPanel = document.getElementById('ai-model-info-panel');
      if (modelInfoPanel) {
        modelInfoPanel.classList.toggle('show');
      }
    });
  }
  
  // AI settings button
  const settingsBtn = document.getElementById('ai-settings');
  if (settingsBtn) {
    settingsBtn.addEventListener('click', function() {
      // Show AI settings modal
      showAISettingsModal();
    });
  }
}

/**
 * Show AI settings modal
 */
function showAISettingsModal() {
  // Create modal if it doesn't exist
  let modal = document.getElementById('ai-settings-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'ai-settings-modal';
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>AI Analytics Settings</h3>
          <button class="close-modal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="setting-group">
            <label>Prediction Horizon</label>
            <select id="prediction-horizon">
              <option value="3" ${aiConfig.predictionHorizon === 3 ? 'selected' : ''}>3 months</option>
              <option value="6" ${aiConfig.predictionHorizon === 6 ? 'selected' : ''}>6 months</option>
              <option value="12" ${aiConfig.predictionHorizon === 12 ? 'selected' : ''}>12 months</option>
              <option value="24" ${aiConfig.predictionHorizon === 24 ? 'selected' : ''}>24 months</option>
            </select>
          </div>
          <div class="setting-group">
            <label>Minimum Confidence Threshold</label>
            <input type="range" id="confidence-threshold" min="0.5" max="0.95" step="0.05" value="${aiConfig.confidenceThreshold}">
            <div class="range-value">${(aiConfig.confidenceThreshold * 100).toFixed(0)}%</div>
          </div>
          <div class="setting-group">
            <label>Features</label>
            <div class="checkbox-group">
              <label>
                <input type="checkbox" id="sentiment-analysis" ${aiConfig.sentimentAnalysisEnabled ? 'checked' : ''}>
                Enable Sentiment Analysis
              </label>
            </div>
            <div class="checkbox-group">
              <label>
                <input type="checkbox" id="auto-recommendations" ${aiConfig.autoRecommendationEnabled ? 'checked' : ''}>
                Enable Automatic Recommendations
              </label>
            </div>
          </div>
          <div class="setting-group">
            <label>Auto-refresh Interval</label>
            <select id="refresh-interval">
              <option value="1" ${aiConfig.refreshInterval === 1 ? 'selected' : ''}>Daily</option>
              <option value="7" ${aiConfig.refreshInterval === 7 ? 'selected' : ''}>Weekly</option>
              <option value="30" ${aiConfig.refreshInterval === 30 ? 'selected' : ''}>Monthly</option>
              <option value="0">Manual only</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline-secondary" id="reset-ai-settings">Reset to Defaults</button>
          <button class="btn btn-primary" id="save-ai-settings">Save Settings</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    
    // Add event listeners
    const closeBtn = modal.querySelector('.close-modal');
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('show');
    });
    
    const saveBtn = modal.querySelector('#save-ai-settings');
    saveBtn.addEventListener('click', () => {
      saveAISettings();
      modal.classList.remove('show');
    });
    
    const resetBtn = modal.querySelector('#reset-ai-settings');
    resetBtn.addEventListener('click', () => {
      resetAISettings();
    });
    
    const confidenceThreshold = modal.querySelector('#confidence-threshold');
    confidenceThreshold.addEventListener('input', (e) => {
      const value = parseFloat(e.target.value);
      modal.querySelector('.range-value').textContent = `${(value * 100).toFixed(0)}%`;
    });
  }
  
  // Show modal
  modal.classList.add('show');
}

/**
 * Save AI settings from modal
 */
function saveAISettings() {
  const predictionHorizon = parseInt(document.getElementById('prediction-horizon').value);
  const confidenceThreshold = parseFloat(document.getElementById('confidence-threshold').value);
  const sentimentAnalysis = document.getElementById('sentiment-analysis').checked;
  const autoRecommendations = document.getElementById('auto-recommendations').checked;
  const refreshInterval = parseInt(document.getElementById('refresh-interval').value);
  
  // Update config
  aiConfig.predictionHorizon = predictionHorizon;
  aiConfig.confidenceThreshold = confidenceThreshold;
  aiConfig.sentimentAnalysisEnabled = sentimentAnalysis;
  aiConfig.autoRecommendationEnabled = autoRecommendations;
  aiConfig.refreshInterval = refreshInterval;
  
  // Regenerate predictions with new settings
  generateAIPredictions();
  
  // Show notification
  if (window.showNotification) {
    window.showNotification(
      'AI settings updated successfully',
      'bi-gear-fill',
      'success'
    );
  }
}

/**
 * Reset AI settings to defaults
 */
function resetAISettings() {
  // Reset to defaults
  document.getElementById('prediction-horizon').value = "12";
  document.getElementById('confidence-threshold').value = "0.7";
  document.querySelector('.range-value').textContent = "70%";
  document.getElementById('sentiment-analysis').checked = true;
  document.getElementById('auto-recommendations').checked = true;
  document.getElementById('refresh-interval').value = "7";
}

/**
 * Initialize property portfolio analyzer
 */
function initPropertyPortfolioAnalyzer() {
  // This would be implemented in production
  console.log('Property Portfolio Analyzer initialized');
}

/**
 * Initialize cross-filtering system for advanced analytics
 */
function initCrossFilteringSystem() {
  // This would be implemented in production
  console.log('Cross-Filtering System initialized');
}

/**
 * Initialize sentiment analysis dashboard
 */
function initSentimentAnalysisDashboard() {
  if (!aiConfig.sentimentAnalysisEnabled) {
    console.log('Sentiment analysis disabled in configuration');
    return;
  }
  
  // This would be implemented in production
  console.log('Sentiment Analysis Dashboard initialized');
}

// Export functionality for module integration
window.realEstateAI = {
  init: initRealEstateAI,
  generatePredictions: generateAIPredictions,
  showSettings: showAISettingsModal
};