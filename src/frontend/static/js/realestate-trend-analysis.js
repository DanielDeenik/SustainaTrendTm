/**
 * Real Estate Sustainability Trend Analysis JavaScript Module
 */

// Chart objects
let trendChart, categoryDistributionChart, impactRadarChart;
let miniCharts = {};

/**
 * Update chart theme based on dark mode
 */
function updateChartTheme(isDarkMode) {
  const theme = {
    backgroundColor: isDarkMode ? '#1e1e1e' : '#ffffff',
    textColor: isDarkMode ? '#e0e0e0' : '#666666',
    gridColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
    borderColor: isDarkMode ? '#444' : '#e0e0e0',
    tooltipBackgroundColor: isDarkMode ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.8)',
    tooltipTextColor: isDarkMode ? '#fff' : '#333'
  };
  
  // Apply theme to all charts
  [trendChart, categoryDistributionChart, impactRadarChart, ...Object.values(miniCharts)].forEach(chart => {
    if (!chart) return;
    
    // Update chart options
    chart.options.scales = chart.options.scales || {};
    
    Object.values(chart.options.scales).forEach(scale => {
      scale.grid = scale.grid || {};
      scale.grid.color = theme.gridColor;
      scale.ticks = scale.ticks || {};
      scale.ticks.color = theme.textColor;
    });
    
    if (chart.options.plugins && chart.options.plugins.legend) {
      chart.options.plugins.legend.labels = chart.options.plugins.legend.labels || {};
      chart.options.plugins.legend.labels.color = theme.textColor;
    }
    
    if (chart.options.plugins && chart.options.plugins.tooltip) {
      chart.options.plugins.tooltip.backgroundColor = theme.tooltipBackgroundColor;
      chart.options.plugins.tooltip.titleColor = theme.tooltipTextColor;
      chart.options.plugins.tooltip.bodyColor = theme.tooltipTextColor;
    }
    
    chart.update();
  });
}

/**
 * Initialize all charts
 */
function initCharts() {
  // Initialize trend chart
  initTrendChart(document.getElementById('trendChart'));
  
  // Initialize category distribution chart
  initCategoryDistribution(document.getElementById('categoryDistribution'));
  
  // Initialize impact radar chart
  initImpactRadar(document.getElementById('impactRadar'));
  
  // Initialize mini charts in cards
  initMiniCharts();
  
  // Apply initial theme
  const isDarkMode = document.body.classList.contains('dark-mode');
  updateChartTheme(isDarkMode);
  
  // Subscribe to dark mode changes
  document.addEventListener('dark-mode-toggled', (e) => {
    updateChartTheme(e.detail.isDarkMode);
  });
}

/**
 * Initialize trend chart
 */
function initTrendChart(element) {
  if (!element) return;
  
  // Sample data - will be replaced with real API data
  const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const data = {
    labels: labels,
    datasets: [
      {
        label: 'Energy Efficiency',
        data: [75, 76, 78, 80, 82, 83, 85, 86, 88, 90, 91, 92],
        borderColor: '#2E7D32',
        backgroundColor: 'rgba(46, 125, 50, 0.1)',
        tension: 0.4,
        pointRadius: 3
      },
      {
        label: 'Emissions Reduction',
        data: [60, 62, 65, 68, 72, 76, 80, 84, 87, 89, 90, 92],
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.4,
        pointRadius: 3
      },
      {
        label: 'Water Conservation',
        data: [50, 52, 55, 58, 62, 65, 68, 72, 75, 78, 80, 82],
        borderColor: '#0288D1',
        backgroundColor: 'rgba(2, 136, 209, 0.1)',
        tension: 0.4,
        pointRadius: 3
      },
      {
        label: 'Waste Reduction',
        data: [40, 45, 49, 52, 58, 64, 70, 74, 78, 82, 85, 88],
        borderColor: '#FFA000',
        backgroundColor: 'rgba(255, 160, 0, 0.1)',
        tension: 0.4,
        pointRadius: 3
      }
    ]
  };
  
  const config = {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': ' + context.raw;
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
            text: 'Score'
          },
          suggestedMin: 0,
          suggestedMax: 100
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  };
  
  trendChart = new Chart(element, config);
}

/**
 * Initialize category distribution chart
 */
function initCategoryDistribution(element) {
  if (!element) return;
  
  // Sample data - will be replaced with real API data
  const data = {
    labels: ['Energy', 'Emissions', 'Water', 'Waste', 'Social', 'Governance'],
    datasets: [{
      data: [82, 75, 65, 70, 60, 55],
      backgroundColor: [
        '#2E7D32', // Energy - Primary
        '#4CAF50', // Emissions - Success
        '#0288D1', // Water - Info
        '#FFA000', // Waste - Warning
        '#78909C', // Social - Secondary
        '#455A64'  // Governance - Dark
      ],
      borderWidth: 0,
      borderRadius: 4
    }]
  };
  
  const config = {
    type: 'bar',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.raw + ' / 100';
            }
          }
        }
      },
      scales: {
        x: {
          max: 100,
          grid: {
            display: true
          }
        },
        y: {
          grid: {
            display: false
          }
        }
      }
    }
  };
  
  categoryDistributionChart = new Chart(element, config);
}

/**
 * Initialize impact radar chart
 */
function initImpactRadar(element) {
  if (!element) return;
  
  // Sample data - will be replaced with real API data
  const data = {
    labels: [
      'Carbon Reduction',
      'Energy Efficiency',
      'Water Conservation',
      'Waste Management',
      'Renewable Energy',
      'Sustainable Materials'
    ],
    datasets: [
      {
        label: 'Current Performance',
        data: [75, 82, 65, 70, 58, 62],
        fill: true,
        backgroundColor: 'rgba(46, 125, 50, 0.2)',
        borderColor: '#2E7D32',
        pointBackgroundColor: '#2E7D32',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#2E7D32'
      },
      {
        label: 'Industry Benchmark',
        data: [65, 70, 60, 55, 50, 58],
        fill: true,
        backgroundColor: 'rgba(66, 165, 245, 0.2)',
        borderColor: '#42A5F5',
        pointBackgroundColor: '#42A5F5',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#42A5F5'
      }
    ]
  };
  
  const config = {
    type: 'radar',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      elements: {
        line: {
          borderWidth: 2
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
  };
  
  impactRadarChart = new Chart(element, config);
}

/**
 * Initialize mini charts in analytics cards
 */
function initMiniCharts() {
  const miniChartElements = document.querySelectorAll('.mini-chart canvas');
  
  miniChartElements.forEach(element => {
    const chartId = element.id;
    const cardType = chartId.replace('TrendMini', '').toLowerCase();
    
    // Generate random data based on card type
    let data, color;
    
    switch (cardType) {
      case 'energy':
        data = [70, 72, 75, 78, 80, 82];
        color = '#2E7D32'; // primary
        break;
      case 'carbon':
        data = [65, 70, 78, 82, 85, 88];
        color = '#4CAF50'; // success
        break;
      case 'water':
        data = [140, 138, 136, 135, 134, 134];
        color = '#0288D1'; // info
        break;
      case 'roi':
        data = [12.5, 13.0, 13.8, 14.5, 15.0, 15.2];
        color = '#FFA000'; // warning
        break;
      default:
        data = [50, 55, 60, 65, 70, 75];
        color = '#2E7D32'; // primary
    }
    
    const config = {
      type: 'line',
      data: {
        labels: ['', '', '', '', '', ''], // Empty labels for cleaner look
        datasets: [{
          data: data,
          borderColor: color,
          backgroundColor: 'rgba(0, 0, 0, 0)', // Transparent
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            enabled: false
          }
        },
        scales: {
          x: {
            display: false
          },
          y: {
            display: false
          }
        },
        elements: {
          line: {
            tension: 0.4
          }
        }
      }
    };
    
    miniCharts[chartId] = new Chart(element, config);
  });
}

/**
 * Fetch real estate trend data from the API
 */
function fetchRealEstateTrendData(category = null, timeframe = null) {
  // Show loading state while fetching data
  showLoadingStates();
  
  // Build URL with parameters
  let url = '/api/realestate-trends';
  const params = [];
  if (category) params.push(`category=${category}`);
  if (timeframe) params.push(`timeframe=${timeframe}`);
  if (params.length > 0) url += '?' + params.join('&');
  
  // Fetch data from API
  fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      updateDashboard(data);
      removeLoadingStates();
    })
    .catch(error => {
      console.error('Error fetching real estate trend data:', error);
      // Use mock data as fallback
      const mockData = generateMockData();
      updateDashboard(mockData);
      removeLoadingStates();
      
      // Show error notification
      if (window.showNotification) {
        window.showNotification(
          'Could not fetch data from API. Using sample data instead.',
          'bi-exclamation-triangle',
          'warning'
        );
      }
    });
}

/**
 * Show loading states for components while data is being fetched
 */
function showLoadingStates() {
  document.querySelectorAll('.card-body').forEach(el => {
    el.classList.add('loading');
  });
}

/**
 * Remove loading states after data has been loaded
 */
function removeLoadingStates() {
  document.querySelectorAll('.card-body').forEach(el => {
    el.classList.remove('loading');
  });
}

/**
 * Update dashboard with fetched data
 */
function updateDashboard(data) {
  // Update summary cards
  updateSummaryCards(data);
  
  // Update charts
  updateCharts(data);
  
  // Update metric table
  updateMetricTable(data.metrics || []);
}

/**
 * Update summary cards with data
 */
function updateSummaryCards(data) {
  // This would be implemented with real data in production
  // For now, we'll keep the static content in the HTML
}

/**
 * Update charts with real data
 */
function updateCharts(data) {
  if (data.trendChartData) {
    updateTrendChart(data.trendChartData);
  }
  
  if (data.categoryDistribution) {
    updateCategoryDistribution(data.categoryDistribution);
  }
  
  if (data.impactData) {
    updateImpactRadar(data.impactData);
  }
}

/**
 * Update trend chart with real data
 */
function updateTrendChart(chartData) {
  if (!trendChart || !chartData || !chartData.datasets) return;
  
  trendChart.data.labels = chartData.labels || trendChart.data.labels;
  trendChart.data.datasets = chartData.datasets || trendChart.data.datasets;
  trendChart.update();
}

/**
 * Update category distribution chart with real data
 */
function updateCategoryDistribution(categoryData) {
  if (!categoryDistributionChart || !categoryData) return;
  
  categoryDistributionChart.data.labels = categoryData.labels || categoryDistributionChart.data.labels;
  categoryDistributionChart.data.datasets[0].data = categoryData.data || categoryDistributionChart.data.datasets[0].data;
  categoryDistributionChart.update();
  
  // Update category insights
  if (categoryData.insights) {
    document.getElementById('topPerformingCategory').textContent = categoryData.insights.topPerforming || 'Energy Efficiency';
    document.getElementById('attentionCategory').textContent = categoryData.insights.needsAttention || 'Water Management';
    document.getElementById('improvedCategory').textContent = categoryData.insights.mostImproved || 'Waste Reduction';
  }
}

/**
 * Update impact radar chart with real data
 */
function updateImpactRadar(impactData) {
  if (!impactRadarChart || !impactData) return;
  
  impactRadarChart.data.labels = impactData.labels || impactRadarChart.data.labels;
  
  if (impactData.datasets && impactData.datasets.length > 0) {
    impactRadarChart.data.datasets = impactData.datasets;
  }
  
  impactRadarChart.update();
}

/**
 * Update metric table with real data
 */
function updateMetricTable(metrics) {
  // This function would be implemented with real data in production
  // For now, we'll use the static content in the HTML
}

/**
 * Filter table by category
 */
function filterTableByCategory(category) {
  const rows = document.querySelectorAll('.metric-row');
  
  rows.forEach(row => {
    if (category === 'all' || row.dataset.category === category) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}

/**
 * Setup value chain selector
 */
function setupValueChainSelector() {
  const valueChainLinks = document.querySelectorAll('[data-value-chain]');
  
  valueChainLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Update active state
      valueChainLinks.forEach(l => l.classList.remove('active'));
      this.classList.add('active');
      
      // Update dropdown button text
      const dropdown = document.getElementById('valueChainDropdown');
      if (dropdown) {
        dropdown.textContent = this.textContent.trim();
      }
      
      // Apply filter
      const segment = this.dataset.valueChain;
      applyValueChainFilter(segment);
    });
  });
}

/**
 * Apply value chain filter
 */
function applyValueChainFilter(segment) {
  // In a real implementation, this would filter the data
  // For demo purposes, we'll just show a notification
  
  if (window.showNotification) {
    window.showNotification(
      `Value chain filter applied: ${segment === 'all' ? 'All Segments' : segment.charAt(0).toUpperCase() + segment.slice(1)}`,
      'bi-filter',
      'info'
    );
  }
}

/**
 * Setup RAG query system
 */
function setupRagQuerySystem() {
  const queryForm = document.getElementById('ragQueryForm');
  
  if (queryForm) {
    queryForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const query = document.getElementById('ragQueryInput').value.trim();
      if (!query) return;
      
      // Show loading state
      const button = document.getElementById('ragQueryButton');
      const originalButtonContent = button.innerHTML;
      button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
      button.disabled = true;
      
      // Show response container
      const responseContainer = document.getElementById('ragResponseContainer');
      responseContainer.style.display = 'block';
      
      // Simulate API call (would be real in production)
      setTimeout(() => {
        const responseContent = document.getElementById('ragResponseContent');
        const mockResponse = getMockRagResponse(query);
        responseContent.innerHTML = mockResponse;
        
        // Reset button state
        button.innerHTML = originalButtonContent;
        button.disabled = false;
      }, 1500);
    });
  }
}

/**
 * Setup property scorecard filtering
 */
function setupPropertyScorecard() {
  const propertyTypeLinks = document.querySelectorAll('[data-property-type]');
  
  propertyTypeLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Update active state
      propertyTypeLinks.forEach(l => l.classList.remove('active'));
      this.classList.add('active');
      
      // Update dropdown button text
      const dropdown = document.getElementById('propertyTypeDropdown');
      if (dropdown) {
        dropdown.textContent = this.textContent.trim();
      }
      
      // Update property scorecard
      const propertyType = this.dataset.propertyType;
      updatePropertyScorecard(propertyType);
      
      // Update recommended upgrades
      updateRecommendedUpgrades(propertyType);
    });
  });
}

/**
 * Update property scorecard based on selected property type
 */
function updatePropertyScorecard(propertyType) {
  // In a real implementation, this would filter the data
  // For demo purposes, we'll just show a notification
  
  if (window.showNotification) {
    window.showNotification(
      `Property scorecard updated for: ${propertyType === 'all' ? 'All Properties' : propertyType.charAt(0).toUpperCase() + propertyType.slice(1)}`,
      'bi-building',
      'info'
    );
  }
}

/**
 * Update recommended upgrades based on selected property type
 */
function updateRecommendedUpgrades(propertyType) {
  // In a real implementation, this would update the recommendations
  // For now, we'll just use the existing HTML content
}

/**
 * Get mock RAG response based on query
 */
function getMockRagResponse(query) {
  const responses = {
    "energy efficiency": `
      <p>Based on your portfolio data, there are several ways to improve energy efficiency in your office properties:</p>
      <ul>
        <li><strong>Building Management Systems:</strong> Implementing smart BMS could reduce energy consumption by 25-35%.</li>
        <li><strong>LED Lighting Upgrades:</strong> Converting to LED lighting with motion sensors can cut lighting energy use by 70-80%.</li>
        <li><strong>HVAC Optimization:</strong> Advanced HVAC controls with AI-driven optimization could save 15-30% on heating and cooling.</li>
      </ul>
      <p>Your office properties currently average 45 kgCO₂e/m², which is 15% better than industry average but still presents improvement opportunities.</p>
    `,
    "solar panels": `
      <p>Based on the portfolio data, solar panel installation shows promising ROI:</p>
      <ul>
        <li><strong>Potential ROI:</strong> 8-12% annually for your property portfolio</li>
        <li><strong>Payback Period:</strong> 6-8 years with current incentives</li>
        <li><strong>Carbon Impact:</strong> Could reduce overall portfolio emissions by approximately 28%</li>
      </ul>
      <p>Your flat-roof office and industrial properties offer the highest potential, with approximately 65% of roof area suitable for solar installation.</p>
    `,
    "water conservation": `
      <p>Your portfolio water usage (134 L/m²/year) presents significant optimization opportunities:</p>
      <ul>
        <li><strong>Rainwater Harvesting:</strong> Could reduce potable water consumption by 40-50% with a 4-5 year payback period</li>
        <li><strong>Smart Irrigation:</strong> Sensor-based systems can reduce landscape water usage by 30-60%</li>
        <li><strong>Low-Flow Fixtures:</strong> Modern fixtures could reduce indoor water usage by 30-35% with minimal investment</li>
      </ul>
      <p>Industrial properties show the highest water usage (210 L/m²/year) and present the greatest savings opportunity.</p>
    `,
    "default": `
      <p>Based on your portfolio data analysis, I can provide insights on several sustainability aspects:</p>
      <ul>
        <li><strong>Energy Performance:</strong> Your properties average 82 EPC score, which is 12% above market benchmark</li>
        <li><strong>Carbon Intensity:</strong> Average of 45 kgCO₂e/m² across portfolio, with office and retail properties performing best</li>
        <li><strong>Improvement Potential:</strong> Implementing the recommended upgrades could improve overall sustainability score by 15-20% within 18 months</li>
      </ul>
      <p>I can provide more specific insights if you ask about particular property types or sustainability aspects.</p>
    `
  };
  
  // Determine which response to use based on query keywords
  const lowerQuery = query.toLowerCase();
  
  if (lowerQuery.includes("energy efficiency") || lowerQuery.includes("energy") || lowerQuery.includes("efficiency")) {
    return responses["energy efficiency"];
  } else if (lowerQuery.includes("solar") || lowerQuery.includes("solar panel") || lowerQuery.includes("panels") || lowerQuery.includes("roi")) {
    return responses["solar panels"];
  } else if (lowerQuery.includes("water") || lowerQuery.includes("water usage") || lowerQuery.includes("conservation")) {
    return responses["water conservation"];
  } else {
    return responses["default"];
  }
}

/**
 * Export data in various formats
 */
function exportData(format) {
  // In a real implementation, this would export actual data
  // For demo purposes, we'll just show a notification
  
  let message = '';
  let icon = 'bi-download';
  
  switch(format) {
    case 'pdf':
      message = 'Generating PDF report...';
      icon = 'bi-file-earmark-pdf';
      break;
    case 'excel':
      message = 'Exporting data to Excel...';
      icon = 'bi-file-earmark-excel';
      break;
    case 'csv':
      message = 'Exporting data to CSV...';
      icon = 'bi-filetype-csv';
      break;
    case 'png':
      message = 'Saving charts as images...';
      icon = 'bi-file-earmark-image';
      break;
    default:
      message = 'Exporting data...';
  }
  
  if (window.showNotification) {
    window.showNotification(message, icon, 'info');
  }
  
  // Simulate export delay
  setTimeout(() => {
    if (window.showNotification) {
      window.showNotification(
        `Data successfully exported in ${format.toUpperCase()} format`,
        'bi-check-circle',
        'success'
      );
    }
  }, 2000);
}

/**
 * Get category display name
 */
function getCategoryDisplayName(category) {
  switch(category.toLowerCase()) {
    case 'energy':
      return 'Energy Efficiency';
    case 'emissions':
      return 'Carbon Emissions';
    case 'water':
      return 'Water Management';
    case 'waste':
      return 'Waste Reduction';
    case 'social':
      return 'Social Impact';
    case 'governance':
      return 'Governance';
    default:
      return category.charAt(0).toUpperCase() + category.slice(1);
  }
}

/**
 * Get category class for styling
 */
function getCategoryClass(category) {
  switch(category.toLowerCase()) {
    case 'energy':
      return 'primary';
    case 'emissions':
      return 'success';
    case 'water':
      return 'info';
    case 'waste':
      return 'warning';
    case 'social':
      return 'secondary';
    case 'governance':
      return 'dark';
    default:
      return 'primary';
  }
}

/**
 * Get category colors for charts
 */
function getCategoryColors(categories) {
  const colors = [];
  
  categories.forEach(category => {
    switch(category.toLowerCase()) {
      case 'energy':
        colors.push('#2E7D32'); // primary
        break;
      case 'emissions':
        colors.push('#4CAF50'); // success
        break;
      case 'water':
        colors.push('#0288D1'); // info
        break;
      case 'waste':
        colors.push('#FFA000'); // warning
        break;
      case 'social':
        colors.push('#78909C'); // secondary
        break;
      case 'governance':
        colors.push('#455A64'); // dark
        break;
      default:
        colors.push('#2E7D32'); // primary
    }
  });
  
  return colors;
}

/**
 * Generate mock data for development
 */
function generateMockData() {
  // Generate labels for 12 months
  const now = new Date();
  const labels = [];
  for (let i = 11; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    labels.push(d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }));
  }
  
  // Generate mock metrics data
  const metrics = [
    {
      name: 'Energy Efficiency',
      category: 'energy',
      value: 82,
      unit: 'EPC score',
      percent_change: 8,
      trend_data: [75, 76, 78, 80, 82, 83, 85, 86, 88, 90, 91, 92],
      virality: 85,
      icon: 'lightning'
    },
    {
      name: 'Carbon Reduction',
      category: 'emissions',
      value: 28.5,
      unit: '%',
      percent_change: 12,
      trend_data: [16, 18, 20, 22, 23, 24, 25, 26, 27, 28, 28.5, 29],
      virality: 92,
      icon: 'cloud'
    },
    {
      name: 'Water Conservation',
      category: 'water',
      value: 134,
      unit: 'L/m²/year',
      percent_change: -5,
      trend_data: [145, 143, 140, 138, 137, 136, 135, 135, 134, 134, 134, 134],
      virality: 65,
      icon: 'droplet'
    },
    {
      name: 'Waste Diversion',
      category: 'waste',
      value: 75,
      unit: '%',
      percent_change: 15,
      trend_data: [60, 62, 64, 66, 68, 70, 71, 72, 73, 74, 75, 75],
      virality: 72,
      icon: 'trash'
    },
    {
      name: 'Renewable Energy',
      category: 'energy',
      value: 35,
      unit: '%',
      percent_change: 22,
      trend_data: [15, 17, 19, 22, 25, 27, 29, 30, 32, 33, 34, 35],
      virality: 88,
      icon: 'sun'
    },
    {
      name: 'Tenant Satisfaction',
      category: 'social',
      value: 4.2,
      unit: '/ 5',
      percent_change: 5,
      trend_data: [3.8, 3.9, 3.9, 4.0, 4.0, 4.1, 4.1, 4.2, 4.2, 4.2, 4.2, 4.2],
      virality: 60,
      icon: 'people'
    },
    {
      name: 'ESG Reporting Score',
      category: 'governance',
      value: 78,
      unit: '/ 100',
      percent_change: 10,
      trend_data: [62, 64, 66, 68, 70, 72, 74, 75, 76, 77, 78, 78],
      virality: 70,
      icon: 'clipboard-check'
    }
  ];
  
  // Generate trend chart data
  const trendChartData = {
    labels: labels,
    datasets: [
      {
        label: 'Energy Efficiency',
        data: [75, 76, 78, 80, 82, 83, 85, 86, 88, 90, 91, 92],
        borderColor: '#2E7D32',
        backgroundColor: 'rgba(46, 125, 50, 0.1)',
        tension: 0.4,
        pointRadius: 3
      },
      {
        label: 'Carbon Reduction',
        data: [60, 62, 65, 68, 72, 76, 80, 84, 87, 89, 90, 92],
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.4,
        pointRadius: 3
      },
      {
        label: 'Water Conservation',
        data: [50, 52, 55, 58, 62, 65, 68, 72, 75, 78, 80, 82],
        borderColor: '#0288D1',
        backgroundColor: 'rgba(2, 136, 209, 0.1)',
        tension: 0.4,
        pointRadius: 3
      },
      {
        label: 'Waste Reduction',
        data: [40, 45, 49, 52, 58, 64, 70, 74, 78, 82, 85, 88],
        borderColor: '#FFA000',
        backgroundColor: 'rgba(255, 160, 0, 0.1)',
        tension: 0.4,
        pointRadius: 3
      }
    ]
  };
  
  // Generate category distribution data
  const categoryDistribution = {
    labels: ['Energy', 'Emissions', 'Water', 'Waste', 'Social', 'Governance'],
    data: [82, 75, 65, 70, 60, 55],
    insights: {
      topPerforming: 'Energy Efficiency',
      needsAttention: 'Water Management',
      mostImproved: 'Waste Reduction'
    }
  };
  
  // Generate impact radar data
  const impactData = {
    labels: [
      'Carbon Reduction',
      'Energy Efficiency',
      'Water Conservation',
      'Waste Management',
      'Renewable Energy',
      'Sustainable Materials'
    ],
    datasets: [
      {
        label: 'Current Performance',
        data: [75, 82, 65, 70, 58, 62],
        fill: true,
        backgroundColor: 'rgba(46, 125, 50, 0.2)',
        borderColor: '#2E7D32',
        pointBackgroundColor: '#2E7D32',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#2E7D32'
      },
      {
        label: 'Industry Benchmark',
        data: [65, 70, 60, 55, 50, 58],
        fill: true,
        backgroundColor: 'rgba(66, 165, 245, 0.2)',
        borderColor: '#42A5F5',
        pointBackgroundColor: '#42A5F5',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#42A5F5'
      }
    ]
  };
  
  return {
    metrics: metrics,
    trendChartData: trendChartData,
    categoryDistribution: categoryDistribution,
    impactData: impactData
  };
}