/**
 * Real Estate Sustainability Intelligence Dashboard
 * SustainaTrend™ Platform - JavaScript for Real Estate Sustainability Visualizations
 */

// Set dark mode as default theme
let isDarkMode = true;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initCharts();
    
    // Fetch real estate trend data on load
    fetchRealEstateTrendData();
    
    // Set up event listeners for filter controls
    document.getElementById('filter-btn')?.addEventListener('click', function() {
        document.getElementById('filter-modal')?.classList.add('show');
    });
    
    document.getElementById('close-modal')?.addEventListener('click', function() {
        document.getElementById('filter-modal')?.classList.remove('show');
    });
    
    document.getElementById('apply-filters')?.addEventListener('click', function() {
        // Get selected filter values
        const timeframe = document.querySelector('input[name="timeframe"]:checked')?.value || 'all';
        
        const categoryCheckboxes = document.querySelectorAll('input[name="category"]:checked');
        const categories = Array.from(categoryCheckboxes).map(cb => cb.value);
        
        const propertyTypeCheckboxes = document.querySelectorAll('input[name="property_type"]:checked');
        const propertyTypes = Array.from(propertyTypeCheckboxes).map(cb => cb.value);
        
        const impactValue = document.getElementById('impact-slider')?.value || 30;
        
        // Apply filters
        applyDataFilters(timeframe, categories, propertyTypes, impactValue);
        
        // Close modal
        document.getElementById('filter-modal')?.classList.remove('show');
        
        // Show notification
        showNotification('Filters applied successfully', 'bi-funnel-fill', 'info');
    });
    
    // Set up value chain selector
    setupValueChainSelector();
    
    // Set up RAG query system
    setupRagQuerySystem();
    
    // Set up property sustainability scorecard
    setupPropertyScorecard();
    
    // Set up chart time range selector
    document.getElementById('chart-time-range')?.addEventListener('change', function() {
        fetchRealEstateTrendData(null, this.value);
    });
    
    // Set up table category filter
    document.getElementById('table-category-filter')?.addEventListener('change', function() {
        const category = this.value;
        filterTableByCategory(category);
    });
    
    // Set up export dropdown
    document.getElementById('export-btn')?.addEventListener('click', function() {
        document.getElementById('export-dropdown')?.classList.toggle('show');
    });
    
    // Set up export actions
    document.querySelectorAll('#export-dropdown a[data-format]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const format = this.getAttribute('data-format');
            exportData(format);
        });
    });
    
    // Close export dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const exportBtn = document.getElementById('export-btn');
        const exportDropdown = document.getElementById('export-dropdown');
        
        if (exportBtn && exportDropdown && !exportBtn.contains(e.target)) {
            exportDropdown.classList.remove('show');
        }
    });
    
    // Set up impact slider value display
    const impactSlider = document.getElementById('impact-slider');
    const impactValue = document.getElementById('impact-value');
    
    if (impactSlider && impactValue) {
        impactSlider.addEventListener('input', function() {
            impactValue.textContent = this.value;
        });
    }
});

function updateChartTheme(isDarkMode) {
    // Apply chart theme based on dark/light mode
    const chartTheme = isDarkMode ? 'dark' : 'light';
    
    // Update theme for all charts
    // This would be implemented based on the charting library used
    console.log(`Updated chart theme to ${chartTheme}`);
}

function initCharts() {
    // Initialize trend chart
    initTrendChart(document.getElementById('trend-chart'));
    
    // Initialize category distribution
    initCategoryDistribution(document.getElementById('category-distribution'));
    
    // Initialize impact radar
    initImpactRadar(document.getElementById('impact-radar'));
    
    // Initialize story charts
    initStoryCharts();
}

function initTrendChart(element) {
    if (!element) return;
    
    // Create a placeholder trend chart (will be populated with real data later)
    const data = [{
        type: 'scatter',
        mode: 'lines',
        name: 'Energy Efficiency',
        x: ['Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025', 'Feb 2025', 'Mar 2025'],
        y: [45, 47, 52, 58, 63, 68],
        line: {
            color: '#2ecc71'
        }
    }, {
        type: 'scatter',
        mode: 'lines',
        name: 'Carbon Footprint',
        x: ['Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025', 'Feb 2025', 'Mar 2025'],
        y: [30, 32, 35, 38, 42, 46],
        line: {
            color: '#3498db'
        }
    }, {
        type: 'scatter',
        mode: 'lines',
        name: 'Green Financing',
        x: ['Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025', 'Feb 2025', 'Mar 2025'],
        y: [12, 15, 18, 22, 28, 35],
        line: {
            color: '#9b59b6'
        }
    }, {
        type: 'scatter',
        mode: 'lines',
        name: 'Certifications',
        x: ['Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025', 'Feb 2025', 'Mar 2025'],
        y: [25, 28, 30, 32, 34, 37],
        line: {
            color: '#f1c40f'
        }
    }, {
        type: 'scatter',
        mode: 'lines',
        name: 'Market Trends',
        x: ['Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025', 'Feb 2025', 'Mar 2025'],
        y: [40, 42, 45, 48, 52, 55],
        line: {
            color: '#e67e22'
        }
    }];
    
    const layout = {
        title: '',
        height: 400,
        margin: {
            l: 50,
            r: 30,
            b: 50,
            t: 10,
            pad: 4
        },
        xaxis: {
            title: '',
            showgrid: false
        },
        yaxis: {
            title: 'Score',
            range: [0, 100]
        },
        legend: {
            orientation: 'h',
            yanchor: 'bottom',
            y: -0.3,
            xanchor: 'center',
            x: 0.5
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: {
            color: isDarkMode ? '#e0e0e0' : '#333333'
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: false
    };
    
    try {
        Plotly.newPlot(element, data, layout, config);
    } catch (e) {
        console.error('Error initializing trend chart:', e);
        element.innerHTML = '<div class="alert alert-danger">Error initializing chart</div>';
    }
}

function initCategoryDistribution(element) {
    if (!element) return;
    
    // Create a placeholder category distribution chart
    const data = [{
        type: 'pie',
        values: [30, 25, 15, 20, 10],
        labels: ['Energy Efficiency', 'Carbon Footprint', 'Green Financing', 'Certifications', 'Market Trends'],
        textinfo: 'label+percent',
        textposition: 'outside',
        automargin: true,
        marker: {
            colors: ['#2ecc71', '#3498db', '#9b59b6', '#f1c40f', '#e67e22']
        }
    }];
    
    const layout = {
        height: 400,
        margin: {
            l: 10,
            r: 10,
            b: 10,
            t: 10,
            pad: 4
        },
        showlegend: false,
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: {
            color: isDarkMode ? '#e0e0e0' : '#333333'
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: false
    };
    
    try {
        Plotly.newPlot(element, data, layout, config);
    } catch (e) {
        console.error('Error initializing category distribution chart:', e);
        element.innerHTML = '<div class="alert alert-danger">Error initializing chart</div>';
    }
}

function initImpactRadar(element) {
    if (!element) return;
    
    // Create a placeholder impact radar chart with improved accessibility
    const data = [{
        type: 'scatterpolar',
        r: [85, 60, 70, 45, 90],
        theta: ['Energy Efficiency', 'Carbon Footprint', 'Green Financing', 'Certifications', 'Market Trends'],
        fill: 'toself',
        name: 'Impact Score',
        marker: {
            color: 'rgba(46, 204, 113, 0.7)'
        }
    }];
    
    const layout = {
        height: 400,
        margin: {
            l: 50,
            r: 50,
            b: 30,
            t: 10,
            pad: 4
        },
        polar: {
            radialaxis: {
                visible: true,
                range: [0, 100],
                tickfont: {
                    size: 10,
                    color: isDarkMode ? '#e0e0e0' : '#333333'
                },
                ticksuffix: '%'
            },
            angularaxis: {
                tickfont: {
                    size: 12,
                    color: isDarkMode ? '#e0e0e0' : '#333333'
                }
            }
        },
        showlegend: false,
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: {
            color: isDarkMode ? '#e0e0e0' : '#333333'
        },
        annotations: [
            {
                x: 0.5,
                y: 1.05,
                xref: 'paper',
                yref: 'paper',
                text: 'Impact Score By Category',
                showarrow: false,
                font: {
                    size: 15,
                    color: isDarkMode ? '#e0e0e0' : '#333333'
                }
            }
        ]
    };
    
    const config = {
        responsive: true,
        displayModeBar: false,
        toImageButtonOptions: {
            format: 'png',
            filename: 'real_estate_impact_radar',
            scale: 2
        }
    };
    
    try {
        Plotly.newPlot(element, data, layout, config);
        
        // Add accessibility description
        const descriptionEl = document.createElement('div');
        descriptionEl.className = 'sr-only';
        descriptionEl.setAttribute('role', 'complementary');
        descriptionEl.innerHTML = `
            <p>This radar chart shows impact scores across different sustainability categories:
            Energy Efficiency: 85%, Carbon Footprint: 60%, Green Financing: 70%, 
            Certifications: 45%, and Market Trends: 90%.</p>
        `;
        element.appendChild(descriptionEl);
    } catch (e) {
        console.error('Error initializing impact radar chart:', e);
        element.innerHTML = '<div class="alert alert-danger">Error initializing chart</div>';
    }
}

function initStoryCharts() {
    // Initialize story charts for data storytelling section
    const storyChart1 = document.getElementById('story-chart-1');
    const storyChart2 = document.getElementById('story-chart-2');
    
    if (storyChart1) {
        // Create price premium by EPC rating chart
        const data = [{
            type: 'bar',
            x: ['G', 'F', 'E', 'D', 'C', 'B', 'A', 'A+'],
            y: [-3.5, -2.1, -0.8, 0, 1.2, 2.5, 4.2, 5.8],
            marker: {
                color: ['#e74c3c', '#e67e22', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60', '#1abc9c', '#16a085']
            }
        }];
        
        const layout = {
            title: 'Price Premium by EPC Rating (%)',
            height: 300,
            margin: {
                l: 50,
                r: 30,
                b: 50,
                t: 50,
                pad: 4
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: {
                color: isDarkMode ? '#e0e0e0' : '#333333'
            }
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        try {
            Plotly.newPlot(storyChart1, data, layout, config);
        } catch (e) {
            console.error('Error initializing story chart 1:', e);
            storyChart1.innerHTML = '<div class="alert alert-danger">Error initializing chart</div>';
        }
    }
    
    if (storyChart2) {
        // Create green mortgage growth chart
        const data = [{
            type: 'scatter',
            mode: 'lines+markers',
            x: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025'],
            y: [8, 10, 13, 15, 18],
            name: 'Green Mortgage Share (%)',
            line: {
                color: '#9b59b6',
                width: 3
            },
            marker: {
                size: 8
            }
        }];
        
        const layout = {
            title: 'Green Mortgage Market Share Growth',
            height: 300,
            margin: {
                l: 50,
                r: 30,
                b: 50,
                t: 50,
                pad: 4
            },
            yaxis: {
                range: [0, 25]
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: {
                color: isDarkMode ? '#e0e0e0' : '#333333'
            }
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        try {
            Plotly.newPlot(storyChart2, data, layout, config);
        } catch (e) {
            console.error('Error initializing story chart 2:', e);
            storyChart2.innerHTML = '<div class="alert alert-danger">Error initializing chart</div>';
        }
    }
}

function fetchRealEstateTrendData(category = null, timeframe = null) {
    console.log('Fetching real estate trend data', 
                category ? `for category: ${category}` : 'for all categories',
                timeframe ? `with timeframe: ${timeframe}` : '');
    
    // Show loading states
    showLoadingStates();
    
    // Prepare API URL with query parameters
    let apiUrl = '/api/realestate-trends';
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
            if (data.success) {
                updateDashboard(data);
                // Show success notification
                showNotification('Real estate sustainability data updated successfully', 'bi-check-circle-fill', 'success');
            } else {
                throw new Error('Data fetch failed');
            }
        })
        .catch(error => {
            console.error('Error fetching real estate trend data:', error);
            // Show error notification
            showNotification('Failed to update real estate data. Please try again.', 'bi-exclamation-triangle-fill', 'error');
            // Remove loading states
            removeLoadingStates();
        });
}

function showLoadingStates() {
    // Show loading state for all relevant containers
    const containers = [
        document.getElementById('trend-chart'),
        document.getElementById('category-distribution'),
        document.getElementById('impact-radar')
    ];
    
    containers.forEach(container => {
        if (container) {
            container.classList.add('loading');
            
            // Add loading indicator if it's a chart container
            if (container.classList.contains('chart-container') || 
                container.classList.contains('trend-chart-container')) {
                
                // Only add if not already present
                if (!container.querySelector('.chart-loading-indicator')) {
                    const loadingEl = document.createElement('div');
                    loadingEl.className = 'chart-loading-indicator';
                    loadingEl.innerHTML = `
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2 text-muted">Loading real estate data...</p>
                    `;
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
                            <span class="visually-hidden">Loading metric data...</span>
                        </div>
                    </div>
                    <p class="text-muted mt-3">Loading real estate sustainability metrics...</p>
                </td>
            </tr>
        `;
    }
}

function removeLoadingStates() {
    // Remove loading state from all relevant containers
    const containers = [
        document.getElementById('trend-chart'),
        document.getElementById('category-distribution'),
        document.getElementById('impact-radar')
    ];
    
    containers.forEach(container => {
        if (container) {
            container.classList.remove('loading');
            
            // Remove loading indicator
            const loadingEl = container.querySelector('.chart-loading-indicator');
            if (loadingEl) {
                loadingEl.remove();
            }
        }
    });
}

function updateDashboard(data) {
    // Update all dashboard components with real estate data
    updateSummaryCards(data);
    updateCharts(data);
    updateMetricTable(data.trends);
    
    // Remove all loading states
    removeLoadingStates();
}

function updateSummaryCards(data) {
    if (!data || !data.trends || data.trends.length === 0) return;
    
    // Get trends sorted by impact score (should already be sorted)
    const sortedTrends = [...data.trends];
    
    // Top metric
    const topMetric = sortedTrends[0];
    if (topMetric) {
        const topMetricName = document.getElementById('top-metric-name');
        const topMetricDesc = document.getElementById('top-metric-desc');
        const topMetricScore = document.getElementById('top-metric-score');
        
        if (topMetricName) topMetricName.textContent = topMetric.name;
        if (topMetricDesc) {
            const categoryDisplay = getCategoryDisplayName(topMetric.category);
            topMetricDesc.textContent = `Highest impact across ${categoryDisplay} metrics`;
        }
        if (topMetricScore) topMetricScore.textContent = topMetric.virality_score;
    }
    
    // Emerging trends (top 3 improving trends)
    const improvingTrends = sortedTrends.filter(t => t.trend_direction === 'improving');
    const emergingTrendsList = document.getElementById('emerging-trends-list');
    
    if (emergingTrendsList && improvingTrends.length > 0) {
        let emergingTrendsHtml = '';
        
        // Take top 3 improving trends
        improvingTrends.slice(0, 3).forEach(trend => {
            const categoryClass = getCategoryClass(trend.category);
            const categoryDisplay = getCategoryDisplayName(trend.category);
            
            emergingTrendsHtml += `
                <li class="list-group-item d-flex align-items-center border-0 px-0">
                    <div class="me-auto">${trend.name} <span class="metric-badge ${categoryClass}">${categoryDisplay}</span></div>
                    <span class="badge bg-primary">↑ ${trend.percent_change}%</span>
                </li>
            `;
        });
        
        emergingTrendsList.innerHTML = emergingTrendsHtml;
    }
    
    // Focus areas (top worsening trends)
    const worseningTrends = sortedTrends.filter(t => t.trend_direction === 'worsening');
    const focusAreasList = document.getElementById('focus-areas-list');
    
    if (focusAreasList) {
        let focusAreasHtml = '';
        
        if (worseningTrends.length > 0) {
            // Take top 2 worsening trends
            worseningTrends.slice(0, 2).forEach(trend => {
                const categoryClass = getCategoryClass(trend.category);
                const categoryDisplay = getCategoryDisplayName(trend.category);
                
                focusAreasHtml += `
                    <li class="list-group-item d-flex align-items-center border-0 px-0">
                        <div class="me-auto">${trend.name} <span class="metric-badge ${categoryClass}">${categoryDisplay}</span></div>
                        <span class="badge bg-danger">↑ ${trend.percent_change}%</span>
                    </li>
                `;
            });
        } else {
            // If no worsening trends, show the lowest performing trends
            sortedTrends.slice(-2).forEach(trend => {
                const categoryClass = getCategoryClass(trend.category);
                const categoryDisplay = getCategoryDisplayName(trend.category);
                
                focusAreasHtml += `
                    <li class="list-group-item d-flex align-items-center border-0 px-0">
                        <div class="me-auto">${trend.name} <span class="metric-badge ${categoryClass}">${categoryDisplay}</span></div>
                        <span class="badge bg-warning">↓ Low Impact</span>
                    </li>
                `;
            });
        }
        
        focusAreasList.innerHTML = focusAreasHtml;
    }
    
    // Key metrics overview
    const totalMetrics = document.getElementById('total-metrics');
    const avgImpact = document.getElementById('avg-impact');
    const improvingMetrics = document.getElementById('improving-metrics');
    const improvingPercent = document.getElementById('improving-percent');
    const worseningMetrics = document.getElementById('worsening-metrics');
    const worseningPercent = document.getElementById('worsening-percent');
    
    if (totalMetrics) totalMetrics.textContent = data.trends.length;
    
    if (avgImpact) {
        const avgScore = data.trends.reduce((sum, trend) => sum + trend.virality_score, 0) / data.trends.length;
        avgImpact.textContent = avgScore.toFixed(1);
    }
    
    const improvingCount = improvingTrends.length;
    const worseningCount = worseningTrends.length;
    
    if (improvingMetrics) improvingMetrics.textContent = improvingCount;
    if (improvingPercent) {
        const improvingPercentValue = (improvingCount / data.trends.length * 100).toFixed(0);
        improvingPercent.textContent = `${improvingPercentValue}%`;
    }
    
    if (worseningMetrics) worseningMetrics.textContent = worseningCount;
    if (worseningPercent) {
        const worseningPercentValue = (worseningCount / data.trends.length * 100).toFixed(0);
        worseningPercent.textContent = `${worseningPercentValue}%`;
    }
}

function updateCharts(data) {
    if (!data) return;
    
    // Update trend chart
    updateTrendChart(data.chart_data);
    
    // Update category distribution
    updateCategoryDistribution(data.category_counts);
    
    // Update impact radar
    updateImpactRadar(data.trends);
}

function updateTrendChart(chartData) {
    const trendChart = document.getElementById('trend-chart');
    if (!trendChart || !chartData || chartData.length === 0) return;
    
    try {
        // Extract timestamps for x-axis
        const timestamps = chartData.map(d => d.timestamp);
        
        // Prepare series data
        const seriesData = [
            {
                type: 'scatter',
                mode: 'lines',
                name: 'Energy Efficiency',
                x: timestamps,
                y: chartData.map(d => d.energy_efficiency || 0),
                line: { color: '#2ecc71' }
            },
            {
                type: 'scatter',
                mode: 'lines',
                name: 'Carbon Footprint',
                x: timestamps,
                y: chartData.map(d => d.carbon_footprint || 0),
                line: { color: '#3498db' }
            },
            {
                type: 'scatter',
                mode: 'lines',
                name: 'Green Financing',
                x: timestamps,
                y: chartData.map(d => d.green_financing || 0),
                line: { color: '#9b59b6' }
            },
            {
                type: 'scatter',
                mode: 'lines',
                name: 'Certifications',
                x: timestamps,
                y: chartData.map(d => d.certifications || 0),
                line: { color: '#f1c40f' }
            },
            {
                type: 'scatter',
                mode: 'lines',
                name: 'Market Trends',
                x: timestamps,
                y: chartData.map(d => d.market_trends || 0),
                line: { color: '#e67e22' }
            }
        ];
        
        // Update chart
        Plotly.react(trendChart, seriesData);
        
    } catch (e) {
        console.error('Error updating trend chart:', e);
    }
}

function updateCategoryDistribution(categoryCounts) {
    const chartElement = document.getElementById('category-distribution');
    if (!chartElement || !categoryCounts) return;
    
    try {
        // Prepare data
        const categories = Object.keys(categoryCounts);
        const counts = categories.map(c => categoryCounts[c]);
        const labels = categories.map(getCategoryDisplayName);
        
        const data = [{
            type: 'pie',
            values: counts,
            labels: labels,
            textinfo: 'label+percent',
            textposition: 'outside',
            automargin: true,
            marker: {
                colors: getCategoryColors(categories)
            }
        }];
        
        // Update chart
        Plotly.react(chartElement, data);
        
    } catch (e) {
        console.error('Error updating category distribution chart:', e);
    }
}

function updateImpactRadar(trends) {
    const chartElement = document.getElementById('impact-radar');
    if (!chartElement || !trends || trends.length === 0) return;
    
    try {
        // Calculate average impact score by category
        const categoryScores = {};
        const categoryCounts = {};
        const highestTrends = {};  // Track highest impact trend per category
        
        trends.forEach(trend => {
            const category = trend.category;
            
            if (!categoryScores[category]) {
                categoryScores[category] = 0;
                categoryCounts[category] = 0;
                highestTrends[category] = { score: 0, name: '' };
            }
            
            categoryScores[category] += trend.virality_score;
            categoryCounts[category]++;
            
            // Track highest impact trend in each category
            if (trend.virality_score > highestTrends[category].score) {
                highestTrends[category] = { 
                    score: trend.virality_score, 
                    name: trend.name,
                    trend_direction: trend.trend_direction,
                    percent_change: trend.percent_change
                };
            }
        });
        
        // Calculate averages
        const categories = Object.keys(categoryScores);
        const avgScores = categories.map(c => Math.round(categoryScores[c] / categoryCounts[c]));
        const labels = categories.map(getCategoryDisplayName);
        
        // Get color scheme based on theme
        const colorScheme = isDarkMode ? 
            'rgba(46, 204, 113, 0.7)' : 
            'rgba(39, 174, 96, 0.7)';
        
        // Prepare data
        const data = [{
            type: 'scatterpolar',
            r: avgScores,
            theta: labels,
            fill: 'toself',
            name: 'Impact Score',
            marker: {
                color: colorScheme
            },
            hoverinfo: 'text',
            hovertext: categories.map((cat, idx) => {
                const highestTrend = highestTrends[cat];
                const directionIcon = highestTrend.trend_direction === 'improving' ? '↑' : '↓';
                return `<b>${labels[idx]}</b><br>
                        Average Impact: <b>${avgScores[idx]}</b><br>
                        Top Metric: ${highestTrend.name}<br>
                        Change: ${directionIcon} ${highestTrend.percent_change}%`;
            })
        }];
        
        // Enhanced layout
        const layout = {
            polar: {
                radialaxis: {
                    visible: true,
                    range: [0, 100],
                    tickfont: {
                        size: 10,
                        color: isDarkMode ? '#e0e0e0' : '#333333'
                    },
                    ticksuffix: '%'
                },
                angularaxis: {
                    tickfont: {
                        size: 12,
                        color: isDarkMode ? '#e0e0e0' : '#333333'
                    }
                }
            },
            showlegend: false,
            margin: {
                l: 50,
                r: 50,
                b: 30,
                t: 50,
                pad: 4
            },
            annotations: [
                {
                    x: 0.5,
                    y: 1.05,
                    xref: 'paper',
                    yref: 'paper',
                    text: 'Sustainability Impact By Category',
                    showarrow: false,
                    font: {
                        size: 15,
                        color: isDarkMode ? '#e0e0e0' : '#333333'
                    }
                }
            ]
        };
        
        // Update chart with improved layout
        Plotly.react(chartElement, data, layout);
        
        // Update accessibility description
        const descriptionEl = chartElement.querySelector('.sr-only');
        if (descriptionEl) {
            const description = `<p>This radar chart shows average impact scores across different sustainability categories: 
                ${categories.map((cat, idx) => `${labels[idx]}: ${avgScores[idx]}%`).join(', ')}.</p>`;
            descriptionEl.innerHTML = description;
        } else {
            const newDescriptionEl = document.createElement('div');
            newDescriptionEl.className = 'sr-only';
            newDescriptionEl.setAttribute('role', 'complementary');
            newDescriptionEl.innerHTML = `<p>This radar chart shows average impact scores across different sustainability categories: 
                ${categories.map((cat, idx) => `${labels[idx]}: ${avgScores[idx]}%`).join(', ')}.</p>`;
            chartElement.appendChild(newDescriptionEl);
        }
        
    } catch (e) {
        console.error('Error updating impact radar chart:', e);
    }
}

function updateMetricTable(trends) {
    const tableBody = document.querySelector('#trend-table tbody');
    if (!tableBody || !trends || trends.length === 0) return;
    
    let tableHtml = '';
    
    trends.forEach((trend, index) => {
        const categoryClass = getCategoryClass(trend.category);
        const categoryDisplay = getCategoryDisplayName(trend.category);
        
        const trendDirectionClass = trend.trend_direction === 'improving' ? 'text-success' : 'text-danger';
        const trendDirectionIcon = trend.trend_direction === 'improving' ? '↑' : '↓';
        
        const dateObj = new Date(trend.timestamp);
        const formattedDate = dateObj.toLocaleDateString();
        
        tableHtml += `
            <tr data-category="${trend.category}">
                <td>${index + 1}</td>
                <td>${trend.name}</td>
                <td><span class="metric-badge ${categoryClass}">${categoryDisplay}</span></td>
                <td>${trend.virality_score.toFixed(1)}</td>
                <td class="${trendDirectionClass}">${trendDirectionIcon} ${trend.percent_change}%</td>
                <td>${trend.trend_duration}</td>
                <td>${formattedDate}</td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = tableHtml;
}

function filterTableByCategory(category) {
    const tableRows = document.querySelectorAll('#trend-table tbody tr');
    
    tableRows.forEach(row => {
        const rowCategory = row.getAttribute('data-category');
        
        if (category === 'all' || rowCategory === category) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    // Show notification
    showNotification(`Table filtered by ${category === 'all' ? 'all categories' : getCategoryDisplayName(category)}`, 'bi-filter', 'info');
}

function setupValueChainSelector() {
    // Set up the real estate value chain selector
    const valueChainItems = document.querySelectorAll('.value-chain-item');
    
    valueChainItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            valueChainItems.forEach(i => i.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Get selected value chain segment
            const segment = this.getAttribute('data-chain');
            
            // Apply value chain segment filter
            applyValueChainFilter(segment);
            
            // Show notification
            showNotification(`Now showing ${segment === 'all' ? 'entire value chain' : segment} data`, 'bi-filter', 'info');
        });
    });
}

function applyValueChainFilter(segment) {
    // Apply filter based on selected value chain segment
    console.log('Applying value chain filter:', segment);
    
    // In a real implementation, this would filter data by value chain segment
    // For now, we'll just simulate the filter effect
    
    // Show filtering effect
    showLoadingStates();
    
    // Simulate loading delay
    setTimeout(() => {
        // Remove loading states
        removeLoadingStates();
        
        // Update visuals to reflect filtered data
        // This would be replaced with actual filtered data in a real implementation
        
    }, 1500);
}

function setupRagQuerySystem() {
    // Set up the RAG-powered query system
    const queryButton = document.getElementById('rag-query-button');
    const queryInput = document.getElementById('rag-query-input');
    const answerContainer = document.getElementById('rag-answer');
    
    if (queryButton && queryInput) {
        queryButton.addEventListener('click', function() {
            const query = queryInput.value.trim();
            
            if (query) {
                // Show loading state
                answerContainer.innerHTML = `
                    <div class="d-flex justify-content-center my-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Processing query...</span>
                        </div>
                    </div>
                    <p class="text-center text-muted">Analyzing real estate sustainability data...</p>
                `;
                
                // In a real implementation, this would call the RAG API
                // For now, we'll just simulate a response after a delay
                setTimeout(() => {
                    // Mock RAG response for demonstration
                    const mockResponse = getMockRagResponse(query);
                    
                    // Update the answer container
                    answerContainer.innerHTML = mockResponse;
                    
                    // Show notification
                    showNotification('AI analysis complete', 'bi-robot', 'success');
                }, 2000);
            } else {
                showNotification('Please enter a question to analyze', 'bi-exclamation-circle-fill', 'warning');
            }
        });
    }
}

function setupPropertyScorecard() {
    // Set up the property sustainability scorecard interactions
    const propertyTypeSelector = document.getElementById('property-type-selector');
    const analyzeButton = document.getElementById('analyze-property');
    
    if (analyzeButton && propertyTypeSelector) {
        analyzeButton.addEventListener('click', function() {
            const propertyType = propertyTypeSelector.value;
            
            // Show loading notification
            showNotification('Analyzing property sustainability profile...', 'bi-building-gear', 'info');
            
            // Simulate API call with loading delay
            setTimeout(() => {
                updatePropertyScorecard(propertyType);
                
                // Show success notification
                showNotification('Property sustainability analysis complete', 'bi-building-check', 'success');
            }, 1500);
        });
    }
}

function updatePropertyScorecard(propertyType) {
    // Update property scorecard based on selected property type
    
    // Example data for different property types
    const propertyData = {
        'residential': {
            address: 'Herengracht 258, Amsterdam',
            constructionYear: 1984,
            floorArea: 125,
            lastRenovation: 2021,
            sustainabilityScore: 85,
            neighborhoodAvg: 72,
            energyLabel: 'A',
            energyIndex: 0.87,
            potentialImprovement: 'Label A+ (0.65)',
            energyProgress: 88,
            carbonFootprint: 18,
            carbonBenchmark: 27,
            carbonTarget: 12,
            carbonProgress: 75,
            greenFinancing: 'Eligible',
            mortgageRateDiscount: 0.42,
            subsidyPotential: '€12,500',
            financingProgress: 92,
            roiValue: 9.2,
            upgradeCosts: '€18,000',
            valueIncrease: '€37,800',
            roiProgress: 85
        },
        'commercial': {
            address: 'Zuidas 45, Amsterdam',
            constructionYear: 2008,
            floorArea: 850,
            lastRenovation: 2019,
            sustainabilityScore: 77,
            neighborhoodAvg: 68,
            energyLabel: 'B',
            energyIndex: 1.14,
            potentialImprovement: 'Label A (0.85)',
            energyProgress: 75,
            carbonFootprint: 28,
            carbonBenchmark: 35,
            carbonTarget: 20,
            carbonProgress: 65,
            greenFinancing: 'Eligible',
            mortgageRateDiscount: 0.38,
            subsidyPotential: '€8,500',
            financingProgress: 82,
            roiValue: 7.8,
            upgradeCosts: '€42,000',
            valueIncrease: '€68,000',
            roiProgress: 78
        },
        'mixed': {
            address: 'Amstel 100, Amsterdam',
            constructionYear: 1998,
            floorArea: 420,
            lastRenovation: 2019,
            sustainabilityScore: 78,
            neighborhoodAvg: 65,
            energyLabel: 'B',
            energyIndex: 1.14,
            potentialImprovement: 'Label A (0.85)',
            energyProgress: 75,
            carbonFootprint: 28,
            carbonBenchmark: 35,
            carbonTarget: 20,
            carbonProgress: 65,
            greenFinancing: 'Eligible',
            mortgageRateDiscount: 0.38,
            subsidyPotential: '€8,500',
            financingProgress: 82,
            roiValue: 7.8,
            upgradeCosts: '€25,000',
            valueIncrease: '€42,000',
            roiProgress: 78
        },
        'industrial': {
            address: 'Industrieweg 78, Rotterdam',
            constructionYear: 2002,
            floorArea: 1250,
            lastRenovation: 2017,
            sustainabilityScore: 62,
            neighborhoodAvg: 58,
            energyLabel: 'C',
            energyIndex: 1.45,
            potentialImprovement: 'Label B (1.10)',
            energyProgress: 55,
            carbonFootprint: 42,
            carbonBenchmark: 45,
            carbonTarget: 25,
            carbonProgress: 40,
            greenFinancing: 'Partially Eligible',
            mortgageRateDiscount: 0.18,
            subsidyPotential: '€15,200',
            financingProgress: 58,
            roiValue: 6.3,
            upgradeCosts: '€68,000',
            valueIncrease: '€92,000',
            roiProgress: 65
        }
    };
    
    // Get data for selected property type
    const data = propertyData[propertyType];
    
    // Update property summary
    document.querySelector('.property-summary .d-flex:nth-child(2) strong').textContent = data.address;
    document.querySelector('.property-summary .d-flex:nth-child(3) strong').textContent = data.constructionYear;
    document.querySelector('.property-summary .d-flex:nth-child(4) strong').textContent = `${data.floorArea} m²`;
    document.querySelector('.property-summary .d-flex:nth-child(5) strong').textContent = data.lastRenovation;
    document.querySelector('.property-summary .d-flex:nth-child(6) strong').textContent = propertyType.charAt(0).toUpperCase() + propertyType.slice(1);
    
    // Update sustainability score
    const scoreCircle = document.querySelector('.sustainability-score-circle');
    scoreCircle.style.background = `conic-gradient(var(--primary-color) 0% ${data.sustainabilityScore}%, #e0e0e0 ${data.sustainabilityScore}% 100%)`;
    document.querySelector('.score-value').textContent = data.sustainabilityScore;
    document.querySelector('.score-comparison .d-flex:nth-child(1) strong').textContent = data.neighborhoodAvg;
    
    // Update energy label
    const energyLabel = document.querySelector('.energy-label');
    energyLabel.textContent = data.energyLabel;
    energyLabel.className = 'energy-label label-' + data.energyLabel.toLowerCase();
    document.querySelector('.sustainability-metric-card:nth-child(1) .d-flex:nth-child(1) strong').textContent = data.energyIndex;
    document.querySelector('.sustainability-metric-card:nth-child(1) .d-flex:nth-child(2) strong').textContent = data.potentialImprovement;
    document.querySelector('.sustainability-metric-card:nth-child(1) .progress-bar').style.width = `${data.energyProgress}%`;
    
    // Update carbon footprint
    document.querySelector('.carbon-value').textContent = `${data.carbonFootprint} kg/m²`;
    document.querySelector('.sustainability-metric-card:nth-child(2) .d-flex:nth-child(1) strong').textContent = `${data.carbonBenchmark} kg/m²`;
    document.querySelector('.sustainability-metric-card:nth-child(2) .d-flex:nth-child(2) strong').textContent = `${data.carbonTarget} kg/m²`;
    document.querySelector('.sustainability-metric-card:nth-child(2) .progress-bar').style.width = `${data.carbonProgress}%`;
    
    // Update green financing
    document.querySelector('.finance-value').textContent = data.greenFinancing;
    document.querySelector('.sustainability-metric-card:nth-child(3) .d-flex:nth-child(1) strong').textContent = `${data.mortgageRateDiscount}%`;
    document.querySelector('.sustainability-metric-card:nth-child(3) .d-flex:nth-child(2) strong').textContent = data.subsidyPotential;
    document.querySelector('.sustainability-metric-card:nth-child(3) .progress-bar').style.width = `${data.financingProgress}%`;
    
    // Update renovation ROI
    document.querySelector('.roi-value').textContent = `${data.roiValue}%`;
    document.querySelector('.sustainability-metric-card:nth-child(4) .d-flex:nth-child(1) strong').textContent = data.upgradeCosts;
    document.querySelector('.sustainability-metric-card:nth-child(4) .d-flex:nth-child(2) strong').textContent = data.valueIncrease;
    document.querySelector('.sustainability-metric-card:nth-child(4) .progress-bar').style.width = `${data.roiProgress}%`;
    
    // Generate recommended upgrades based on property type
    updateRecommendedUpgrades(propertyType);
}

function updateRecommendedUpgrades(propertyType) {
    // Update recommended upgrades based on property type
    const recommendationsContainer = document.querySelector('.upgrade-recommendations .row');
    
    // Example recommendations for different property types
    const recommendations = {
        'residential': [
            { icon: 'bi-sun', name: 'Solar Panels (15m²)', roi: 12.5 },
            { icon: 'bi-thermometer-half', name: 'Heat Pump Installation', roi: 9.3 },
            { icon: 'bi-droplet', name: 'Water Recycling System', roi: 7.8 }
        ],
        'commercial': [
            { icon: 'bi-lightning', name: 'Smart Energy Management', roi: 14.2 },
            { icon: 'bi-sun', name: 'Solar Panels (120m²)', roi: 11.8 },
            { icon: 'bi-thermometer-half', name: 'HVAC Efficiency Upgrade', roi: 9.6 }
        ],
        'mixed': [
            { icon: 'bi-sun', name: 'Solar Panels (20m²)', roi: 11.2 },
            { icon: 'bi-thermometer-half', name: 'Heat Pump Installation', roi: 8.7 },
            { icon: 'bi-layers', name: 'Window Insulation', roi: 9.3 }
        ],
        'industrial': [
            { icon: 'bi-lightning', name: 'Industrial Energy Recovery', roi: 15.7 },
            { icon: 'bi-sun', name: 'Solar Roof (450m²)', roi: 13.2 },
            { icon: 'bi-moisture', name: 'Rainwater Harvesting', roi: 8.4 }
        ]
    };
    
    // Get recommendations for selected property type
    const propertyRecommendations = recommendations[propertyType];
    
    // Update recommendation items
    let recommendationsHTML = '';
    propertyRecommendations.forEach(rec => {
        recommendationsHTML += `
            <div class="col-md-4">
                <div class="upgrade-item">
                    <i class="${rec.icon}"></i>
                    <span>${rec.name}</span>
                    <div class="upgrade-roi">ROI: ${rec.roi}%</div>
                </div>
            </div>
        `;
    });
    
    recommendationsContainer.innerHTML = recommendationsHTML;
}

function getMockRagResponse(query) {
    // Generate a mock RAG response based on the query
    // In a real implementation, this would come from the RAG API
    
    query = query.toLowerCase();
    
    if (query.includes('epc') || query.includes('energy') || query.includes('rating')) {
        return `
            <p><strong>Real Estate Energy Efficiency Analysis:</strong> 
            Based on data from 843 properties across the Netherlands, the average EPC rating has improved from 3.2 to 2.1 
            over the past 18 months. Properties with A and B ratings now represent 28% of the market, up from 18% in 2023.
            </p>
            <p>
            Housing corporations have been leading this transition, with 37% of their portfolios now at B rating or better, 
            compared to 22% for private rental properties. The average cost of upgrading from an E to a B rating ranges from 
            €15,000 to €24,000, with ROI periods of 7-12 years when accounting for both operational savings and value appreciation.
            </p>
        `;
    } else if (query.includes('carbon') || query.includes('footprint') || query.includes('emission')) {
        return `
            <p><strong>Property Carbon Footprint Analysis:</strong> 
            The average carbon intensity across the analyzed property portfolio is 32 kg CO₂/m² annually, with 
            high-performing buildings achieving under 15 kg CO₂/m². New construction projects implementing 
            circular material usage principles (now at 23% adoption) are showing 40-55% lower embodied carbon 
            compared to conventional construction.
            </p>
            <p>
            The data indicates that operational carbon emissions are decreasing at approximately 7% annually 
            across the surveyed properties, primarily driven by heating system upgrades and improved insulation. 
            Properties implementing full electrification achieve an additional 12-18% reduction in their carbon footprint.
            </p>
        `;
    } else if (query.includes('financing') || query.includes('mortgage') || query.includes('loan')) {
        return `
            <p><strong>Green Financing & Mortgage Analysis:</strong> 
            Green mortgages now represent 18% of new mortgage originations in the Netherlands, up from 10% in 2023. 
            These mortgages offer interest rate discounts averaging 0.3-0.5% for properties meeting specific energy 
            efficiency thresholds (typically EPC A/B ratings).
            </p>
            <p>
            The data shows that buy-to-let investors are increasingly targeting energy-efficient properties, with 42% 
            citing favorable financing terms as a primary motivator. For housing corporations, green bonds and 
            sustainability-linked loans are providing €85-€130 million in annual financing for energy renovation projects, 
            with an average Green Retrofit ROI of 7.2%.
            </p>
        `;
    } else if (query.includes('value') || query.includes('premium') || query.includes('price')) {
        return `
            <p><strong>Sustainability Value Premium Analysis:</strong> 
            Properties with top-tier energy ratings (EPC A/A+) command a market premium of 4.2% in sales prices 
            and 5.8% in rental values compared to equivalent properties with average energy performance (EPC C/D). 
            This "green premium" has been growing at approximately 1.2 percentage points annually.
            </p>
            <p>
            The most significant premiums are observed in urban markets and for commercial properties, where energy 
            costs represent a higher proportion of occupancy expenses. Properties with additional certifications beyond 
            energy ratings (such as WELL or BREEAM) demonstrate an additional premium of 2.3-3.5%, particularly in the 
            high-end commercial and luxury residential segments.
            </p>
        `;
    } else {
        return `
            <p><strong>Real Estate Sustainability Overview:</strong> 
            Analysis of our property database shows accelerating adoption of sustainability features across the Dutch 
            real estate market. Top-performing sustainable properties show clear financial advantages: 4.2% higher 
            sales values, 5.8% rental premiums, and 18% lower vacancy rates compared to conventional properties.
            </p>
            <p>
            Green financing adoption is up 18% year-over-year, with preferential rates for energy-efficient properties 
            creating a compelling financial incentive. Housing corporations implementing portfolio-wide sustainability 
            improvements are seeing operational cost reductions of €3.20-€4.80 per square meter annually, alongside 
            significant reductions in carbon footprint (32 kg CO₂/m² on average).
            </p>
        `;
    }
}

function exportData(format) {
    console.log(`Exporting data in ${format} format`);
    
    // Show processing notification
    showNotification(`Preparing ${format.toUpperCase()} export...`, 'bi-hourglass-split', 'info');
    
    // Simulate export process
    setTimeout(() => {
        // Show success notification
        showNotification(`Real estate data exported successfully as ${format.toUpperCase()}`, 'bi-download', 'success');
    }, 1500);
}

function getCategoryDisplayName(category) {
    const displayNames = {
        'energy_efficiency': 'Energy Efficiency',
        'carbon_footprint': 'Carbon Footprint',
        'green_financing': 'Green Financing',
        'certifications': 'Certifications',
        'market_trends': 'Market Trends'
    };
    
    return displayNames[category] || category;
}

function getCategoryClass(category) {
    const classMap = {
        'energy_efficiency': 'energy',
        'carbon_footprint': 'carbon',
        'green_financing': 'financing',
        'certifications': 'certification',
        'market_trends': 'market'
    };
    
    return classMap[category] || '';
}

function getCategoryColors(categories) {
    const colorMap = {
        'energy_efficiency': '#2ecc71',
        'carbon_footprint': '#3498db',
        'green_financing': '#9b59b6',
        'certifications': '#f1c40f',
        'market_trends': '#e67e22'
    };
    
    return categories.map(c => colorMap[c] || '#95a5a6');
}

function showNotification(message, iconClass, type = 'info') {
    // Create notification element
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    
    // Set inner HTML with icon and message
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="bi ${iconClass}"></i>
        </div>
        <div class="toast-message">${message}</div>
        <button class="toast-close">&times;</button>
    `;
    
    // Add to container
    const container = document.getElementById('toast-container');
    if (container) {
        container.appendChild(toast);
        
        // Add visible class after a short delay (for animation)
        setTimeout(() => {
            toast.classList.add('visible');
        }, 10);
        
        // Close button functionality
        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                closeToast(toast);
            });
        }
        
        // Auto close after duration
        setTimeout(() => {
            closeToast(toast);
        }, 6000);
    }
}

function closeToast(toast) {
    // Remove visible class first (for animation)
    toast.classList.remove('visible');
    
    // Remove element after animation completes
    setTimeout(() => {
        toast.remove();
    }, 300);
}