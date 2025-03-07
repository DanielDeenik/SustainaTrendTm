/**
 * SustainaTrend™ - Trend Analysis Dashboard
 * Main JavaScript file for the trend analysis dashboard
 */

// Global state
const state = {
  trends: [],
  filters: {
    timeframe: 'year',
    categories: ['emissions', 'energy', 'water', 'waste', 'social', 'governance'],
    minVirality: 30
  },
  chartTimeRange: 'year'
};

/**
 * Initialize the trend analysis dashboard
 */
function initTrendAnalysis() {
  console.log('Initializing Trend Analysis Dashboard');
  
  // Initialize tooltips and other UI components
  initUI();
  
  // Fetch trend data
  fetchTrendData();
  
  // Initialize export functionality
  initExport();
  
  // Initialize filter modal
  initFilterModal();
  
  // Initialize chart controls
  initChartControls();
}

/**
 * Initialize UI components
 */
function initUI() {
  // Initialize tooltips
  initTooltips();
  
  // Initialize card animations
  initCardAnimation();
  
  // Initialize notifications
  initNotifications();
  
  // Show welcome notification
  setTimeout(() => {
    showNotification('Welcome to the Trend Analysis Dashboard. Data is being loaded.', 'info');
  }, 1000);
}

/**
 * Fetch trend data from API
 */
function fetchTrendData() {
  // Show loading state
  showLoading(true);
  
  // Fetch data from API
  fetch('/api/trends')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('Trend data loaded:', data);
      
      // Store data in state
      state.trends = data.trends || [];
      
      // Update UI with data
      updateDashboard();
      
      // Hide loading state
      showLoading(false);
      
      // Show success notification
      showNotification('Trend data loaded successfully', 'success');
    })
    .catch(error => {
      console.error('Error fetching trend data:', error);
      
      // Hide loading state
      showLoading(false);
      
      // Show error notification
      showNotification('Failed to load trend data. Please try again.', 'error');
      
      // Load mock data as fallback
      loadMockData();
    });
}

/**
 * Load mock data as fallback
 */
function loadMockData() {
  console.log('Loading mock trend data');
  
  // Generate mock trend data
  const mockTrends = generateMockTrends();
  
  // Store mock data in state
  state.trends = mockTrends;
  
  // Update UI with mock data
  updateDashboard();
  
  // Show info notification
  showNotification('Using mock data for demonstration', 'info');
}

/**
 * Generate mock trend data
 * @returns {Array} Array of mock trend objects
 */
function generateMockTrends() {
  const categories = ['emissions', 'energy', 'water', 'waste', 'social', 'governance'];
  const trendNames = {
    emissions: ['Carbon Footprint Reduction', 'Scope 3 Emissions Tracking', 'Carbon Capture Implementation', 'Emissions Reporting Standards', 'Net Zero Commitments'],
    energy: ['Renewable Energy Usage', 'Energy Efficiency Measures', 'Green Energy Certificates', 'Energy Storage Solutions', 'Smart Grid Integration'],
    water: ['Water Conservation', 'Water Recycling Programs', 'Water Footprint Assessment', 'Watershed Protection', 'Water Quality Monitoring'],
    waste: ['Zero Waste Initiatives', 'Circular Economy Integration', 'Plastic Reduction Programs', 'Composting Programs', 'E-waste Management'],
    social: ['Diversity Initiatives', 'Community Engagement', 'Labor Standards Compliance', 'Human Rights Due Diligence', 'Employee Wellbeing Programs'],
    governance: ['ESG Board Oversight', 'Sustainability Reporting', 'Ethical Supply Chain', 'Anti-corruption Measures', 'Stakeholder Engagement']
  };
  
  const trends = [];
  
  // Generate 30 mock trends
  for (let i = 0; i < 30; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)];
    const nameOptions = trendNames[category];
    const name = nameOptions[Math.floor(Math.random() * nameOptions.length)];
    
    // Generate date within last year
    const daysAgo = Math.floor(Math.random() * 365);
    const date = new Date();
    date.setDate(date.getDate() - daysAgo);
    
    trends.push({
      id: `trend-${i + 1}`,
      name: name,
      category: category,
      virality_score: Math.floor(Math.random() * 70) + 30, // 30-100
      direction: Math.random() > 0.3 ? 'increasing' : 'decreasing',
      duration: ['short', 'medium', 'long'][Math.floor(Math.random() * 3)],
      date: date.toISOString(),
      description: `Trend in ${name} showing ${Math.random() > 0.3 ? 'positive' : 'negative'} momentum across the industry.`
    });
  }
  
  return trends;
}

/**
 * Update dashboard with current data
 */
function updateDashboard() {
  // Apply current filters
  const filteredTrends = filterTrends(state.trends, state.filters);
  
  // Update metrics overview
  updateMetricsOverview(filteredTrends);
  
  // Update charts
  createTrendChart(filteredTrends);
  createCategoryDistribution(filteredTrends);
  createViralityRadar(filteredTrends);
  
  // Update trend table
  updateTrendTable(filteredTrends);
}

/**
 * Filter trends based on current filters
 * @param {Array} trends - Trends to filter
 * @param {Object} filters - Filter criteria
 * @returns {Array} Filtered trends
 */
function filterTrends(trends, filters) {
  return trends.filter(trend => {
    // Filter by category
    if (filters.categories.length > 0 && !filters.categories.includes(trend.category)) {
      return false;
    }
    
    // Filter by virality score
    if (trend.virality_score < filters.minVirality) {
      return false;
    }
    
    // Filter by timeframe
    if (filters.timeframe !== 'all') {
      const trendDate = new Date(trend.date);
      const now = new Date();
      
      // Calculate date threshold based on timeframe
      let threshold = new Date();
      switch (filters.timeframe) {
        case 'month':
          threshold.setMonth(now.getMonth() - 1);
          break;
        case '3month':
          threshold.setMonth(now.getMonth() - 3);
          break;
        case '6month':
          threshold.setMonth(now.getMonth() - 6);
          break;
        case 'year':
          threshold.setFullYear(now.getFullYear() - 1);
          break;
      }
      
      if (trendDate < threshold) {
        return false;
      }
    }
    
    return true;
  });
}

/**
 * Update metrics overview with trend data
 * @param {Array} trends - Filtered trends
 */
function updateMetricsOverview(trends) {
  // Get DOM elements
  const totalTrendsEl = document.getElementById('total-trends');
  const avgViralityEl = document.getElementById('avg-virality');
  const improvingTrendsEl = document.getElementById('improving-trends');
  const improvingPercentEl = document.getElementById('improving-percent');
  const worseningTrendsEl = document.getElementById('worsening-trends');
  const worseningPercentEl = document.getElementById('worsening-percent');
  
  // Calculate metrics
  const totalTrends = trends.length;
  
  // Calculate average virality
  const totalVirality = trends.reduce((sum, trend) => sum + trend.virality_score, 0);
  const avgVirality = totalTrends > 0 ? Math.round(totalVirality / totalTrends) : 0;
  
  // Count improving and worsening trends
  const improvingTrends = trends.filter(trend => trend.direction === 'increasing').length;
  const worseningTrends = trends.filter(trend => trend.direction === 'decreasing').length;
  
  // Calculate percentages
  const improvingPercent = totalTrends > 0 ? Math.round((improvingTrends / totalTrends) * 100) : 0;
  const worseningPercent = totalTrends > 0 ? Math.round((worseningTrends / totalTrends) * 100) : 0;
  
  // Update DOM elements
  totalTrendsEl.textContent = totalTrends;
  avgViralityEl.textContent = avgVirality;
  improvingTrendsEl.textContent = improvingTrends;
  improvingPercentEl.textContent = `${improvingPercent}%`;
  worseningTrendsEl.textContent = worseningTrends;
  worseningPercentEl.textContent = `${worseningPercent}%`;
}

/**
 * Create the main trend chart
 * @param {Array} trends - Filtered trends
 */
function createTrendChart(trends) {
  // Prepare chart data
  const chartData = prepareTrendChartData(trends, state.chartTimeRange);
  
  // Create traces for each category
  const traces = Object.keys(chartData).map(category => {
    return {
      type: 'scatter',
      mode: 'lines',
      name: category.charAt(0).toUpperCase() + category.slice(1),
      x: chartData[category].dates,
      y: chartData[category].values,
      line: {
        shape: 'spline',
        width: 3,
        color: trendViz.categoryColors[category] || '#666'
      }
    };
  });
  
  // Create chart
  trendViz.createLineChart('trend-chart', traces, {
    yAxisTitle: 'Virality Score',
    xAxisTitle: 'Date',
    gridLines: true,
    responsive: true
  });
}

/**
 * Prepare data for trend chart
 * @param {Array} trends - Filtered trends
 * @param {string} timeRange - Time range for chart
 * @returns {Object} Chart data organized by category
 */
function prepareTrendChartData(trends, timeRange) {
  // Get categories from trends
  const categories = [...new Set(trends.map(trend => trend.category))];
  
  // Get time range boundaries
  const now = new Date();
  let startDate = new Date();
  
  // Set start date based on time range
  switch (timeRange) {
    case '3month':
      startDate.setMonth(now.getMonth() - 3);
      break;
    case '6month':
      startDate.setMonth(now.getMonth() - 6);
      break;
    case 'year':
      startDate.setFullYear(now.getFullYear() - 1);
      break;
    case 'all':
      // Find earliest trend date
      startDate = new Date(Math.min(...trends.map(trend => new Date(trend.date).getTime())));
      break;
  }
  
  // Generate date series for the time range
  const dateRange = generateDateRange(startDate, now, timeRange);
  
  // Initialize chart data structure
  const chartData = {};
  categories.forEach(category => {
    chartData[category] = {
      dates: dateRange,
      values: Array(dateRange.length).fill(0)
    };
  });
  
  // Populate values for each category
  trends.forEach(trend => {
    const trendDate = new Date(trend.date);
    
    // Skip trends outside the date range
    if (trendDate < startDate) return;
    
    // Find closest date index
    const closestDateIndex = findClosestDateIndex(dateRange, trendDate);
    if (closestDateIndex !== -1) {
      // Add trend virality to the appropriate date and category
      chartData[trend.category].values[closestDateIndex] += trend.virality_score;
    }
  });
  
  // Smooth the data for better visualization
  categories.forEach(category => {
    chartData[category].values = smoothArray(chartData[category].values);
  });
  
  return chartData;
}

/**
 * Generate a date range array
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date
 * @param {string} timeRange - Time range type
 * @returns {Array} Array of date strings
 */
function generateDateRange(startDate, endDate, timeRange) {
  const dates = [];
  const step = timeRange === '3month' ? 7 : 15; // Use weekly or bi-weekly steps
  
  const currentDate = new Date(startDate);
  while (currentDate <= endDate) {
    dates.push(formatDate(currentDate, 'short'));
    currentDate.setDate(currentDate.getDate() + step);
  }
  
  return dates;
}

/**
 * Find the closest date index in a date array
 * @param {Array} dates - Array of date strings
 * @param {Date} targetDate - Target date to find
 * @returns {number} Index of closest date, or -1 if not found
 */
function findClosestDateIndex(dates, targetDate) {
  const targetDateStr = formatDate(targetDate, 'short');
  
  // First try exact match
  const exactIndex = dates.indexOf(targetDateStr);
  if (exactIndex !== -1) return exactIndex;
  
  // If no exact match, find closest date
  // For simplicity, we'll just use the nearest past date
  // by converting back all strings to dates
  const dateObjects = dates.map(d => new Date(d));
  
  for (let i = dateObjects.length - 1; i >= 0; i--) {
    if (dateObjects[i] <= targetDate) {
      return i;
    }
  }
  
  return 0; // Default to first date if no past date found
}

/**
 * Apply simple smoothing to an array of numbers
 * @param {Array} arr - Array to smooth
 * @returns {Array} Smoothed array
 */
function smoothArray(arr) {
  // Skip smoothing for small arrays
  if (arr.length < 4) return arr;
  
  const result = [...arr];
  
  // Apply simple moving average smoothing
  for (let i = 1; i < arr.length - 1; i++) {
    result[i] = (arr[i - 1] + arr[i] * 2 + arr[i + 1]) / 4;
  }
  
  return result;
}

/**
 * Create the category distribution pie chart
 * @param {Array} trends - Filtered trends
 */
function createCategoryDistribution(trends) {
  // Get categories and count trends in each
  const categoryMap = {};
  trends.forEach(trend => {
    categoryMap[trend.category] = (categoryMap[trend.category] || 0) + 1;
  });
  
  // Prepare chart data
  const labels = Object.keys(categoryMap).map(cat => cat.charAt(0).toUpperCase() + cat.slice(1));
  const values = Object.values(categoryMap);
  
  // Set colors based on category names
  const colors = Object.keys(categoryMap).map(cat => trendViz.categoryColors[cat] || '#666');
  
  // Create chart
  trendViz.createPieChart('category-distribution', { labels, values }, {
    colors: colors,
    donut: true,
    holeSize: 0.4,
    showLabels: true,
    showPercentages: true
  });
}

/**
 * Create the virality radar chart
 * @param {Array} trends - Filtered trends
 */
function createViralityRadar(trends) {
  // Get categories and average virality in each
  const categoryMap = {};
  const categoryCount = {};
  
  trends.forEach(trend => {
    if (!categoryMap[trend.category]) {
      categoryMap[trend.category] = 0;
      categoryCount[trend.category] = 0;
    }
    categoryMap[trend.category] += trend.virality_score;
    categoryCount[trend.category]++;
  });
  
  // Calculate average virality for each category
  const categories = Object.keys(categoryMap);
  categories.forEach(cat => {
    categoryMap[cat] = categoryCount[cat] > 0 
      ? categoryMap[cat] / categoryCount[cat]
      : 0;
  });
  
  // Prepare chart data
  const radarData = [{
    name: 'Average Virality',
    categories: categories.map(cat => cat.charAt(0).toUpperCase() + cat.slice(1)),
    values: categories.map(cat => categoryMap[cat])
  }];
  
  // Create chart
  trendViz.createRadarChart('virality-radar', radarData, {
    colors: ['#2E7D32'],
    bgFill: 0.2,
    showLegend: false,
    maxValue: 100
  });
}

/**
 * Update the trend table with filtered data
 * @param {Array} trends - Filtered trends
 */
function updateTrendTable(trends) {
  const tableBody = document.querySelector('#trend-table tbody');
  
  // Clear table
  tableBody.innerHTML = '';
  
  // Sort trends by virality score (descending)
  const sortedTrends = [...trends].sort((a, b) => b.virality_score - a.virality_score);
  
  // Populate table
  sortedTrends.forEach((trend, index) => {
    const row = document.createElement('tr');
    
    // Define direction icon and class
    const directionIcon = trend.direction === 'increasing' 
      ? '<i class="bi bi-arrow-up-right text-success"></i>' 
      : '<i class="bi bi-arrow-down-right text-danger"></i>';
    
    const durationMap = {
      'short': 'Short-term',
      'medium': 'Medium-term',
      'long': 'Long-term'
    };
    
    // Create table row
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${trend.name}</td>
      <td>
        <span class="badge rounded-pill" style="background-color: ${trendViz.categoryColors[trend.category] || '#666'}">
          ${trend.category.charAt(0).toUpperCase() + trend.category.slice(1)}
        </span>
      </td>
      <td>
        <div class="progress" style="height: 8px;">
          <div class="progress-bar bg-success" role="progressbar" style="width: ${trend.virality_score}%"></div>
        </div>
        <span class="small">${trend.virality_score}</span>
      </td>
      <td>${directionIcon} ${trend.direction.charAt(0).toUpperCase() + trend.direction.slice(1)}</td>
      <td>${durationMap[trend.duration] || trend.duration}</td>
      <td>${formatDate(new Date(trend.date), 'medium')}</td>
    `;
    
    tableBody.appendChild(row);
  });
  
  // Show empty state if no trends
  if (sortedTrends.length === 0) {
    const emptyRow = document.createElement('tr');
    emptyRow.innerHTML = `
      <td colspan="7" class="text-center py-4">
        <i class="bi bi-search me-2"></i>
        No trends match the current filters. Try adjusting your filter criteria.
      </td>
    `;
    tableBody.appendChild(emptyRow);
  }
}

/**
 * Initialize export functionality
 */
function initExport() {
  const exportButtons = document.querySelectorAll('[data-export]');
  
  exportButtons.forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault();
      const exportType = button.getAttribute('data-export');
      
      switch (exportType) {
        case 'csv':
          exportTrendsCSV();
          break;
        case 'json':
          exportTrendsJSON();
          break;
        case 'pdf':
          showNotification('PDF export will be available in a future update', 'info');
          break;
      }
    });
  });
}

/**
 * Export trends data as CSV
 */
function exportTrendsCSV() {
  // Apply current filters
  const filteredTrends = filterTrends(state.trends, state.filters);
  
  // Create CSV header
  let csv = 'Name,Category,Virality Score,Direction,Duration,Date\n';
  
  // Add rows
  filteredTrends.forEach(trend => {
    const row = [
      `"${trend.name}"`,
      trend.category,
      trend.virality_score,
      trend.direction,
      trend.duration,
      new Date(trend.date).toLocaleDateString()
    ];
    csv += row.join(',') + '\n';
  });
  
  // Download file
  downloadFile(csv, 'sustainatrend_trends.csv', 'text/csv');
  
  // Show notification
  showNotification('Trends exported as CSV', 'success');
}

/**
 * Export trends data as JSON
 */
function exportTrendsJSON() {
  // Apply current filters
  const filteredTrends = filterTrends(state.trends, state.filters);
  
  // Convert to JSON
  const json = JSON.stringify(filteredTrends, null, 2);
  
  // Download file
  downloadFile(json, 'sustainatrend_trends.json', 'application/json');
  
  // Show notification
  showNotification('Trends exported as JSON', 'success');
}

/**
 * Initialize filter modal
 */
function initFilterModal() {
  // Get filter button and modal elements
  const filterButton = document.querySelector('[data-action="filter"]');
  const filterModal = document.getElementById('filter-modal');
  const closeModal = document.getElementById('close-modal');
  const applyFilters = document.getElementById('apply-filters');
  const resetFilters = document.getElementById('reset-filters');
  const viralitySlider = document.getElementById('virality-slider');
  const viralityValue = document.getElementById('virality-value');
  
  // Show modal when filter button is clicked
  if (filterButton && filterModal) {
    filterButton.addEventListener('click', () => {
      filterModal.classList.add('show');
    });
  }
  
  // Close modal when close button is clicked
  if (closeModal && filterModal) {
    closeModal.addEventListener('click', () => {
      filterModal.classList.remove('show');
    });
  }
  
  // Close modal when clicking outside
  if (filterModal) {
    filterModal.addEventListener('click', (e) => {
      if (e.target === filterModal) {
        filterModal.classList.remove('show');
      }
    });
  }
  
  // Update virality slider value
  if (viralitySlider && viralityValue) {
    viralitySlider.value = state.filters.minVirality;
    viralityValue.textContent = state.filters.minVirality;
    
    viralitySlider.addEventListener('input', () => {
      viralityValue.textContent = viralitySlider.value;
    });
  }
  
  // Apply filters when apply button is clicked
  if (applyFilters) {
    applyFilters.addEventListener('click', () => {
      // Get selected timeframe
      const timeframeEl = document.querySelector('input[name="timeframe"]:checked');
      if (timeframeEl) {
        state.filters.timeframe = timeframeEl.value;
      }
      
      // Get selected categories
      const categoryEls = document.querySelectorAll('input[name="category"]:checked');
      state.filters.categories = Array.from(categoryEls).map(el => el.value);
      
      // Get virality slider value
      if (viralitySlider) {
        state.filters.minVirality = parseInt(viralitySlider.value);
      }
      
      // Update dashboard with new filters
      updateDashboard();
      
      // Close modal
      filterModal.classList.remove('show');
      
      // Show notification
      showNotification('Filters applied successfully', 'success');
    });
  }
  
  // Reset filters when reset button is clicked
  if (resetFilters) {
    resetFilters.addEventListener('click', () => {
      // Reset timeframe
      const timeframeEls = document.querySelectorAll('input[name="timeframe"]');
      timeframeEls.forEach(el => {
        el.checked = el.value === 'all';
      });
      
      // Reset categories
      const categoryEls = document.querySelectorAll('input[name="category"]');
      categoryEls.forEach(el => {
        el.checked = true;
      });
      
      // Reset virality slider
      if (viralitySlider && viralityValue) {
        viralitySlider.value = 30;
        viralityValue.textContent = '30';
      }
    });
  }
}

/**
 * Initialize chart control events
 */
function initChartControls() {
  const chartTimeRange = document.getElementById('chart-time-range');
  const tableFilter = document.getElementById('table-category-filter');
  const refreshTable = document.getElementById('refresh-table');
  
  // Update chart when time range changes
  if (chartTimeRange) {
    chartTimeRange.addEventListener('change', () => {
      state.chartTimeRange = chartTimeRange.value;
      createTrendChart(filterTrends(state.trends, state.filters));
    });
  }
  
  // Filter table when category filter changes
  if (tableFilter) {
    tableFilter.addEventListener('change', () => {
      const category = tableFilter.value;
      
      if (category === 'all') {
        // Show all trends
        updateTrendTable(filterTrends(state.trends, state.filters));
      } else {
        // Filter by selected category
        const filteredTrends = filterTrends(state.trends, state.filters)
          .filter(trend => trend.category === category);
        updateTrendTable(filteredTrends);
      }
    });
  }
  
  // Refresh table
  if (refreshTable) {
    refreshTable.addEventListener('click', () => {
      // Reload data and update table
      fetchTrendData();
      
      // Show loading in the button
      const originalText = refreshTable.innerHTML;
      refreshTable.innerHTML = '<i class="bi bi-arrow-clockwise spin-animation"></i> Loading...';
      refreshTable.disabled = true;
      
      // Reset button after 2 seconds
      setTimeout(() => {
        refreshTable.innerHTML = originalText;
        refreshTable.disabled = false;
      }, 2000);
    });
  }
}

/**
 * Show/hide loading state
 * @param {boolean} isLoading - Whether to show or hide loading state
 */
function showLoading(isLoading) {
  // Get loading elements
  const loadingElements = document.querySelectorAll('.placeholder-glow');
  
  if (isLoading) {
    // Show loading state
    loadingElements.forEach(el => {
      el.style.display = 'block';
    });
  } else {
    // Hide loading state
    loadingElements.forEach(el => {
      el.style.display = 'none';
    });
  }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', initTrendAnalysis);