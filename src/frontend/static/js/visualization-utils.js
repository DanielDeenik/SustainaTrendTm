/**
 * SustainaTrend™ Visualization Utilities
 * Common visualization functions for consistent chart styling across the platform
 */

// Create a namespace for the visualization utilities
const trendViz = {};

// Define default color scheme for sustainability categories
trendViz.categoryColors = {
  emissions: 'rgb(16, 185, 129)', // green
  energy: 'rgb(14, 165, 233)',     // blue
  water: 'rgb(6, 182, 212)',       // cyan
  waste: 'rgb(100, 116, 139)',     // slate
  social: 'rgb(124, 58, 237)',     // purple
  governance: 'rgb(225, 29, 72)'   // red
};

// Default chart style settings
trendViz.chartDefaults = {
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  fontSize: 12,
  gridColor: 'rgba(0, 0, 0, 0.1)',
  darkModeGridColor: 'rgba(255, 255, 255, 0.1)',
  tickColor: '#666',
  darkModeTickColor: '#a5a5a5',
  padding: 20,
  animation: {
    duration: 800,
    easing: 'easeOutQuart'
  }
};

/**
 * Initialize tooltips for the current page
 * Compatible with Bootstrap 5
 */
function initTooltips() {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  if (tooltipTriggerList.length > 0) {
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
  }
}

/**
 * Initialize card animations for the current page
 */
function initCardAnimation() {
  // Add hover effect to cards
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-5px)';
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'translateY(0)';
    });
  });
}

/**
 * Initialize notifications system
 */
function initNotifications() {
  // Create toast container if it doesn't exist
  if (!document.getElementById('toastContainer')) {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
  }
}

/**
 * Show a toast notification
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, error, warning, info)
 * @param {number} duration - Duration in ms
 */
function showNotification(message, type = 'info', duration = 3000) {
  // Use the common showToast function if available
  if (typeof showToast === 'function') {
    showToast(message, type, duration);
    return;
  }
  
  const toastContainer = document.getElementById('toastContainer');
  
  if (!toastContainer) {
    console.error('Toast container not found. Call initNotifications() first.');
    return;
  }
  
  // Create toast element
  const toastId = 'toast-' + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="toast-header bg-${type === 'error' ? 'danger' : type}${type === 'info' ? '' : ' text-white'}">
        <i class="bi ${getToastIcon(type)} me-2"></i>
        <strong class="me-auto">${capitalizeFirstLetter(type)}</strong>
        <small>${formatDate(new Date(), 'time')}</small>
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, { delay: duration });
  toast.show();
  
  // Remove toast from DOM after it's hidden
  toastElement.addEventListener('hidden.bs.toast', () => {
    toastElement.remove();
  });
}

/**
 * Get icon class for toast notification
 * @param {string} type - Toast type
 * @returns {string} Icon class
 */
function getToastIcon(type) {
  switch (type) {
    case 'success': return 'bi-check-circle-fill';
    case 'error': return 'bi-exclamation-triangle-fill';
    case 'warning': return 'bi-exclamation-circle-fill';
    case 'info': 
    default: return 'bi-info-circle-fill';
  }
}

/**
 * Capitalize first letter of a string
 * @param {string} string - String to capitalize
 * @returns {string} Capitalized string
 */
function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Format date for display if the common formatDate function is not available
 * @param {Date|string} date - Date to format
 * @param {string} format - Display format (short, medium, long, time)
 * @returns {string} Formatted date string
 */
function formatDate(date, format = 'medium') {
  // Use the common formatDate function if available
  if (typeof window.formatDate === 'function') {
    return window.formatDate(date, format);
  }
  
  const dateObj = date instanceof Date ? date : new Date(date);
  
  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString();
    case 'long':
      return dateObj.toLocaleDateString(undefined, { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    case 'time':
      return dateObj.toLocaleTimeString(undefined, { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    case 'medium':
    default:
      return dateObj.toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
  }
}

/**
 * Show or hide a loading spinner
 * @param {boolean} show - Whether to show or hide the spinner
 * @param {string} targetId - ID of the element to show/hide the spinner in (optional)
 */
function showLoading(show, targetId = null) {
  // If target ID is provided, show/hide spinner in that element
  if (targetId) {
    const target = document.getElementById(targetId);
    if (!target) return;
    
    // Remove existing spinner if any
    const existingSpinner = target.querySelector('.spinner-container');
    if (existingSpinner) {
      existingSpinner.remove();
    }
    
    // Add new spinner if needed
    if (show) {
      const spinner = `
        <div class="spinner-container position-absolute w-100 h-100 d-flex align-items-center justify-content-center bg-light bg-opacity-75">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
      `;
      target.style.position = 'relative';
      target.insertAdjacentHTML('beforeend', spinner);
    }
    
    return;
  }
  
  // Otherwise, show/hide the global spinner
  let spinner = document.getElementById('global-spinner');
  
  // Create global spinner if it doesn't exist
  if (!spinner && show) {
    spinner = document.createElement('div');
    spinner.id = 'global-spinner';
    spinner.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-light bg-opacity-75';
    spinner.style.zIndex = '9999';
    spinner.innerHTML = `
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    `;
    document.body.appendChild(spinner);
  }
  
  // Show/hide the spinner
  if (spinner) {
    spinner.style.display = show ? 'flex' : 'none';
  }
}

/**
 * Create a Plotly line chart with consistent styling
 * 
 * @param {string} elementId - HTML element ID to render chart
 * @param {Object} data - Chart data
 * @param {Object} options - Chart options
 * @returns {Object} Plotly chart instance
 */
trendViz.createLineChart = function(elementId, data, options = {}) {
  const isDarkMode = document.body.classList.contains('dark-mode');
  const element = document.getElementById(elementId);
  
  if (!element) {
    console.error(`Element with ID ${elementId} not found`);
    return null;
  }
  
  // Default options
  const defaults = {
    title: '',
    xAxisTitle: '',
    yAxisTitle: '',
    showLegend: true,
    legendPosition: 'top-right',
    colors: Object.values(trendViz.categoryColors),
    smoothing: 0.3,
    gridLines: true,
    responsive: true
  };
  
  // Merge defaults with provided options
  const chartOptions = { ...defaults, ...options };
  
  // Prepare layout
  const layout = {
    title: chartOptions.title ? {
      text: chartOptions.title,
      font: {
        family: trendViz.chartDefaults.fontFamily,
        size: 16,
        color: isDarkMode ? '#ECEFF1' : '#212121'
      }
    } : null,
    font: {
      family: trendViz.chartDefaults.fontFamily,
      size: trendViz.chartDefaults.fontSize,
      color: isDarkMode ? '#B0BEC5' : '#666666'
    },
    xaxis: {
      title: chartOptions.xAxisTitle,
      color: isDarkMode ? trendViz.chartDefaults.darkModeTickColor : trendViz.chartDefaults.tickColor,
      gridcolor: isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor,
      showgrid: chartOptions.gridLines,
      zeroline: false
    },
    yaxis: {
      title: chartOptions.yAxisTitle,
      color: isDarkMode ? trendViz.chartDefaults.darkModeTickColor : trendViz.chartDefaults.tickColor,
      gridcolor: isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor,
      showgrid: chartOptions.gridLines,
      zeroline: false
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: {
      l: trendViz.chartDefaults.padding + 30,
      r: trendViz.chartDefaults.padding,
      t: chartOptions.title ? trendViz.chartDefaults.padding + 30 : trendViz.chartDefaults.padding,
      b: trendViz.chartDefaults.padding + 30
    },
    showlegend: chartOptions.showLegend,
    legend: {
      orientation: 'h',
      x: chartOptions.legendPosition.includes('right') ? 1 : 0,
      y: chartOptions.legendPosition.includes('top') ? 1.1 : -0.2,
      xanchor: chartOptions.legendPosition.includes('right') ? 'right' : 'left',
      yanchor: chartOptions.legendPosition.includes('top') ? 'top' : 'bottom',
      bgcolor: 'rgba(255,255,255,0.1)',
      bordercolor: isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor,
      borderwidth: 1
    }
  };
  
  // Config options
  const config = {
    responsive: chartOptions.responsive,
    displayModeBar: true,
    modeBarButtonsToRemove: [
      'lasso2d', 
      'select2d', 
      'toggleSpikelines',
      'hoverClosestCartesian',
      'hoverCompareCartesian'
    ],
    displaylogo: false,
    toImageButtonOptions: {
      format: 'png',
      filename: 'sustainatrend_chart',
      height: 500,
      width: 700,
      scale: 2
    }
  };
  
  // Plot chart
  Plotly.newPlot(elementId, data, layout, config);
  
  // Return element for chaining
  return element;
}

/**
 * Create a Plotly pie chart with consistent styling
 * 
 * @param {string} elementId - HTML element ID to render chart
 * @param {Object} data - Chart data (labels and values)
 * @param {Object} options - Chart options
 * @returns {Object} Plotly chart instance
 */
trendViz.createPieChart = function(elementId, data, options = {}) {
  const isDarkMode = document.body.classList.contains('dark-mode');
  const element = document.getElementById(elementId);
  
  if (!element) {
    console.error(`Element with ID ${elementId} not found`);
    return null;
  }
  
  // Default options
  const defaults = {
    title: '',
    colors: Object.values(trendViz.categoryColors),
    donut: false,
    holeSize: 0.4,
    showLabels: true,
    showPercentages: true,
    responsive: true
  };
  
  // Merge defaults with provided options
  const chartOptions = { ...defaults, ...options };
  
  // Prepare trace data
  const trace = [{
    labels: data.labels,
    values: data.values,
    type: 'pie',
    textinfo: chartOptions.showLabels 
      ? (chartOptions.showPercentages ? 'label+percent' : 'label')
      : 'none',
    textposition: 'outside',
    textfont: {
      family: trendViz.chartDefaults.fontFamily,
      size: 12,
      color: isDarkMode ? '#ECEFF1' : '#212121'
    },
    marker: {
      colors: chartOptions.colors,
      line: {
        color: isDarkMode ? '#263238' : '#ffffff',
        width: 2
      }
    },
    hole: chartOptions.donut ? chartOptions.holeSize : 0,
    sort: false
  }];
  
  // Prepare layout
  const layout = {
    title: chartOptions.title ? {
      text: chartOptions.title,
      font: {
        family: trendViz.chartDefaults.fontFamily,
        size: 16,
        color: isDarkMode ? '#ECEFF1' : '#212121'
      }
    } : null,
    font: {
      family: trendViz.chartDefaults.fontFamily,
      size: trendViz.chartDefaults.fontSize,
      color: isDarkMode ? '#B0BEC5' : '#666666'
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: {
      l: trendViz.chartDefaults.padding,
      r: trendViz.chartDefaults.padding,
      t: chartOptions.title ? trendViz.chartDefaults.padding + 30 : trendViz.chartDefaults.padding,
      b: trendViz.chartDefaults.padding
    },
    showlegend: false,
    legend: {
      orientation: 'h',
      x: 0.5,
      y: -0.1,
      xanchor: 'center',
      yanchor: 'top'
    }
  };
  
  // Config options
  const config = {
    responsive: chartOptions.responsive,
    displayModeBar: false,
    displaylogo: false
  };
  
  // Plot chart
  Plotly.newPlot(elementId, trace, layout, config);
  
  // Return element for chaining
  return element;
}

/**
 * Create a Chart.js chart with consistent SustainaTrend styling
 * 
 * @param {string|object} elementId - Canvas element ID or reference
 * @param {string} type - Chart type (line, bar, pie, doughnut, radar, etc.)
 * @param {Object} data - Chart data object
 * @param {Object} options - Chart options
 * @returns {Object} Chart.js instance
 */
trendViz.createChart = function(elementId, type, data, options = {}) {
  const isDarkMode = document.body.classList.contains('dark-mode');
  const element = typeof elementId === 'string' ? document.getElementById(elementId) : elementId;
  
  if (!element) {
    console.error(`Element ${elementId} not found`);
    return null;
  }
  
  // Get canvas context
  const ctx = element.getContext('2d');
  
  // Get theme colors
  const textColor = isDarkMode ? '#ECEFF1' : '#212121';
  const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
  
  // Default options with SustainaTrend styling
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          font: {
            family: trendViz.chartDefaults.fontFamily,
            size: 12
          },
          color: textColor
        }
      },
      tooltip: {
        backgroundColor: isDarkMode ? 'rgba(30, 30, 30, 0.8)' : 'rgba(255, 255, 255, 0.8)',
        titleColor: isDarkMode ? '#ECEFF1' : '#212121',
        bodyColor: isDarkMode ? '#B0BEC5' : '#666666',
        borderColor: gridColor,
        borderWidth: 1
      }
    },
    scales: type !== 'pie' && type !== 'doughnut' ? {
      x: {
        grid: {
          color: gridColor
        },
        ticks: {
          font: {
            family: trendViz.chartDefaults.fontFamily,
            size: 12
          },
          color: textColor
        }
      },
      y: {
        grid: {
          color: gridColor
        },
        ticks: {
          font: {
            family: trendViz.chartDefaults.fontFamily,
            size: 12
          },
          color: textColor
        },
        beginAtZero: true
      }
    } : {}
  };
  
  // Get category colors if data doesn't specify colors
  if (data.datasets) {
    data.datasets.forEach((dataset, index) => {
      // Apply theme-aware colors if not specified
      if (!dataset.backgroundColor) {
        const categoryKeys = Object.keys(trendViz.categoryColors);
        const colorKey = dataset.label?.toLowerCase().includes('emissions') ? 'emissions' :
                        dataset.label?.toLowerCase().includes('energy') ? 'energy' :
                        dataset.label?.toLowerCase().includes('water') ? 'water' :
                        dataset.label?.toLowerCase().includes('social') ? 'social' :
                        dataset.label?.toLowerCase().includes('governance') ? 'governance' :
                        'waste';
        
        const color = trendViz.categoryColors[colorKey] || 
                      trendViz.categoryColors[categoryKeys[index % categoryKeys.length]];
                      
        // For line charts
        if (type === 'line') {
          dataset.borderColor = color;
          dataset.backgroundColor = color.replace('rgb', 'rgba').replace(')', ', 0.2)');
        } 
        // For bar, pie, doughnut charts
        else {
          dataset.backgroundColor = Array.isArray(dataset.data) 
            ? dataset.data.map((_, i) => {
                const categoryColor = trendViz.categoryColors[categoryKeys[i % categoryKeys.length]];
                return categoryColor;
              })
            : color;
        }
      }
    });
  }
  
  // Merge default options with user options
  const mergedOptions = deepMerge(defaultOptions, options);
  
  // Create and return the chart
  return new Chart(ctx, {
    type: type,
    data: data,
    options: mergedOptions
  });
};

/**
 * Deep merge two objects
 * @param {Object} target - Target object
 * @param {Object} source - Source object
 * @returns {Object} Merged object
 */
function deepMerge(target, source) {
  const output = Object.assign({}, target);
  
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach(key => {
      if (isObject(source[key])) {
        if (!(key in target))
          Object.assign(output, { [key]: source[key] });
        else
          output[key] = deepMerge(target[key], source[key]);
      } else {
        Object.assign(output, { [key]: source[key] });
      }
    });
  }
  
  return output;
}

/**
 * Check if value is an object
 * @param {*} item - Value to check
 * @returns {boolean} True if object
 */
function isObject(item) {
  return (item && typeof item === 'object' && !Array.isArray(item));
}

/**
 * Create a Plotly radar chart with consistent styling
 * 
 * @param {string} elementId - HTML element ID to render chart
 * @param {Object} data - Chart data (categories and values)
 * @param {Object} options - Chart options
 * @returns {Object} Plotly chart instance
 */
trendViz.createRadarChart = function(elementId, data, options = {}) {
  const isDarkMode = document.body.classList.contains('dark-mode');
  const element = document.getElementById(elementId);
  
  if (!element) {
    console.error(`Element with ID ${elementId} not found`);
    return null;
  }
  
  // Default options
  const defaults = {
    title: '',
    colors: ['rgb(46, 125, 50)'], // SustainaTrend primary green
    bgFill: 0.2,
    showLegend: true,
    responsive: true,
    maxValue: null // Auto-scale
  };
  
  // Merge defaults with provided options
  const chartOptions = { ...defaults, ...options };
  
  // Prepare trace data
  const traces = data.map((series, index) => ({
    type: 'scatterpolar',
    name: series.name,
    r: series.values,
    theta: series.categories,
    fill: 'toself',
    fillcolor: `rgba(${trendViz.hexToRgb(chartOptions.colors[index % chartOptions.colors.length])}, ${chartOptions.bgFill})`,
    line: {
      color: chartOptions.colors[index % chartOptions.colors.length],
      width: 2
    }
  }));
  
  // Prepare layout
  const layout = {
    title: chartOptions.title ? {
      text: chartOptions.title,
      font: {
        family: trendViz.chartDefaults.fontFamily,
        size: 16,
        color: isDarkMode ? '#ECEFF1' : '#212121'
      }
    } : null,
    font: {
      family: trendViz.chartDefaults.fontFamily,
      size: trendViz.chartDefaults.fontSize,
      color: isDarkMode ? '#B0BEC5' : '#666666'
    },
    polar: {
      radialaxis: {
        visible: true,
        range: chartOptions.maxValue ? [0, chartOptions.maxValue] : null,
        gridcolor: isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor,
        linecolor: isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor
      },
      angularaxis: {
        gridcolor: isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor,
        linecolor: isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor
      },
      bgcolor: 'rgba(0,0,0,0)'
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: {
      l: trendViz.chartDefaults.padding,
      r: trendViz.chartDefaults.padding,
      t: chartOptions.title ? trendViz.chartDefaults.padding + 30 : trendViz.chartDefaults.padding,
      b: trendViz.chartDefaults.padding
    },
    showlegend: chartOptions.showLegend && data.length > 1,
    legend: {
      orientation: 'h',
      x: 0.5,
      y: -0.1,
      xanchor: 'center',
      yanchor: 'top'
    }
  };
  
  // Config options
  const config = {
    responsive: chartOptions.responsive,
    displayModeBar: false,
    displaylogo: false
  };
  
  // Plot chart
  Plotly.newPlot(elementId, traces, layout, config);
  
  // Return element for chaining
  return element;
}

/**
 * Create a Plotly bar chart with consistent styling
 * 
 * @param {string} elementId - HTML element ID to render chart
 * @param {Object} data - Chart data
 * @param {Object} options - Chart options
 * @returns {Object} Plotly chart instance
 */
trendViz.createBarChart = function(elementId, data, options = {}) {
  const isDarkMode = document.body.classList.contains('dark-mode');
  const element = document.getElementById(elementId);
  
  if (!element) {
    console.error(`Element with ID ${elementId} not found`);
    return null;
  }
  
  // Default options
  const defaults = {
    title: '',
    xAxisTitle: '',
    yAxisTitle: '',
    horizontal: false,
    stacked: false,
    colors: Object.values(trendViz.categoryColors),
    showLegend: true,
    legendPosition: 'top-right',
    gridLines: true,
    responsive: true
  };
  
  // Merge defaults with provided options
  const chartOptions = { ...defaults, ...options };
  
  // Prepare layout
  const layout = {
    title: chartOptions.title ? {
      text: chartOptions.title,
      font: {
        family: trendViz.chartDefaults.fontFamily,
        size: 16,
        color: isDarkMode ? '#ECEFF1' : '#212121'
      }
    } : null,
    font: {
      family: trendViz.chartDefaults.fontFamily,
      size: trendViz.chartDefaults.fontSize,
      color: isDarkMode ? '#B0BEC5' : '#666666'
    },
    xaxis: {
      title: chartOptions.xAxisTitle,
      color: isDarkMode ? trendViz.chartDefaults.darkModeTickColor : trendViz.chartDefaults.tickColor,
      gridcolor: isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor,
      showgrid: chartOptions.horizontal && chartOptions.gridLines,
      zeroline: false
    },
    yaxis: {
      title: chartOptions.yAxisTitle,
      color: isDarkMode ? trendViz.chartDefaults.darkModeTickColor : trendViz.chartDefaults.tickColor,
      gridcolor: isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor,
      showgrid: !chartOptions.horizontal && chartOptions.gridLines,
      zeroline: false
    },
    barmode: chartOptions.stacked ? 'stack' : 'group',
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: {
      l: trendViz.chartDefaults.padding + 30,
      r: trendViz.chartDefaults.padding,
      t: chartOptions.title ? trendViz.chartDefaults.padding + 30 : trendViz.chartDefaults.padding,
      b: trendViz.chartDefaults.padding + 30
    },
    showlegend: chartOptions.showLegend,
    legend: {
      orientation: 'h',
      x: chartOptions.legendPosition.includes('right') ? 1 : 0,
      y: chartOptions.legendPosition.includes('top') ? 1.1 : -0.2,
      xanchor: chartOptions.legendPosition.includes('right') ? 'right' : 'left',
      yanchor: chartOptions.legendPosition.includes('top') ? 'top' : 'bottom',
      bgcolor: 'rgba(255,255,255,0.1)',
      bordercolor: isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor,
      borderwidth: 1
    }
  };
  
  // Config options
  const config = {
    responsive: chartOptions.responsive,
    displayModeBar: true,
    modeBarButtonsToRemove: [
      'lasso2d', 
      'select2d', 
      'toggleSpikelines',
      'hoverClosestCartesian',
      'hoverCompareCartesian'
    ],
    displaylogo: false,
    toImageButtonOptions: {
      format: 'png',
      filename: 'sustainatrend_chart',
      height: 500,
      width: 700,
      scale: 2
    }
  };
  
  // Plot chart
  Plotly.newPlot(elementId, data, layout, config);
  
  // Return element for chaining
  return element;
}

/**
 * Update chart theme based on dark/light mode
 * @param {string} elementId - Chart element ID
 */
trendViz.updateChartTheme = function(elementId) {
  const isDarkMode = document.body.classList.contains('dark-mode');
  const chart = document.getElementById(elementId);
  
  if (!chart || !chart.layout) return;
  
  const update = {
    'font.color': isDarkMode ? '#B0BEC5' : '#666666',
    'xaxis.color': isDarkMode ? trendViz.chartDefaults.darkModeTickColor : trendViz.chartDefaults.tickColor,
    'yaxis.color': isDarkMode ? trendViz.chartDefaults.darkModeTickColor : trendViz.chartDefaults.tickColor,
    'xaxis.gridcolor': isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor,
    'yaxis.gridcolor': isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor
  };
  
  // Only update title if it exists
  if (chart.layout.title) {
    update['title.font.color'] = isDarkMode ? '#ECEFF1' : '#212121';
  }
  
  // Update radar chart if it's a polar chart
  if (chart.layout.polar) {
    update['polar.radialaxis.gridcolor'] = isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor;
    update['polar.radialaxis.linecolor'] = isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor;
    update['polar.angularaxis.gridcolor'] = isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor;
    update['polar.angularaxis.linecolor'] = isDarkMode ? trendViz.chartDefaults.darkModeGridColor : trendViz.chartDefaults.gridColor;
  }
  
  Plotly.relayout(elementId, update);
}

/**
 * Update all charts when theme changes
 */
trendViz.updateAllCharts = function() {
  // Find all Plotly chart divs
  const chartDivs = document.querySelectorAll('[id^="chart-"], [id$="-chart"], [id*="-chart-"]');
  chartDivs.forEach(div => {
    if (div._fullData) { // Check if this is a Plotly div
      trendViz.updateChartTheme(div.id);
    }
  });
};

/**
 * Helper function to convert hex color to RGB
 * @param {string} hex - Hex color string
 * @returns {string} RGB values as comma-separated string
 */
trendViz.hexToRgb = function(hex) {
  // Default to green if conversion fails
  if (!hex || typeof hex !== 'string') return '46, 125, 50';
  
  // Remove # if present
  hex = hex.replace('#', '');
  
  // Convert 3-digit hex to 6-digits
  if (hex.length === 3) {
    hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
  }
  
  // Convert hex to RGB
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  
  return `${r}, ${g}, ${b}`;
};

/**
 * Initialize all visualization components
 * Call this function when the page loads to set up charts and tooltips
 */
trendViz.init = function() {
  // Initialize tooltips
  initTooltips();
  
  // Initialize card animations
  initCardAnimation();
  
  // Initialize notifications
  initNotifications();
  
  // Set up dark mode listeners for charts
  const darkModeToggle = document.getElementById('darkModeToggle');
  if (darkModeToggle) {
    darkModeToggle.addEventListener('click', trendViz.updateAllCharts);
  }
  
  // Return for chaining
  return trendViz;
};

// Auto-initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
  trendViz.init();
});

// Make helper utilities available
trendViz.showNotification = showNotification;
trendViz.showLoading = showLoading;
trendViz.initTooltips = initTooltips;
trendViz.initCardAnimation = initCardAnimation;
trendViz.initNotifications = initNotifications;

// Export trendViz to global scope
window.trendViz = trendViz;