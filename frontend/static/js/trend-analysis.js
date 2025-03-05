// Sustainability Trend Analysis Dashboard JavaScript
// Handles dark mode toggling, chart theme updates, filter functionality and data operations

// Global variable initialization
let currentTrendData = []; // Store current trend data
let chartInstances = []; // Store chart instances for theme updates
let currentTheme = localStorage.getItem('darkMode') === 'true' ? 'dark' : 'light';

// Chart color palette configuration
const chartColors = {
  light: {
    emissions: '#10b981', // green
    energy: '#0ea5e9',    // blue
    water: '#06b6d4',     // cyan
    waste: '#64748b',     // slate
    social: '#7c3aed',    // purple
    background: '#f8fafc',
    text: '#1e293b',
    grid: '#e2e8f0',
    tooltip: 'rgba(255, 255, 255, 0.9)'
  },
  dark: {
    emissions: '#4ade80', // brighter green
    energy: '#38bdf8',    // brighter blue
    water: '#22d3ee',     // brighter cyan
    waste: '#94a3b8',     // brighter slate
    social: '#a78bfa',    // brighter purple
    background: '#0f172a',
    text: '#e2e8f0',
    grid: '#334155',
    tooltip: 'rgba(15, 23, 42, 0.9)'
  }
};

document.addEventListener('DOMContentLoaded', function() {
    // Apply dark mode on initial load if saved in local storage
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    if (savedDarkMode) {
        document.body.classList.add('dark-mode');
        document.documentElement.classList.add('dark-mode');
        updateChartTheme(true);
    }
    
    // Theme toggler
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            // Add transition class for smooth effect
            document.body.classList.add('theme-transition');
            document.documentElement.classList.add('theme-transition');
            
            // Toggle dark mode
            document.body.classList.toggle('dark-mode');
            document.documentElement.classList.toggle('dark-mode');
            
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode);
            updateChartTheme(isDarkMode);
            
            // Update theme icon
            const themeIcon = this.querySelector('i');
            if (isDarkMode) {
                themeIcon.classList.remove('bi-sun');
                themeIcon.classList.add('bi-moon-stars-fill');
            } else {
                themeIcon.classList.remove('bi-moon-stars-fill');
                themeIcon.classList.add('bi-sun');
            }
            
            // Show theme notification
            showNotification(
                isDarkMode ? 'Dark mode activated' : 'Light mode activated', 
                isDarkMode ? 'bi-moon-stars-fill' : 'bi-sun'
            );
            
            // Remove transition class after animation completes
            setTimeout(() => {
                document.body.classList.remove('theme-transition');
                document.documentElement.classList.remove('theme-transition');
            }, 500);
        });
        
        // Update theme icon on initial load
        if (savedDarkMode) {
            const themeIcon = themeToggle.querySelector('i');
            if (themeIcon) {
                themeIcon.classList.remove('bi-sun');
                themeIcon.classList.add('bi-moon-stars-fill');
            }
        }
    }
    
    // Chart time range selector
    const chartTimeRange = document.getElementById('chart-time-range');
    if (chartTimeRange) {
        chartTimeRange.addEventListener('change', function() {
            fetchTrendData(null, this.value);
            
            // Show filter notification
            const selectedTimeframe = this.options[this.selectedIndex].text;
            showNotification(`Timeframe set to ${selectedTimeframe}`, 'bi-calendar');
        });
    }
    
    // Table category filter
    const tableCategoryFilter = document.getElementById('table-category-filter');
    if (tableCategoryFilter) {
        tableCategoryFilter.addEventListener('change', function() {
            const category = this.value;
            
            // If category is 'all', show all rows
            if (category === 'all') {
                document.querySelectorAll('#trend-table tbody tr').forEach(row => {
                    row.style.display = '';
                });
            } else {
                // Otherwise, show only rows with matching category
                document.querySelectorAll('#trend-table tbody tr').forEach(row => {
                    if (row.classList.contains(`category-${category}`)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
            
            // Show filter notification
            const selectedCategory = this.options[this.selectedIndex].text;
            showNotification(`Table filtered to ${selectedCategory}`, 'bi-filter');
        });
    }
    
    // Refresh table button
    const refreshTableBtn = document.getElementById('refresh-table');
    if (refreshTableBtn) {
        refreshTableBtn.addEventListener('click', function() {
            const tableCategoryFilter = document.getElementById('table-category-filter');
            const category = tableCategoryFilter ? tableCategoryFilter.value : null;
            
            // Add spinning animation to icon
            const icon = this.querySelector('i');
            if (icon) icon.classList.add('spin-animation');
            
            // Fetch data and update table
            fetchTrendData(category);
            
            // Show notification
            showNotification('Trend data refreshed', 'bi-arrow-clockwise');
            
            // Remove spinning animation after a short delay
            setTimeout(() => {
                if (icon) icon.classList.remove('spin-animation');
            }, 1000);
        });
    }
    
    // Category filter
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            fetchTrendData(this.value);
            
            // Show filter notification
            const selectedCategory = this.options[this.selectedIndex].text;
            showNotification(`Filtered to ${selectedCategory}`, 'bi-filter');
        });
    }
    
    // Export button
    const exportBtn = document.getElementById('export-btn');
    const exportDropdown = document.getElementById('export-dropdown');
    
    if (exportBtn && exportDropdown) {
        exportBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            exportDropdown.classList.toggle('show');
            
            // Position the dropdown
            const btnRect = exportBtn.getBoundingClientRect();
            exportDropdown.style.top = btnRect.bottom + 5 + 'px';
            exportDropdown.style.right = (window.innerWidth - btnRect.right) + 'px';
        });
        
        // Close dropdown when clicking elsewhere
        document.addEventListener('click', function(e) {
            if (!exportBtn.contains(e.target) && !exportDropdown.contains(e.target)) {
                exportDropdown.classList.remove('show');
            }
        });
        
        // Export format click handlers
        const exportFormats = exportDropdown.querySelectorAll('a');
        exportFormats.forEach(format => {
            format.addEventListener('click', function(e) {
                e.preventDefault();
                const formatType = this.getAttribute('data-format');
                exportData(formatType);
                exportDropdown.classList.remove('show');
            });
        });
    }
    
    // Filter modal
    const filterBtn = document.getElementById('filter-btn');
    const filterModal = document.getElementById('filter-modal');
    const closeModal = document.getElementById('close-modal');
    const applyFilters = document.getElementById('apply-filters');
    
    if (filterBtn && filterModal) {
        filterBtn.addEventListener('click', function(e) {
            e.preventDefault();
            filterModal.classList.add('show');
        });
        
        if (closeModal) {
            closeModal.addEventListener('click', function() {
                filterModal.classList.remove('show');
            });
        }
        
        // Close modal when clicking outside
        filterModal.addEventListener('click', function(e) {
            if (e.target === filterModal) {
                filterModal.classList.remove('show');
            }
        });
        
        if (applyFilters) {
            applyFilters.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Collect filter values
                const timeframe = document.querySelector('input[name="timeframe"]:checked')?.value || 'all';
                const categories = Array.from(document.querySelectorAll('input[name="category"]:checked'))
                    .map(checkbox => checkbox.value);
                
                // Apply filters and close modal
                applyDataFilters(timeframe, categories);
                filterModal.classList.remove('show');
                
                // Show confirmation
                showNotification('Filters applied successfully', 'bi-check-circle');
            });
        }
    }
    
    // Initialize charts
    initCharts();
    
    // Fetch initial data
    fetchTrendData();
});

// Function to update chart theme
function updateChartTheme(isDarkMode) {
    // Update the current theme
    currentTheme = isDarkMode ? 'dark' : 'light';
    
    // Apply CSS variables for chart themes
    const root = document.documentElement;
    const colors = chartColors[currentTheme];
    
    // Set CSS variables for charts
    root.style.setProperty('--chart-emissions-color', colors.emissions);
    root.style.setProperty('--chart-energy-color', colors.energy);
    root.style.setProperty('--chart-water-color', colors.water);
    root.style.setProperty('--chart-waste-color', colors.waste);
    root.style.setProperty('--chart-social-color', colors.social);
    root.style.setProperty('--chart-background', colors.background);
    root.style.setProperty('--chart-text-color', colors.text);
    root.style.setProperty('--chart-grid-color', colors.grid);
    root.style.setProperty('--chart-tooltip-background', colors.tooltip);
    
    // Update Plotly charts
    updatePlotlyTheme(isDarkMode);
    
    // Update Recharts if React dashboard is active
    if (window.reactTrendDashboard && typeof window.reactTrendDashboard.updateTheme === 'function') {
        window.reactTrendDashboard.updateTheme(currentTheme);
    }
    
    // Log theme update
    console.log(`Theme updated to ${currentTheme} mode`);
}

// Update Plotly charts with theme
function updatePlotlyTheme(isDarkMode) {
    if (typeof Plotly === 'undefined') return;
    
    const colors = chartColors[currentTheme];
    
    // Update each Plotly chart
    const plotlyCharts = document.querySelectorAll('[id^="plotly-"]');
    plotlyCharts.forEach(chart => {
        const chartId = chart.id;
        
        Plotly.relayout(chartId, {
            paper_bgcolor: colors.background,
            plot_bgcolor: colors.background,
            font: {
                color: colors.text
            },
            xaxis: {
                gridcolor: colors.grid,
                zerolinecolor: colors.grid,
                tickcolor: colors.text
            },
            yaxis: {
                gridcolor: colors.grid,
                zerolinecolor: colors.grid,
                tickcolor: colors.text
            }
        });
    });
}

// Function to initialize charts
function initCharts() {
    const trendChartEl = document.getElementById('trend-chart');
    const categoryDistributionEl = document.getElementById('category-distribution');
    const viralityRadarEl = document.getElementById('virality-radar');
    
    // Initialize charts based on which elements are present
    if (trendChartEl) {
        initTrendChart(trendChartEl);
    }
    
    if (categoryDistributionEl) {
        initCategoryDistribution(categoryDistributionEl);
    }
    
    if (viralityRadarEl) {
        initViralityRadar(viralityRadarEl);
    }
    
    // Apply initial theme
    updateChartTheme(currentTheme === 'dark');
}

// Initialize the main trend chart
function initTrendChart(element) {
    if (typeof Plotly === 'undefined') {
        console.warn('Plotly library not loaded');
        return;
    }
    
    // Create an empty trend chart with proper styling
    const colors = chartColors[currentTheme];
    
    Plotly.newPlot(element.id, [], {
        margin: { t: 10, r: 10, l: 50, b: 50 },
        paper_bgcolor: colors.background,
        plot_bgcolor: colors.background,
        font: { color: colors.text },
        xaxis: {
            title: 'Date',
            gridcolor: colors.grid,
            tickcolor: colors.text
        },
        yaxis: {
            title: 'Virality Score',
            gridcolor: colors.grid,
            tickcolor: colors.text
        },
        showlegend: true,
        legend: { orientation: 'h', y: -0.2 }
    }, {
        responsive: true
    });
}

// Initialize category distribution chart
function initCategoryDistribution(element) {
    if (typeof Plotly === 'undefined') {
        console.warn('Plotly library not loaded');
        return;
    }
    
    // Create an empty pie chart with proper styling
    const colors = chartColors[currentTheme];
    
    Plotly.newPlot(element.id, [], {
        margin: { t: 10, r: 10, l: 10, b: 10 },
        paper_bgcolor: colors.background,
        plot_bgcolor: colors.background,
        font: { color: colors.text },
        showlegend: true
    }, {
        responsive: true
    });
}

// Initialize virality radar chart
function initViralityRadar(element) {
    if (typeof Plotly === 'undefined') {
        console.warn('Plotly library not loaded');
        return;
    }
    
    // Create an empty radar chart with proper styling
    const colors = chartColors[currentTheme];
    
    Plotly.newPlot(element.id, [], {
        margin: { t: 30, r: 30, l: 30, b: 30 },
        paper_bgcolor: colors.background,
        plot_bgcolor: colors.background,
        font: { color: colors.text },
        polar: {
            radialaxis: {
                visible: true,
                gridcolor: colors.grid
            },
            angularaxis: {
                gridcolor: colors.grid
            }
        }
    }, {
        responsive: true
    });
}

// Function to fetch trend data
function fetchTrendData(category = null, timeframe = null) {
    console.log('Fetching trend data', 
                category ? `for category: ${category}` : 'for all categories',
                timeframe ? `with timeframe: ${timeframe}` : '');
    
    // Show loading state for all relevant containers
    const containers = [
        document.getElementById('trend-container'),
        document.getElementById('trend-chart'),
        document.getElementById('category-distribution'),
        document.getElementById('virality-radar')
    ];
    
    containers.forEach(container => {
        if (container) {
            container.classList.add('loading');
            
            // Add loading indicator if it's a chart container
            if (container.classList.contains('chart-container') || 
                container.classList.contains('trend-chart-container')) {
                const loadingEl = document.createElement('div');
                loadingEl.className = 'chart-loading-indicator';
                loadingEl.innerHTML = `
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2 text-muted">Loading data...</p>
                `;
                
                // Only add if not already present
                if (!container.querySelector('.chart-loading-indicator')) {
                    container.appendChild(loadingEl);
                }
            }
        }
    });
    
    // Show loading placeholder in table
    const tableBody = document.querySelector('#trend-table tbody');
    if (tableBody) {
        tableBody.innerHTML = `
            <tr class="placeholder-glow">
                <td colspan="7" class="text-center py-5">
                    <div class="d-flex justify-content-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading trend data...</span>
                        </div>
                    </div>
                    <p class="text-muted mt-3">Loading trend data...</p>
                </td>
            </tr>
        `;
    }
    
    // Prepare API URL with query parameters
    let apiUrl = '/api/trends';
    const params = new URLSearchParams();
    
    if (category && category !== 'all') {
        params.append('category', category);
    }
    
    if (timeframe && timeframe !== 'all') {
        params.append('timeframe', timeframe);
    }
    
    // Add params to URL if any exist
    if (params.toString()) {
        apiUrl += `?${params.toString()}`;
    }
    
    // Fetch data
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            currentTrendData = data;
            updateDashboard(data);
            
            // Remove loading states
            containers.forEach(container => {
                if (container) {
                    container.classList.remove('loading');
                    const loadingEl = container.querySelector('.chart-loading-indicator');
                    if (loadingEl) {
                        loadingEl.remove();
                    }
                }
            });
            
            // Show success notification
            showNotification('Data updated successfully', 'bi-check-circle');
        })
        .catch(error => {
            console.error('Error fetching trend data:', error);
            showNotification('Error loading data. Please try again.', 'bi-exclamation-triangle');
            
            // Remove loading states
            containers.forEach(container => {
                if (container) {
                    container.classList.remove('loading');
                    const loadingEl = container.querySelector('.chart-loading-indicator');
                    if (loadingEl) {
                        loadingEl.remove();
                    }
                }
            });
            
            // Show error in table
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center py-5">
                            <div class="error-icon">
                                <i class="bi bi-exclamation-triangle text-danger fs-1"></i>
                            </div>
                            <p class="text-danger">Error loading trend data. Please try again.</p>
                            <p class="text-muted small">${error.message}</p>
                        </td>
                    </tr>
                `;
            }
        });
}

// Function to update dashboard with data
function updateDashboard(data) {
    console.log('Updating dashboard with data:', data);
    
    // Update cards with summary stats
    updateSummaryCards(data);
    
    // Update charts
    updateCharts(data);
    
    // Update trend tables
    updateTrendTables(data);
}

// Function to update summary cards
function updateSummaryCards(data) {
    if (!data || !data.trends || data.trends.length === 0) {
        console.warn('No data available for summary cards');
        return;
    }
    
    const trends = data.trends;
    
    // Calculate summary statistics
    const stats = {
        totalTrends: trends.length,
        avgViralityScore: 0,
        improvingTrends: 0,
        worseningTrends: 0,
        topCategory: '',
        categoryDistribution: {}
    };
    
    // Calculate statistics
    let totalViralityScore = 0;
    
    trends.forEach(trend => {
        // Track virality score
        totalViralityScore += trend.virality_score;
        
        // Track trend direction
        if (trend.trend_direction === 'improving' || trend.trend_direction === 'increasing') {
            stats.improvingTrends++;
        } else {
            stats.worseningTrends++;
        }
        
        // Track category distribution
        if (!stats.categoryDistribution[trend.category]) {
            stats.categoryDistribution[trend.category] = 0;
        }
        stats.categoryDistribution[trend.category]++;
    });
    
    // Calculate average virality score
    stats.avgViralityScore = Math.round(totalViralityScore / trends.length);
    
    // Find top category
    let maxCount = 0;
    Object.entries(stats.categoryDistribution).forEach(([category, count]) => {
        if (count > maxCount) {
            maxCount = count;
            stats.topCategory = category;
        }
    });
    
    // Update total trends card
    const totalTrendsEl = document.getElementById('total-trends');
    if (totalTrendsEl) {
        totalTrendsEl.textContent = stats.totalTrends;
    }
    
    // Update average virality score card
    const avgViralityEl = document.getElementById('avg-virality');
    if (avgViralityEl) {
        avgViralityEl.textContent = stats.avgViralityScore;
        
        // Set color based on score
        if (stats.avgViralityScore > 75) {
            avgViralityEl.classList.add('high-virality');
        } else if (stats.avgViralityScore > 50) {
            avgViralityEl.classList.add('medium-virality');
        } else {
            avgViralityEl.classList.add('low-virality');
        }
    }
    
    // Update improving/worsening trends cards
    const improvingTrendsEl = document.getElementById('improving-trends');
    if (improvingTrendsEl) {
        improvingTrendsEl.textContent = stats.improvingTrends;
        
        // Update percentage if element exists
        const improvingPercentEl = document.getElementById('improving-percent');
        if (improvingPercentEl) {
            const percent = Math.round((stats.improvingTrends / stats.totalTrends) * 100);
            improvingPercentEl.textContent = `${percent}%`;
        }
    }
    
    const worseningTrendsEl = document.getElementById('worsening-trends');
    if (worseningTrendsEl) {
        worseningTrendsEl.textContent = stats.worseningTrends;
        
        // Update percentage if element exists
        const worseningPercentEl = document.getElementById('worsening-percent');
        if (worseningPercentEl) {
            const percent = Math.round((stats.worseningTrends / stats.totalTrends) * 100);
            worseningPercentEl.textContent = `${percent}%`;
        }
    }
    
    // Update top category card
    const topCategoryEl = document.getElementById('top-category');
    if (topCategoryEl) {
        const formattedCategory = stats.topCategory.charAt(0).toUpperCase() + stats.topCategory.slice(1);
        topCategoryEl.textContent = formattedCategory;
    }
    
    console.log('Summary cards updated with stats:', stats);
}

// Function to update charts
function updateCharts(data) {
    if (!data || !data.trends || data.trends.length === 0) {
        console.warn('No data available for charts');
        return;
    }
    
    const trends = data.trends;
    
    // Update main trend chart
    updateTrendChart(trends);
    
    // Update category distribution chart
    updateCategoryDistributionChart(trends);
    
    // Update virality radar chart
    updateViralityRadarChart(trends);
}

// Update the main trend chart
function updateTrendChart(trends) {
    const trendChartEl = document.getElementById('trend-chart');
    if (!trendChartEl || typeof Plotly === 'undefined') return;
    
    // Process data for trend chart
    // Group by category
    const categoryData = {};
    const timestamps = [...new Set(trends.map(t => t.timestamp))].sort();
    
    // Initialize data structure
    trends.forEach(trend => {
        if (!categoryData[trend.category]) {
            categoryData[trend.category] = {
                x: [],
                y: [],
                type: 'scatter',
                mode: 'lines+markers',
                name: trend.category.charAt(0).toUpperCase() + trend.category.slice(1),
                line: {
                    width: 3,
                    color: chartColors[currentTheme][trend.category] || '#8884d8'
                },
                marker: {
                    size: 8
                }
            };
        }
    });
    
    // Add data points
    trends.forEach(trend => {
        categoryData[trend.category].x.push(trend.timestamp);
        categoryData[trend.category].y.push(trend.virality_score);
    });
    
    // Convert to array for Plotly
    const plotData = Object.values(categoryData);
    
    // Colors for theme
    const colors = chartColors[currentTheme];
    
    // Update chart
    Plotly.react(trendChartEl.id, plotData, {
        margin: { t: 10, r: 10, l: 50, b: 50 },
        paper_bgcolor: colors.background,
        plot_bgcolor: colors.background,
        font: { color: colors.text },
        xaxis: {
            title: 'Date',
            gridcolor: colors.grid,
            tickcolor: colors.text
        },
        yaxis: {
            title: 'Virality Score',
            gridcolor: colors.grid,
            tickcolor: colors.text
        },
        showlegend: true,
        legend: { orientation: 'h', y: -0.2 }
    }, {
        responsive: true
    });
}

// Update category distribution chart
function updateCategoryDistributionChart(trends) {
    const categoryDistributionEl = document.getElementById('category-distribution');
    if (!categoryDistributionEl || typeof Plotly === 'undefined') return;
    
    // Count trends by category
    const categoryCount = {};
    trends.forEach(trend => {
        if (!categoryCount[trend.category]) {
            categoryCount[trend.category] = 0;
        }
        categoryCount[trend.category]++;
    });
    
    // Prepare data for pie chart
    const labels = Object.keys(categoryCount).map(
        cat => cat.charAt(0).toUpperCase() + cat.slice(1)
    );
    const values = Object.values(categoryCount);
    const colors = Object.keys(categoryCount).map(
        cat => chartColors[currentTheme][cat] || '#8884d8'
    );
    
    const data = [{
        type: 'pie',
        labels: labels,
        values: values,
        marker: {
            colors: colors
        },
        textinfo: 'label+percent',
        insidetextorientation: 'radial',
        hoverinfo: 'label+value'
    }];
    
    // Update chart
    Plotly.react(categoryDistributionEl.id, data, {
        margin: { t: 20, r: 20, l: 20, b: 20 },
        paper_bgcolor: chartColors[currentTheme].background,
        plot_bgcolor: chartColors[currentTheme].background,
        font: { color: chartColors[currentTheme].text },
        showlegend: false
    }, {
        responsive: true
    });
}

// Update virality radar chart
function updateViralityRadarChart(trends) {
    const viralityRadarEl = document.getElementById('virality-radar');
    if (!viralityRadarEl || typeof Plotly === 'undefined') return;
    
    // Calculate average virality score by category
    const categoryData = {};
    trends.forEach(trend => {
        if (!categoryData[trend.category]) {
            categoryData[trend.category] = {
                sum: 0,
                count: 0
            };
        }
        categoryData[trend.category].sum += trend.virality_score;
        categoryData[trend.category].count++;
    });
    
    // Convert to radar data
    const categories = Object.keys(categoryData);
    const scores = categories.map(cat => 
        Math.round(categoryData[cat].sum / categoryData[cat].count)
    );
    
    // Add the first point again to close the loop
    categories.push(categories[0]);
    scores.push(scores[0]);
    
    const formattedCategories = categories.map(
        cat => cat.charAt(0).toUpperCase() + cat.slice(1)
    );
    
    const data = [{
        type: 'scatterpolar',
        r: scores,
        theta: formattedCategories,
        fill: 'toself',
        fillcolor: `rgba(124, 58, 237, ${currentTheme === 'dark' ? 0.4 : 0.2})`,
        line: {
            color: chartColors[currentTheme].social,
            width: 3
        },
        name: 'Avg. Virality Score'
    }];
    
    // Colors for theme
    const colors = chartColors[currentTheme];
    
    // Update chart
    Plotly.react(viralityRadarEl.id, data, {
        polar: {
            radialaxis: {
                visible: true,
                range: [0, 100],
                gridcolor: colors.grid
            },
            angularaxis: {
                gridcolor: colors.grid
            }
        },
        margin: { t: 30, r: 30, l: 30, b: 30 },
        paper_bgcolor: colors.background,
        plot_bgcolor: colors.background,
        font: { color: colors.text }
    }, {
        responsive: true
    });
}

// Function to update trend tables
function updateTrendTables(data) {
    if (!data || !data.trends || data.trends.length === 0) {
        console.warn('No data available for trend tables');
        return;
    }
    
    const trends = data.trends;
    const trendTableBody = document.querySelector('#trend-table tbody');
    
    if (!trendTableBody) return;
    
    // Clear existing rows
    trendTableBody.innerHTML = '';
    
    // Sort trends by virality score descending
    const sortedTrends = [...trends].sort((a, b) => b.virality_score - a.virality_score);
    
    // Generate table rows
    sortedTrends.forEach((trend, index) => {
        const row = document.createElement('tr');
        
        // Apply category-specific class for styling
        row.classList.add(`category-${trend.category}`);
        
        // Format date
        const date = new Date(trend.timestamp);
        const formattedDate = `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
        
        // Determine virality class
        let viralityClass = 'low-virality';
        if (trend.virality_score > 75) {
            viralityClass = 'high-virality';
        } else if (trend.virality_score > 50) {
            viralityClass = 'medium-virality';
        }
        
        // Format trend direction with icon
        const directionIcon = trend.trend_direction === 'improving' || trend.trend_direction === 'increasing' 
            ? '<i class="bi bi-arrow-up-right"></i>' 
            : '<i class="bi bi-arrow-down-right"></i>';
        
        const directionClass = trend.trend_direction === 'improving' || trend.trend_direction === 'increasing'
            ? 'text-success'
            : 'text-danger';
        
        // Generate row HTML
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${trend.name}</td>
            <td>
                <span class="category-badge ${trend.category}">
                    ${trend.category.charAt(0).toUpperCase() + trend.category.slice(1)}
                </span>
            </td>
            <td class="${viralityClass}">${Math.round(trend.virality_score)}</td>
            <td class="${directionClass}">${directionIcon} ${trend.trend_direction.charAt(0).toUpperCase() + trend.trend_direction.slice(1)}</td>
            <td>${trend.trend_duration.charAt(0).toUpperCase() + trend.trend_duration.slice(1)}</td>
            <td>${formattedDate}</td>
        `;
        
        trendTableBody.appendChild(row);
    });
    
    console.log('Trend table updated with', trends.length, 'rows');
}

// Function to apply data filters
function applyDataFilters(timeframe, categories) {
    console.log('Applying filters:', {timeframe, categories});
    
    // In a real implementation, this would update the chart data
    // For now, just refresh with the category filter
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        fetchTrendData(categoryFilter.value);
    }
}

// Function to export data
function exportData(format) {
    console.log('Exporting data as', format);
    
    // Show notification
    showNotification(`Data exported as ${format.toUpperCase()}`, 'bi-download');
    
    // In a real implementation, this would generate and download the file
    // For now, just log the action
    const mockData = {
        trends: currentTrendData || [],
        format: format,
        timestamp: new Date().toISOString()
    };
    
    console.log('Export data:', mockData);
}

// Show notification
function showNotification(message, iconClass, type = 'info') {
    console.log('Notification:', message, type);
    
    // Get the container
    let container = document.getElementById('toast-container');
    if (!container) {
        console.warn('Toast container not found, fallback to body');
        // Create container if it doesn't exist
        const newContainer = document.createElement('div');
        newContainer.id = 'toast-container';
        newContainer.className = 'toast-container';
        document.body.appendChild(newContainer);
        container = newContainer;
    }
    
    // Determine notification type if not set based on iconClass
    if (type === 'info') {
        if (iconClass.includes('check')) type = 'success';
        else if (iconClass.includes('exclamation')) type = 'warning';
        else if (iconClass.includes('x-circle')) type = 'error';
    }
    
    // Create the notification element
    const notification = document.createElement('div');
    notification.className = `toast-notification ${type}`;
    
    // Add content
    notification.innerHTML = `
        <div class="toast-icon"><i class="bi ${iconClass}"></i></div>
        <div class="toast-content">
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" aria-label="Close">&times;</button>
    `;
    
    // Add to container
    container.appendChild(notification);
    
    // Apply animation and show
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Add event listener for close button
    const closeBtn = notification.querySelector('.toast-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
    }
    
    // Auto-remove after delay (different times based on type)
    const displayTime = type === 'error' ? 8000 : type === 'warning' ? 6000 : 5000;
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, displayTime);
}