/**
 * SustainaTrend™ Data-Based Storytelling Integration
 * Integrates sustainability data with AI-driven storytelling using visualization components
 */

// Initialize the data storytelling module when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize storytelling components
  initStorytellingComponents();
  
  // Set up form submission event
  setupStoryFormSubmission();
  
  // Initialize visualization components
  initVisualizationComponents();
});

/**
 * Initialize storytelling UI components
 */
function initStorytellingComponents() {
  // Initialize tooltips
  if (typeof initTooltips === 'function') {
    initTooltips();
  }
  
  // Initialize card animations
  if (typeof initCardAnimation === 'function') {
    initCardAnimation();
  }
  
  // Initialize export functionality
  initExportFunctionality();
}

/**
 * Setup the story generation form submission
 */
function setupStoryFormSubmission() {
  const storyForm = document.getElementById('storyGenerationForm');
  
  if (!storyForm) return;
  
  storyForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Show loading indicator
    if (typeof showLoading === 'function') {
      showLoading(true, 'storyContainer');
    }
    
    // Get form data
    const formData = new FormData(storyForm);
    const company = formData.get('company_name');
    const industry = formData.get('industry');
    
    // Get selected sections
    const includeSections = [];
    document.querySelectorAll('input[name="include_sections"]:checked').forEach(checkbox => {
      includeSections.push(checkbox.value);
    });
    
    // Prepare request data
    const requestData = {
      company_name: company,
      industry: industry,
      include_sections: includeSections
    };
    
    // Make API request to generate story
    fetch('/api/storytelling/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      // Update UI with story data
      updateStoryUI(data);
      
      // Hide loading indicator
      if (typeof showLoading === 'function') {
        showLoading(false, 'storyContainer');
      }
      
      // Show success notification
      if (typeof showNotification === 'function') {
        showNotification('Story generated successfully!', 'success');
      }
    })
    .catch(error => {
      console.error('Error generating story:', error);
      
      // Hide loading indicator
      if (typeof showLoading === 'function') {
        showLoading(false, 'storyContainer');
      }
      
      // Show error notification
      if (typeof showNotification === 'function') {
        showNotification('Error generating story. Please try again.', 'error');
      }
    });
  });
}

/**
 * Update the UI with generated story data
 * @param {Object} storyData - Generated story data
 */
function updateStoryUI(storyData) {
  // Update company profile section
  updateCompanyProfile(storyData);
  
  // Update industry context section
  updateIndustryContext(storyData);
  
  // Update recommendations section if available
  if (storyData.Actionable_Recommendations) {
    updateRecommendations(storyData.Actionable_Recommendations);
  }
  
  // Update monetization section if available
  if (storyData.Monetization_Model) {
    updateMonetizationModel(storyData.Monetization_Model);
  }
  
  // Update metrics section if available
  if (storyData.Performance_Metrics) {
    updatePerformanceMetrics(storyData.Performance_Metrics);
  }
  
  // Update financial impact section if available
  if (storyData.Estimated_Financial_Impact) {
    updateFinancialImpact(storyData.Estimated_Financial_Impact);
  }
  
  // Scroll to the story container
  const storyContainer = document.getElementById('storyContainer');
  if (storyContainer) {
    storyContainer.scrollIntoView({ behavior: 'smooth' });
  }
}

/**
 * Update company profile section with story data
 * @param {Object} storyData - Story data
 */
function updateCompanyProfile(storyData) {
  const companyNameElement = document.querySelector('.company-profile h2');
  const industryElement = document.querySelector('.company-profile .badge:first-child');
  const strategyElement = document.querySelector('.company-profile .lead');
  
  if (companyNameElement && storyData.Company) {
    companyNameElement.textContent = storyData.Company;
  }
  
  if (industryElement && storyData.Industry) {
    industryElement.textContent = storyData.Industry;
  }
  
  if (strategyElement && storyData.Sustainability_Strategy) {
    strategyElement.textContent = storyData.Sustainability_Strategy;
  }
}

/**
 * Update industry context section with story data
 * @param {Object} storyData - Story data
 */
function updateIndustryContext(storyData) {
  const contextElement = document.querySelector('.industry-context p');
  
  if (contextElement && storyData.Industry_Context) {
    contextElement.textContent = storyData.Industry_Context;
  }
}

/**
 * Update recommendations section with story data
 * @param {Array} recommendations - Recommendations data
 */
function updateRecommendations(recommendations) {
  const recommendationsContainer = document.getElementById('recommendationsContainer');
  
  if (!recommendationsContainer || !recommendations || !recommendations.length) return;
  
  // Clear existing recommendations
  recommendationsContainer.innerHTML = '';
  
  // Add new recommendations
  recommendations.forEach((recommendation, index) => {
    const recommendationItem = document.createElement('div');
    recommendationItem.className = 'recommendation-item';
    
    const content = typeof recommendation === 'string' 
      ? recommendation 
      : (recommendation.text || recommendation.recommendation || '');
    
    recommendationItem.innerHTML = `
      <div class="d-flex">
        <div class="me-3">
          <span class="badge bg-primary rounded-circle p-2">${index + 1}</span>
        </div>
        <div>
          <p class="mb-0">${content}</p>
        </div>
      </div>
    `;
    
    recommendationsContainer.appendChild(recommendationItem);
  });
}

/**
 * Update monetization model section with story data
 * @param {Array} monetizationModels - Monetization models data
 */
function updateMonetizationModel(monetizationModels) {
  const monetizationContainer = document.getElementById('monetizationContainer');
  
  if (!monetizationContainer || !monetizationModels || !monetizationModels.length) return;
  
  // Clear existing models
  monetizationContainer.innerHTML = '';
  
  // Add new monetization models
  monetizationModels.forEach((model, index) => {
    const modelItem = document.createElement('div');
    modelItem.className = 'monetization-model';
    
    const title = typeof model === 'string' 
      ? `Opportunity ${index + 1}` 
      : (model.title || model.name || `Opportunity ${index + 1}`);
    
    const description = typeof model === 'string' 
      ? model 
      : (model.description || model.text || '');
    
    modelItem.innerHTML = `
      <h5>${title}</h5>
      <p>${description}</p>
    `;
    
    monetizationContainer.appendChild(modelItem);
  });
}

/**
 * Update performance metrics section with story data
 * @param {Array} metrics - Performance metrics data
 */
function updatePerformanceMetrics(metrics) {
  const metricsContainer = document.getElementById('metricsContainer');
  
  if (!metricsContainer || !metrics || !metrics.length) return;
  
  // Clear existing metrics
  metricsContainer.innerHTML = '';
  
  // Create row for metrics
  const row = document.createElement('div');
  row.className = 'row';
  
  // Add new metrics
  metrics.forEach((metric, index) => {
    const metricText = typeof metric === 'string' ? metric : (metric.name || '');
    const metricValue = typeof metric === 'string' ? '' : (metric.value || '');
    const metricUnit = typeof metric === 'string' ? '' : (metric.unit || '');
    
    const col = document.createElement('div');
    col.className = 'col-md-4 mb-3';
    col.innerHTML = `
      <div class="card h-100">
        <div class="card-body text-center">
          ${metricValue ? `<div class="metric-value">${metricValue}${metricUnit}</div>` : ''}
          <p class="metric-label">${metricText}</p>
        </div>
      </div>
    `;
    
    row.appendChild(col);
  });
  
  metricsContainer.appendChild(row);
}

/**
 * Update financial impact section with story data
 * @param {Object} financialImpact - Financial impact data
 */
function updateFinancialImpact(financialImpact) {
  const impactContainer = document.getElementById('financialImpactContainer');
  
  if (!impactContainer) return;
  
  // Determine if we have scenario data
  const hasScenarios = financialImpact.scenarios && financialImpact.scenarios.length;
  
  // Clear existing content
  impactContainer.innerHTML = '';
  
  // Create chart if we have scenarios
  if (hasScenarios) {
    // Create chart container
    const chartContainer = document.createElement('div');
    chartContainer.className = 'roi-chart-container';
    chartContainer.id = 'roiChartContainer';
    impactContainer.appendChild(chartContainer);
    
    // Create canvas for chart
    const canvas = document.createElement('canvas');
    canvas.id = 'roiChart';
    chartContainer.appendChild(canvas);
    
    // Prepare data for chart
    createROIChart(financialImpact.scenarios);
  } else {
    // Display text summary if no chart data
    const summary = typeof financialImpact === 'string' 
      ? financialImpact 
      : (financialImpact.summary || 'No financial impact data available.');
    
    const summaryElement = document.createElement('p');
    summaryElement.textContent = summary;
    impactContainer.appendChild(summaryElement);
  }
}

/**
 * Create ROI chart with scenarios
 * @param {Array} scenarios - ROI scenarios data
 */
function createROIChart(scenarios) {
  // Skip if no Chart.js or no scenarios
  if (typeof Chart === 'undefined' || !scenarios || !scenarios.length) return;
  
  // Get canvas element
  const canvas = document.getElementById('roiChart');
  if (!canvas) return;
  
  // Prepare data for chart
  const labels = scenarios.map(scenario => 
    typeof scenario === 'string' ? 'Scenario' : (scenario.name || 'Scenario')
  );
  
  const values = scenarios.map(scenario => {
    if (typeof scenario === 'string') return 0;
    return scenario.value || scenario.roi || 0;
  });
  
  // Create chart
  if (window.roiChart) {
    window.roiChart.destroy();
  }
  
  window.roiChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'ROI Potential (%)',
        data: values,
        backgroundColor: [
          'rgba(16, 185, 129, 0.7)', // green
          'rgba(14, 165, 233, 0.7)', // blue
          'rgba(124, 58, 237, 0.7)'  // purple
        ],
        borderColor: [
          'rgb(16, 185, 129)',
          'rgb(14, 165, 233)',
          'rgb(124, 58, 237)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'ROI Potential (%)'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Estimated ROI by Scenario'
        }
      }
    }
  });
}

/**
 * Initialize visualization components with data from story
 */
function initVisualizationComponents() {
  // Initialize benchmarking visualization if the container exists
  initCompetitorBenchmarking();
  
  // Create sentiment analysis visualization if the container exists
  initSentimentVisualization();
}

/**
 * Initialize competitor benchmarking visualization
 */
function initCompetitorBenchmarking() {
  const benchmarkingContainer = document.getElementById('benchmarkingContainer');
  if (!benchmarkingContainer) return;
  
  // Check if we already have canvas elements created
  if (benchmarkingContainer.querySelector('canvas')) return;
  
  // Create canvas for chart
  const canvas = document.createElement('canvas');
  canvas.id = 'benchmarkingChart';
  benchmarkingContainer.appendChild(canvas);
  
  // Sample data for benchmarking chart - this will be replaced with real data from the API
  const labels = ['Carbon Emissions', 'Renewable Energy', 'Water Conservation', 'Circular Economy', 'Social Impact'];
  const companyData = [85, 90, 75, 80, 95];
  const industryData = [65, 70, 60, 55, 75];
  
  // Create chart if Chart.js is available
  if (typeof Chart !== 'undefined') {
    new Chart(canvas, {
      type: 'radar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Company',
            data: companyData,
            fill: true,
            backgroundColor: 'rgba(16, 185, 129, 0.2)',
            borderColor: 'rgb(16, 185, 129)',
            pointBackgroundColor: 'rgb(16, 185, 129)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgb(16, 185, 129)'
          },
          {
            label: 'Industry Average',
            data: industryData,
            fill: true,
            backgroundColor: 'rgba(124, 58, 237, 0.2)',
            borderColor: 'rgb(124, 58, 237)',
            pointBackgroundColor: 'rgb(124, 58, 237)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgb(124, 58, 237)'
          }
        ]
      },
      options: {
        elements: {
          line: {
            borderWidth: 3
          }
        },
        scales: {
          r: {
            angleLines: {
              display: true
            },
            suggestedMin: 0,
            suggestedMax: 100
          }
        }
      }
    });
  }
}

/**
 * Initialize sentiment analysis visualization
 */
function initSentimentVisualization() {
  const sentimentContainer = document.getElementById('sentimentContainer');
  if (!sentimentContainer) return;
  
  // Check if we already have canvas elements created
  if (sentimentContainer.querySelector('canvas')) return;
  
  // Create canvas for chart
  const canvas = document.createElement('canvas');
  canvas.id = 'sentimentChart';
  sentimentContainer.appendChild(canvas);
  
  // Sample data for sentiment chart - this will be replaced with real data from the API
  const labels = ['Twitter', 'News', 'Reports', 'Investor Calls', 'Sustainability Blogs'];
  const positiveData = [65, 75, 80, 60, 85];
  const neutralData = [25, 15, 15, 30, 10];
  const negativeData = [10, 10, 5, 10, 5];
  
  // Create chart if Chart.js is available
  if (typeof Chart !== 'undefined') {
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Positive',
            data: positiveData,
            backgroundColor: 'rgba(16, 185, 129, 0.7)',
            borderColor: 'rgb(16, 185, 129)',
            borderWidth: 1
          },
          {
            label: 'Neutral',
            data: neutralData,
            backgroundColor: 'rgba(14, 165, 233, 0.7)',
            borderColor: 'rgb(14, 165, 233)',
            borderWidth: 1
          },
          {
            label: 'Negative',
            data: negativeData,
            backgroundColor: 'rgba(225, 29, 72, 0.7)',
            borderColor: 'rgb(225, 29, 72)',
            borderWidth: 1
          }
        ]
      },
      options: {
        scales: {
          x: {
            stacked: true,
          },
          y: {
            stacked: true,
            beginAtZero: true,
            title: {
              display: true,
              text: 'Percentage (%)'
            },
            max: 100
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Sentiment Analysis by Source'
          }
        }
      }
    });
  }
}

/**
 * Initialize export functionality for reports
 */
function initExportFunctionality() {
  const pdfExportBtn = document.getElementById('pdfExportBtn');
  
  if (!pdfExportBtn) return;
  
  pdfExportBtn.addEventListener('click', function() {
    // Show loading notification
    if (typeof showNotification === 'function') {
      showNotification('Preparing PDF export...', 'info');
    }
    
    // Get company name for filename
    const companyName = document.querySelector('.company-profile h2')?.textContent || 'Company';
    const sanitizedCompanyName = companyName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    
    // Get story container
    const storyContainer = document.getElementById('storyContainer');
    
    if (!storyContainer) {
      if (typeof showNotification === 'function') {
        showNotification('Nothing to export', 'error');
      }
      return;
    }
    
    // Create filename
    const filename = `sustainability_story_${sanitizedCompanyName}_${getFormattedDate()}.pdf`;
    
    // Check if we have html2pdf.js available
    if (typeof html2pdf === 'function') {
      // Export using html2pdf
      const opt = {
        margin: 10,
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };
      
      html2pdf()
        .from(storyContainer)
        .set(opt)
        .save()
        .then(() => {
          if (typeof showNotification === 'function') {
            showNotification('PDF exported successfully!', 'success');
          }
        })
        .catch(err => {
          console.error('PDF export error:', err);
          if (typeof showNotification === 'function') {
            showNotification('Error exporting PDF', 'error');
          }
        });
    } else {
      // Fallback: use browser print functionality
      window.print();
      
      if (typeof showNotification === 'function') {
        showNotification('Please save as PDF from the print dialog', 'info');
      }
    }
  });
}

/**
 * Get formatted date for file naming
 * @returns {string} Formatted date (YYYY-MM-DD)
 */
function getFormattedDate() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
}