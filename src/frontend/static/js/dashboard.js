/**
 * SustainaTrend™ Dashboard JavaScript
 * Provides functionality for the dashboard UI
 */

// Global chart instances for reference
let metricsChart = null;
let categoryChart = null;

/**
 * Initialize dashboard charts
 * @param {Array} metricsData - The metrics data from the API
 */
function initCharts(metricsData) {
    initMetricsChart(metricsData);
    initCategoryChart(metricsData);
    
    // Set up chart type switcher
    document.querySelectorAll('[data-chart-type]').forEach(button => {
        button.addEventListener('click', function() {
            const chartType = this.getAttribute('data-chart-type');
            updateChartType(chartType);
            
            // Update active state
            document.querySelectorAll('[data-chart-type]').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
        });
    });
    
    // Set up theme change listener to update charts
    document.addEventListener('themeChanged', (e) => {
        updateChartTheme(e.detail.theme === 'dark');
    });
}

/**
 * Initialize the metrics chart
 * @param {Array} metricsData - The metrics data from the API
 */
function initMetricsChart(metricsData) {
    // Get the most recent 12 months of data for each category
    const chartData = processMetricsForChart(metricsData, 12);
    
    // Set up the dark mode compatible theme
    const isDarkMode = document.documentElement.classList.contains('dark-mode');
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    const textColor = isDarkMode ? '#e0e0e0' : '#666666';
    
    // Get the canvas context
    const ctx = document.getElementById('metrics-chart').getContext('2d');
    
    // Create the chart
    metricsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: chartData.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false // We'll use a custom legend
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: isDarkMode ? 'rgba(45, 45, 45, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                    titleColor: isDarkMode ? '#e0e0e0' : '#333333',
                    bodyColor: isDarkMode ? '#cccccc' : '#666666',
                    borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    boxPadding: 5,
                    padding: 10,
                    cornerRadius: 4,
                    bodyFont: {
                        size: 13
                    },
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(1);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            hover: {
                mode: 'index',
                intersect: false
            }
        }
    });
    
    // Create custom legends
    createCustomLegend(chartData.datasets);
}

/**
 * Initialize the category distribution chart
 * @param {Array} metricsData - The metrics data from the API
 */
function initCategoryChart(metricsData) {
    // Process data for the category chart
    const categoryData = processCategoryDistribution(metricsData);
    
    // Set up the dark mode compatible theme
    const isDarkMode = document.documentElement.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#e0e0e0' : '#666666';
    
    // Get the canvas context
    const ctx = document.getElementById('category-chart').getContext('2d');
    
    // Create the chart
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categoryData.labels,
            datasets: [{
                data: categoryData.data,
                backgroundColor: categoryData.colors,
                borderColor: isDarkMode ? '#2d2d2d' : '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: textColor,
                        font: {
                            size: 12
                        },
                        padding: 15,
                        boxWidth: 12,
                        boxHeight: 12
                    }
                },
                tooltip: {
                    backgroundColor: isDarkMode ? 'rgba(45, 45, 45, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                    titleColor: isDarkMode ? '#e0e0e0' : '#333333',
                    bodyColor: isDarkMode ? '#cccccc' : '#666666',
                    borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    boxPadding: 5,
                    padding: 10,
                    cornerRadius: 4,
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            let value = context.parsed || 0;
                            let total = context.dataset.data.reduce((a, b) => a + b, 0);
                            let percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '70%'
        }
    });
}

/**
 * Process metrics data for chart display
 * @param {Array} metricsData - Raw metrics data from the API
 * @param {number} months - Number of months to include
 * @returns {Object} Processed chart data
 */
function processMetricsForChart(metricsData, months = 12) {
    // Group metrics by category
    const categories = {};
    const dateLabels = new Set();
    
    // First pass: collect all dates and categorize metrics
    metricsData.forEach(metric => {
        const category = metric.category || 'Uncategorized';
        const date = new Date(metric.timestamp);
        const dateStr = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
        
        dateLabels.add(dateStr);
        
        if (!categories[category]) {
            categories[category] = {};
        }
        
        if (!categories[category][dateStr]) {
            categories[category][dateStr] = [];
        }
        
        categories[category][dateStr].push(metric.value);
    });
    
    // Convert date labels to array and sort chronologically
    const sortedLabels = Array.from(dateLabels).sort();
    
    // Limit to the last X months
    const limitedLabels = sortedLabels.slice(-months);
    
    // Create datasets - use trendViz colors if available
    const categoryColors = trendViz && trendViz.categoryColors ? {
        'Emissions': trendViz.categoryColors.emissions.replace('rgb', 'rgba').replace(')', ', 0.7)'),
        'Water': trendViz.categoryColors.water.replace('rgb', 'rgba').replace(')', ', 0.7)'),
        'Energy': trendViz.categoryColors.energy.replace('rgb', 'rgba').replace(')', ', 0.7)'),
        'Waste': trendViz.categoryColors.waste.replace('rgb', 'rgba').replace(')', ', 0.7)'),
        'Social': trendViz.categoryColors.social.replace('rgb', 'rgba').replace(')', ', 0.7)'),
        'Governance': trendViz.categoryColors.governance.replace('rgb', 'rgba').replace(')', ', 0.7)')
    } : {
        'Emissions': 'rgba(220, 53, 69, 0.7)', // Red
        'Water': 'rgba(13, 202, 240, 0.7)',    // Light blue
        'Energy': 'rgba(255, 193, 7, 0.7)',    // Yellow
        'Waste': 'rgba(25, 135, 84, 0.7)',     // Green
        'Social': 'rgba(13, 110, 253, 0.7)',   // Blue
        'Governance': 'rgba(108, 117, 125, 0.7)' // Gray
    };
    
    const datasets = [];
    
    Object.keys(categories).forEach(category => {
        const dataPoints = [];
        
        // Calculate average for each month
        limitedLabels.forEach(dateStr => {
            if (categories[category][dateStr]) {
                const sum = categories[category][dateStr].reduce((a, b) => a + b, 0);
                const avg = sum / categories[category][dateStr].length;
                dataPoints.push(avg);
            } else {
                dataPoints.push(null); // No data for this month
            }
        });
        
        // Generate a color for categories not in our predefined map
        const color = categoryColors[category] || `hsl(${Math.random() * 360}, 70%, 50%, 0.7)`;
        
        datasets.push({
            label: category,
            data: dataPoints,
            backgroundColor: color,
            borderColor: color.replace('0.7', '1'),
            borderWidth: 2,
            tension: 0.4,
            fill: false,
            pointBackgroundColor: color.replace('0.7', '1'),
            pointBorderColor: '#fff',
            pointBorderWidth: 1,
            pointRadius: 3,
            pointHoverRadius: 5
        });
    });
    
    // Format labels for display
    const displayLabels = limitedLabels.map(dateStr => {
        const [year, month] = dateStr.split('-');
        const date = new Date(parseInt(year), parseInt(month) - 1, 1);
        return date.toLocaleDateString(undefined, { month: 'short', year: 'numeric' });
    });
    
    return {
        labels: displayLabels,
        datasets: datasets
    };
}

/**
 * Process metrics for category distribution
 * @param {Array} metricsData - Raw metrics data from the API
 * @returns {Object} Processed category distribution data
 */
function processCategoryDistribution(metricsData) {
    // Count metrics by category
    const categoryCounts = {};
    
    metricsData.forEach(metric => {
        const category = metric.category || 'Uncategorized';
        categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });
    
    const labels = Object.keys(categoryCounts);
    const data = Object.values(categoryCounts);
    
    // Define colors for categories - use trendViz colors if available
    const categoryColors = trendViz && trendViz.categoryColors ? {
        'Emissions': trendViz.categoryColors.emissions.replace('rgb', 'rgba').replace(')', ', 0.7)'),
        'Water': trendViz.categoryColors.water.replace('rgb', 'rgba').replace(')', ', 0.7)'),
        'Energy': trendViz.categoryColors.energy.replace('rgb', 'rgba').replace(')', ', 0.7)'),
        'Waste': trendViz.categoryColors.waste.replace('rgb', 'rgba').replace(')', ', 0.7)'),
        'Social': trendViz.categoryColors.social.replace('rgb', 'rgba').replace(')', ', 0.7)'),
        'Governance': trendViz.categoryColors.governance.replace('rgb', 'rgba').replace(')', ', 0.7)')
    } : {
        'Emissions': 'rgba(220, 53, 69, 0.7)', // Red
        'Water': 'rgba(13, 202, 240, 0.7)',    // Light blue
        'Energy': 'rgba(255, 193, 7, 0.7)',    // Yellow
        'Waste': 'rgba(25, 135, 84, 0.7)',     // Green
        'Social': 'rgba(13, 110, 253, 0.7)',   // Blue
        'Governance': 'rgba(108, 117, 125, 0.7)' // Gray
    };
    
    // Map colors to categories
    const colors = labels.map(category => 
        categoryColors[category] || `hsl(${Math.random() * 360}, 70%, 50%, 0.7)`
    );
    
    return {
        labels: labels,
        data: data,
        colors: colors
    };
}

/**
 * Create custom legends for the metrics chart
 * @param {Array} datasets - The datasets from the chart
 */
function createCustomLegend(datasets) {
    const legendContainer = document.getElementById('custom-legend');
    if (!legendContainer) return;
    
    legendContainer.innerHTML = '';
    
    datasets.forEach((dataset, index) => {
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        legendItem.dataset.index = index;
        
        const colorBox = document.createElement('div');
        colorBox.className = 'legend-color';
        colorBox.style.backgroundColor = dataset.backgroundColor;
        
        const label = document.createElement('span');
        label.className = 'legend-label';
        label.textContent = dataset.label;
        
        legendItem.appendChild(colorBox);
        legendItem.appendChild(label);
        
        // Toggle dataset visibility on click
        legendItem.addEventListener('click', function() {
            const index = parseInt(this.dataset.index);
            const isVisible = !metricsChart.isDatasetVisible(index);
            metricsChart.setDatasetVisibility(index, isVisible);
            metricsChart.update();
            
            // Update legend item style
            this.classList.toggle('disabled', !isVisible);
        });
        
        legendContainer.appendChild(legendItem);
    });
}

/**
 * Update the chart type
 * @param {string} type - The chart type (line, bar, area)
 */
function updateChartType(type) {
    if (!metricsChart) return;
    
    // Save current data and options
    const data = metricsChart.data;
    const options = metricsChart.options;
    
    // Destroy current chart
    metricsChart.destroy();
    
    // Create new chart with the same data but different type
    const ctx = document.getElementById('metrics-chart').getContext('2d');
    
    // Adjust dataset properties based on chart type
    data.datasets.forEach(dataset => {
        if (type === 'area') {
            dataset.fill = true;
            dataset.backgroundColor = dataset.borderColor.replace('1)', '0.1)');
        } else {
            dataset.fill = false;
        }
    });
    
    // Create new chart
    metricsChart = new Chart(ctx, {
        type: type === 'area' ? 'line' : type,
        data: data,
        options: options
    });
    
    // Show success notification
    showNotification('Chart type updated', 'bi-check-circle', 'success');
}

/**
 * Update charts theme based on dark mode
 * @param {boolean} isDarkMode - Whether dark mode is enabled
 */
function updateChartTheme(isDarkMode) {
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    const textColor = isDarkMode ? '#e0e0e0' : '#666666';
    
    // Update metrics chart if it exists
    if (metricsChart) {
        // Update grid and text colors
        metricsChart.options.scales.x.grid.color = gridColor;
        metricsChart.options.scales.y.grid.color = gridColor;
        metricsChart.options.scales.x.ticks.color = textColor;
        metricsChart.options.scales.y.ticks.color = textColor;
        
        // Update tooltip style
        metricsChart.options.plugins.tooltip.backgroundColor = isDarkMode ? 'rgba(45, 45, 45, 0.95)' : 'rgba(255, 255, 255, 0.95)';
        metricsChart.options.plugins.tooltip.titleColor = isDarkMode ? '#e0e0e0' : '#333333';
        metricsChart.options.plugins.tooltip.bodyColor = isDarkMode ? '#cccccc' : '#666666';
        metricsChart.options.plugins.tooltip.borderColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        
        metricsChart.update();
    }
    
    // Update category chart if it exists
    if (categoryChart) {
        // Update text color for legend
        categoryChart.options.plugins.legend.labels.color = textColor;
        
        // Update tooltip style
        categoryChart.options.plugins.tooltip.backgroundColor = isDarkMode ? 'rgba(45, 45, 45, 0.95)' : 'rgba(255, 255, 255, 0.95)';
        categoryChart.options.plugins.tooltip.titleColor = isDarkMode ? '#e0e0e0' : '#333333';
        categoryChart.options.plugins.tooltip.bodyColor = isDarkMode ? '#cccccc' : '#666666';
        categoryChart.options.plugins.tooltip.borderColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        
        // Update dataset style
        categoryChart.data.datasets[0].borderColor = isDarkMode ? '#2d2d2d' : '#ffffff';
        
        categoryChart.update();
    }
}

/**
 * Export dashboard data
 * @param {string} format - The export format (csv, excel, pdf, json)
 */
function exportData(format) {
    // Show loading notification
    showNotification('Preparing export...', 'bi-hourglass-split', 'info');
    
    // Simulate export process
    setTimeout(() => {
        // Success notification
        showNotification(`Data exported as ${format.toUpperCase()}`, 'bi-check-circle', 'success');
        
        // Hide the dropdown
        document.getElementById('export-dropdown').classList.remove('show');
        
        // In a real implementation, we would generate and download the file here
    }, 1000);
}

/**
 * Show a notification toast
 * @param {string} message - The notification message
 * @param {string} icon - The Bootstrap icon class
 * @param {string} type - The notification type (info, success, warning, error)
 */
function showNotification(message, icon, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast ${type}`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Set toast content
    toastEl.innerHTML = `
        <div class="toast-header">
            <i class="bi ${icon} me-2"></i>
            <strong class="me-auto">SustainaTrend™</strong>
            <small>Just now</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Add to container
    toastContainer.appendChild(toastEl);
    
    // Initialize and show the toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 5000
    });
    toast.show();
    
    // Remove from DOM after hidden
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

/**
 * Helper function to capitalize the first letter of a string
 * @param {string} string - The string to capitalize
 * @returns {string} The capitalized string
 */
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Initialize the dashboard
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode
    initDarkMode();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize sidebar
    initSidebar();
    
    // Initialize export dropdown
    initExportMenu();
    
    // Initialize notifications
    initNotifications();
    
    // Set up export links
    document.querySelectorAll('#export-dropdown a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const format = this.getAttribute('data-format');
            exportData(format);
        });
    });
    
    // Check if metrics data is available in the page
    if (window.metricsData) {
        initCharts(window.metricsData);
    }
    
    // Make updateChartTheme globally available for dark mode toggle
    window.updateChartTheme = updateChartTheme;
});