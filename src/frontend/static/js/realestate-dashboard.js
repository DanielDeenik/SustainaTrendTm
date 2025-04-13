/**
 * SustainaTrend™ Real Estate Dashboard
 * JavaScript functionality for the Real Estate Sustainability dashboard
 */

// Initialize the SimCorp-inspired dashboard components
document.addEventListener('DOMContentLoaded', function() {
  // Set up tab functionality
  initTabs();
  
  // Set up real-time updates
  initRealTimeUpdates();
  
  // Set up Gemini search functionality
  initGeminiSearch();
  
  // Initialize charts
  if (typeof Chart !== 'undefined') {
    initCharts();
  }
});

/**
 * Initialize the tabs functionality
 */
function initTabs() {
  const tabs = document.querySelectorAll('.st-simcorp-tab');
  
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      // Remove active class from all tabs
      tabs.forEach(t => t.classList.remove('active'));
      
      // Add active class to clicked tab
      this.classList.add('active');
      
      // Hide all tab content
      const tabContents = document.querySelectorAll('.st-tab-content');
      tabContents.forEach(content => content.classList.remove('active'));
      
      // Show the corresponding tab content
      const tabId = this.getAttribute('data-tab');
      const activeContent = document.getElementById(`${tabId}-tab`);
      if (activeContent) {
        activeContent.classList.add('active');
      }
    });
  });
}

/**
 * Initialize the real-time updates functionality using Server-Sent Events
 */
function initRealTimeUpdates() {
  // Check if we're on the correct page and if the browser supports SSE
  const realtimeFeed = document.querySelector('.st-realtime-feed');
  if (!realtimeFeed || !window.EventSource) {
    return;
  }
  
  let eventSource;
  
  try {
    // Connect to the SSE endpoint
    eventSource = new EventSource('/api/realestate-realtime-updates');
    
    // Listen for messages
    eventSource.addEventListener('message', function(e) {
      try {
        const data = JSON.parse(e.data);
        addRealtimeUpdate(data);
      } catch (error) {
        console.error('Error parsing SSE message:', error);
      }
    });
    
    // Handle errors
    eventSource.addEventListener('error', function() {
      console.warn('SSE connection error. Falling back to polling.');
      if (eventSource) {
        eventSource.close();
      }
      
      // Fall back to polling
      fallbackToPolling();
    });
  } catch (error) {
    console.error('Error setting up SSE:', error);
    fallbackToPolling();
  }
  
  // Clean up function to close SSE connection when leaving the page
  window.addEventListener('beforeunload', function() {
    if (eventSource) {
      eventSource.close();
    }
  });
}

/**
 * Fall back to polling for real-time updates if SSE fails
 */
function fallbackToPolling() {
  const realtimePoll = setInterval(function() {
    fetch('/api/realestate-updates')
      .then(response => response.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          // Add the latest update to the feed
          addRealtimeUpdate(data[0]);
        }
      })
      .catch(error => {
        console.error('Error polling for updates:', error);
      });
  }, 30000); // Poll every 30 seconds
  
  // Clean up function
  window.addEventListener('beforeunload', function() {
    clearInterval(realtimePoll);
  });
}

/**
 * Add a real-time update to the feed
 * @param {Object} data - The update data
 */
function addRealtimeUpdate(data) {
  const realtimeFeed = document.querySelector('.st-realtime-feed');
  if (!realtimeFeed) return;
  
  // Create the new update element
  const updateElement = document.createElement('div');
  updateElement.className = 'st-realtime-item';
  
  // Determine the icon class based on the category
  let iconClass = 'st-realtime-icon-breeam';
  if (data.category === 'energy') {
    iconClass = 'st-realtime-icon-energy';
  } else if (data.category === 'carbon') {
    iconClass = 'st-realtime-icon-carbon';
  } else if (data.category === 'financial') {
    iconClass = 'st-realtime-icon-financial';
  }
  
  // Set the icon based on the category
  let iconHtml = '<i class="bi bi-award"></i>';
  if (data.category === 'energy') {
    iconHtml = '<i class="bi bi-lightning-charge"></i>';
  } else if (data.category === 'carbon') {
    iconHtml = '<i class="bi bi-cloud"></i>';
  } else if (data.category === 'financial') {
    iconHtml = '<i class="bi bi-graph-up-arrow"></i>';
  }
  
  // Populate the update element
  updateElement.innerHTML = `
    <div class="st-realtime-icon ${iconClass}">
      ${iconHtml}
    </div>
    <div class="st-realtime-content">
      <div class="st-realtime-title">${data.title}</div>
      <div class="st-realtime-description">${data.description}</div>
      <div class="st-realtime-timestamp">Just now</div>
    </div>
  `;
  
  // Add the new update to the top of the feed
  realtimeFeed.insertBefore(updateElement, realtimeFeed.firstChild);
  
  // If there are more than 5 updates, remove the oldest one
  if (realtimeFeed.children.length > 5) {
    realtimeFeed.removeChild(realtimeFeed.lastChild);
  }
  
  // Add a fade-in effect
  updateElement.style.opacity = '0';
  setTimeout(() => {
    updateElement.style.transition = 'opacity 0.5s ease-in-out';
    updateElement.style.opacity = '1';
  }, 10);
}

/**
 * Initialize the Gemini search functionality
 */
function initGeminiSearch() {
  const searchInput = document.getElementById('gemini-search-input');
  const searchButton = document.getElementById('gemini-search-button');
  const resultsContainer = document.getElementById('gemini-results');
  const responseContainer = document.getElementById('gemini-response');
  const suggestions = document.querySelectorAll('.gemini-suggestion');
  
  if (!searchInput || !searchButton || !resultsContainer || !responseContainer) {
    return;
  }
  
  // Handle search button click
  searchButton.addEventListener('click', function() {
    performGeminiSearch(searchInput.value);
  });
  
  // Handle enter key in search input
  searchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      performGeminiSearch(searchInput.value);
    }
  });
  
  // Handle suggestion clicks
  suggestions.forEach(suggestion => {
    suggestion.addEventListener('click', function() {
      searchInput.value = this.textContent;
      performGeminiSearch(this.textContent);
    });
  });
  
  /**
   * Perform a search using the Gemini API
   * @param {string} query - The search query
   */
  function performGeminiSearch(query) {
    if (!query || query.trim() === '') {
      return;
    }
    
    // Show loading state
    responseContainer.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Analyzing your query with Gemini AI...</p></div>';
    resultsContainer.style.display = 'block';
    
    // Make the API request
    fetch('/api-realestate-gemini-search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: query })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      // Format and display the results
      displayGeminiResults(data);
    })
    .catch(error => {
      console.error('Error with Gemini search:', error);
      responseContainer.innerHTML = `
        <div class="alert alert-danger">
          <i class="bi bi-exclamation-triangle me-2"></i>
          Sorry, there was an error processing your request. Please try again.
        </div>
      `;
    });
  }
  
  /**
   * Display the Gemini search results
   * @param {Object} data - The search results data
   */
  function displayGeminiResults(data) {
    if (!data || !data.response) {
      responseContainer.innerHTML = `
        <div class="alert alert-warning">
          <i class="bi bi-exclamation-circle me-2"></i>
          No results found. Please try a different query.
        </div>
      `;
      return;
    }
    
    // Create formatted HTML for the response
    let responseHtml = `
      <div class="st-gemini-response">
        <div class="st-gemini-response-text mb-3">
          ${formatResponseText(data.response)}
        </div>
    `;
    
    // Add recommendations if available
    if (data.recommendations && data.recommendations.length > 0) {
      responseHtml += `
        <div class="st-gemini-recommendations mt-3">
          <h6 class="mb-2"><i class="bi bi-lightbulb me-2 text-warning"></i>Recommendations</h6>
          <ul class="list-unstyled">
      `;
      
      data.recommendations.forEach(rec => {
        responseHtml += `<li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>${rec}</li>`;
      });
      
      responseHtml += `
          </ul>
        </div>
      `;
    }
    
    // Add metrics if available
    if (data.metrics && Object.keys(data.metrics).length > 0) {
      responseHtml += `
        <div class="st-gemini-metrics mt-3">
          <h6 class="mb-2"><i class="bi bi-graph-up me-2 text-primary"></i>Related Metrics</h6>
          <div class="row">
      `;
      
      Object.entries(data.metrics).forEach(([key, value]) => {
        responseHtml += `
          <div class="col-md-4 mb-2">
            <div class="card border-0 bg-light">
              <div class="card-body p-2">
                <div class="d-flex justify-content-between align-items-center">
                  <div class="small text-muted">${key}</div>
                  <div class="fw-bold">${value}</div>
                </div>
              </div>
            </div>
          </div>
        `;
      });
      
      responseHtml += `
          </div>
        </div>
      `;
    }
    
    responseHtml += `</div>`;
    
    // Update the response container
    responseContainer.innerHTML = responseHtml;
  }
  
  /**
   * Format the response text with proper formatting
   * @param {string} text - The response text
   * @returns {string} - The formatted HTML
   */
  function formatResponseText(text) {
    // Convert markdown-style formatting to HTML
    let formattedText = text;
    
    // Replace markdown headers
    formattedText = formattedText.replace(/^### (.*$)/gm, '<h6>$1</h6>');
    formattedText = formattedText.replace(/^## (.*$)/gm, '<h5>$1</h5>');
    formattedText = formattedText.replace(/^# (.*$)/gm, '<h4>$1</h4>');
    
    // Replace markdown lists
    formattedText = formattedText.replace(/^\* (.*$)/gm, '<li>$1</li>');
    formattedText = formattedText.replace(/^- (.*$)/gm, '<li>$1</li>');
    formattedText = formattedText.replace(/<\/li>\n<li>/g, '</li><li>');
    formattedText = formattedText.replace(/<li>(.*)<\/li>/g, '<ul><li>$1</li></ul>');
    formattedText = formattedText.replace(/<\/ul>\n<ul>/g, '');
    
    // Replace markdown emphasis
    formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Replace markdown code blocks
    formattedText = formattedText.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Replace double newlines with paragraph breaks
    formattedText = formattedText.replace(/\n\n/g, '</p><p>');
    
    // Wrap in paragraph tags if not already done
    if (!formattedText.startsWith('<p>')) {
      formattedText = '<p>' + formattedText;
    }
    if (!formattedText.endsWith('</p>')) {
      formattedText = formattedText + '</p>';
    }
    
    return formattedText;
  }
}

/**
 * Initialize charts for the dashboard
 */
function initCharts() {
  // Energy Performance Chart
  const energyChartElement = document.getElementById('energy-performance-chart');
  if (energyChartElement) {
    const energyChart = new Chart(energyChartElement, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [
          {
            label: 'This Year',
            data: [42, 40, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            fill: true
          },
          {
            label: 'Last Year',
            data: [50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39],
            borderColor: '#9ca3af',
            borderDash: [5, 5],
            backgroundColor: 'transparent',
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Energy Consumption (kWh/m²)'
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: 'kWh/m²'
            }
          }
        }
      }
    });
  }
  
  // Carbon Footprint Chart
  const carbonChartElement = document.getElementById('carbon-footprint-chart');
  if (carbonChartElement) {
    const carbonChart = new Chart(carbonChartElement, {
      type: 'bar',
      data: {
        labels: ['Office', 'Residential', 'Retail', 'Mixed Use', 'Industrial'],
        datasets: [
          {
            label: 'Current',
            data: [18.5, 12.3, 25.7, 20.1, 30.5],
            backgroundColor: '#10b981'
          },
          {
            label: 'Target 2025',
            data: [15, 10, 20, 15, 25],
            backgroundColor: '#3b82f6'
          },
          {
            label: 'Target 2030',
            data: [10, 7, 15, 10, 20],
            backgroundColor: '#6366f1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Carbon Footprint by Property Type'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'kg CO₂e/m²'
            }
          }
        }
      }
    });
  }
  
  // BREEAM Distribution Chart
  const breeamChartElement = document.getElementById('breeam-distribution-chart');
  if (breeamChartElement) {
    const breeamChart = new Chart(breeamChartElement, {
      type: 'doughnut',
      data: {
        labels: ['Outstanding', 'Excellent', 'Very Good', 'Good', 'Pass', 'Unclassified'],
        datasets: [
          {
            data: [15, 30, 25, 20, 8, 2],
            backgroundColor: [
              '#006633', // Outstanding
              '#39a935', // Excellent
              '#88c542', // Very Good
              '#ffd100', // Good
              '#ff9933', // Pass
              '#dd0000'  // Unclassified
            ],
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
          },
          title: {
            display: true,
            text: 'BREEAM Rating Distribution'
          }
        }
      }
    });
  }
  
  // ROI Chart
  const roiChartElement = document.getElementById('roi-chart');
  if (roiChartElement) {
    const roiChart = new Chart(roiChartElement, {
      type: 'bar',
      data: {
        labels: ['Solar Panels', 'Insulation', 'Smart HVAC', 'LED Lighting', 'Water Systems', 'Green Roof'],
        datasets: [
          {
            label: 'ROI (%)',
            data: [14.2, 18.7, 12.3, 22.5, 16.8, 9.4],
            backgroundColor: [
              '#10b981', 
              '#3b82f6', 
              '#f59e0b', 
              '#6366f1',
              '#ec4899',
              '#0ea5e9'
            ],
            borderWidth: 1
          }
        ]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          title: {
            display: true,
            text: 'ROI by Sustainability Investment Type'
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Return on Investment (%)'
            }
          }
        }
      }
    });
  }
}