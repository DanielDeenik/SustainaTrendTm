/**
 * SustainaTrend™ Visualization Utilities
 * Common visualization functions for consistent chart styling across the platform
 */

// Define default color scheme for sustainability categories
const categoryColors = {
  emissions: 'rgb(16, 185, 129)', // green
  energy: 'rgb(14, 165, 233)',     // blue
  water: 'rgb(6, 182, 212)',       // cyan
  waste: 'rgb(100, 116, 139)',     // slate
  social: 'rgb(124, 58, 237)',     // purple
  governance: 'rgb(225, 29, 72)'   // red
};

// Default chart style settings
const chartDefaults = {
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
 * Create a Plotly line chart with consistent styling
 * 
 * @param {string} elementId - HTML element ID to render chart
 * @param {Object} data - Chart data
 * @param {Object} options - Chart options
 * @returns {Object} Plotly chart instance
 */
function createLineChart(elementId, data, options = {}) {
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
    colors: Object.values(categoryColors),
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
        family: chartDefaults.fontFamily,
        size: 16,
        color: isDarkMode ? '#ECEFF1' : '#212121'
      }
    } : null,
    font: {
      family: chartDefaults.fontFamily,
      size: chartDefaults.fontSize,
      color: isDarkMode ? '#B0BEC5' : '#666666'
    },
    xaxis: {
      title: chartOptions.xAxisTitle,
      color: isDarkMode ? chartDefaults.darkModeTickColor : chartDefaults.tickColor,
      gridcolor: isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor,
      showgrid: chartOptions.gridLines,
      zeroline: false
    },
    yaxis: {
      title: chartOptions.yAxisTitle,
      color: isDarkMode ? chartDefaults.darkModeTickColor : chartDefaults.tickColor,
      gridcolor: isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor,
      showgrid: chartOptions.gridLines,
      zeroline: false
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: {
      l: chartDefaults.padding + 30,
      r: chartDefaults.padding,
      t: chartOptions.title ? chartDefaults.padding + 30 : chartDefaults.padding,
      b: chartDefaults.padding + 30
    },
    showlegend: chartOptions.showLegend,
    legend: {
      orientation: 'h',
      x: chartOptions.legendPosition.includes('right') ? 1 : 0,
      y: chartOptions.legendPosition.includes('top') ? 1.1 : -0.2,
      xanchor: chartOptions.legendPosition.includes('right') ? 'right' : 'left',
      yanchor: chartOptions.legendPosition.includes('top') ? 'top' : 'bottom',
      bgcolor: 'rgba(255,255,255,0.1)',
      bordercolor: isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor,
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
function createPieChart(elementId, data, options = {}) {
  const isDarkMode = document.body.classList.contains('dark-mode');
  const element = document.getElementById(elementId);
  
  if (!element) {
    console.error(`Element with ID ${elementId} not found`);
    return null;
  }
  
  // Default options
  const defaults = {
    title: '',
    colors: Object.values(categoryColors),
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
      family: chartDefaults.fontFamily,
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
        family: chartDefaults.fontFamily,
        size: 16,
        color: isDarkMode ? '#ECEFF1' : '#212121'
      }
    } : null,
    font: {
      family: chartDefaults.fontFamily,
      size: chartDefaults.fontSize,
      color: isDarkMode ? '#B0BEC5' : '#666666'
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: {
      l: chartDefaults.padding,
      r: chartDefaults.padding,
      t: chartOptions.title ? chartDefaults.padding + 30 : chartDefaults.padding,
      b: chartDefaults.padding
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
 * Create a Plotly radar chart with consistent styling
 * 
 * @param {string} elementId - HTML element ID to render chart
 * @param {Object} data - Chart data (categories and values)
 * @param {Object} options - Chart options
 * @returns {Object} Plotly chart instance
 */
function createRadarChart(elementId, data, options = {}) {
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
    fillcolor: `rgba(${hexToRgb(chartOptions.colors[index % chartOptions.colors.length])}, ${chartOptions.bgFill})`,
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
        family: chartDefaults.fontFamily,
        size: 16,
        color: isDarkMode ? '#ECEFF1' : '#212121'
      }
    } : null,
    font: {
      family: chartDefaults.fontFamily,
      size: chartDefaults.fontSize,
      color: isDarkMode ? '#B0BEC5' : '#666666'
    },
    polar: {
      radialaxis: {
        visible: true,
        range: chartOptions.maxValue ? [0, chartOptions.maxValue] : null,
        gridcolor: isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor,
        linecolor: isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor
      },
      angularaxis: {
        gridcolor: isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor,
        linecolor: isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor
      },
      bgcolor: 'rgba(0,0,0,0)'
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: {
      l: chartDefaults.padding,
      r: chartDefaults.padding,
      t: chartOptions.title ? chartDefaults.padding + 30 : chartDefaults.padding,
      b: chartDefaults.padding
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
function createBarChart(elementId, data, options = {}) {
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
    colors: Object.values(categoryColors),
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
        family: chartDefaults.fontFamily,
        size: 16,
        color: isDarkMode ? '#ECEFF1' : '#212121'
      }
    } : null,
    font: {
      family: chartDefaults.fontFamily,
      size: chartDefaults.fontSize,
      color: isDarkMode ? '#B0BEC5' : '#666666'
    },
    xaxis: {
      title: chartOptions.xAxisTitle,
      color: isDarkMode ? chartDefaults.darkModeTickColor : chartDefaults.tickColor,
      gridcolor: isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor,
      showgrid: chartOptions.horizontal && chartOptions.gridLines,
      zeroline: false
    },
    yaxis: {
      title: chartOptions.yAxisTitle,
      color: isDarkMode ? chartDefaults.darkModeTickColor : chartDefaults.tickColor,
      gridcolor: isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor,
      showgrid: !chartOptions.horizontal && chartOptions.gridLines,
      zeroline: false
    },
    barmode: chartOptions.stacked ? 'stack' : 'group',
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: {
      l: chartDefaults.padding + 30,
      r: chartDefaults.padding,
      t: chartOptions.title ? chartDefaults.padding + 30 : chartDefaults.padding,
      b: chartDefaults.padding + 30
    },
    showlegend: chartOptions.showLegend,
    legend: {
      orientation: 'h',
      x: chartOptions.legendPosition.includes('right') ? 1 : 0,
      y: chartOptions.legendPosition.includes('top') ? 1.1 : -0.2,
      xanchor: chartOptions.legendPosition.includes('right') ? 'right' : 'left',
      yanchor: chartOptions.legendPosition.includes('top') ? 'top' : 'bottom',
      bgcolor: 'rgba(255,255,255,0.1)',
      bordercolor: isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor,
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
function updateChartTheme(elementId) {
  const isDarkMode = document.body.classList.contains('dark-mode');
  const chart = document.getElementById(elementId);
  
  if (!chart || !chart.layout) return;
  
  const update = {
    'font.color': isDarkMode ? '#B0BEC5' : '#666666',
    'xaxis.color': isDarkMode ? chartDefaults.darkModeTickColor : chartDefaults.tickColor,
    'yaxis.color': isDarkMode ? chartDefaults.darkModeTickColor : chartDefaults.tickColor,
    'xaxis.gridcolor': isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor,
    'yaxis.gridcolor': isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor
  };
  
  // Only update title if it exists
  if (chart.layout.title) {
    update['title.font.color'] = isDarkMode ? '#ECEFF1' : '#212121';
  }
  
  // Update radar chart if it's a polar chart
  if (chart.layout.polar) {
    update['polar.radialaxis.gridcolor'] = isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor;
    update['polar.radialaxis.linecolor'] = isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor;
    update['polar.angularaxis.gridcolor'] = isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor;
    update['polar.angularaxis.linecolor'] = isDarkMode ? chartDefaults.darkModeGridColor : chartDefaults.gridColor;
  }
  
  Plotly.relayout(elementId, update);
}

/**
 * Update all charts when theme changes
 */
function updateAllCharts() {
  // Find all Plotly chart divs
  const chartDivs = document.querySelectorAll('[id^="chart-"], [id$="-chart"], [id*="-chart-"]');
  chartDivs.forEach(div => {
    if (div._fullData) { // Check if this is a Plotly div
      updateChartTheme(div.id);
    }
  });
}

/**
 * Helper function to convert hex color to RGB
 * @param {string} hex - Hex color string
 * @returns {string} RGB values as comma-separated string
 */
function hexToRgb(hex) {
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
}

// Initialize theme detection for charts
document.addEventListener('DOMContentLoaded', function() {
  // Add listener for dark mode toggle
  const darkModeToggle = document.getElementById('darkModeToggle');
  if (darkModeToggle) {
    darkModeToggle.addEventListener('click', updateAllCharts);
  }
});

// Export functions for use in other scripts
window.trendViz = {
  createLineChart,
  createPieChart,
  createRadarChart,
  createBarChart,
  updateChartTheme,
  updateAllCharts,
  categoryColors
};