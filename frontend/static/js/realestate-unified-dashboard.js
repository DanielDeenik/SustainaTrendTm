/**
 * SustainaTrend™ Real Estate Unified Dashboard JavaScript
 * 
 * This script handles:
 * 1. Gemini-powered integrated search functionality
 * 2. Dynamic dashboard updates
 * 3. Real-time BREEAM metrics visualization
 * 4. Context-aware AI insights based on search queries
 */

// Initialize dashboard functionality when DOM is loaded
document.addEventListener("DOMContentLoaded", function() {
    initializeSearchIntegration();
    initializeValueChainFilters();
    initializeCharts();
    initializeTabNavigation();
    initializeRealtimeUpdates(); // Add real-time updates via SSE

    // Show initial AI insight
    showDefaultAIInsight();
});

/**
 * Initialize integrated search functionality
 * Connects search input to the Gemini-powered backend
 */
function initializeSearchIntegration() {
    const searchInput = document.getElementById('integrated-search');
    const searchTimeout = 750; // Delay between user typing and search execution
    let searchTimer = null;

    // Only proceed if search input exists
    if (!searchInput) return;

    // Handle input events on search box
    searchInput.addEventListener('input', function(e) {
        // Clear any pending search timer
        if (searchTimer) {
            clearTimeout(searchTimer);
        }

        const query = e.target.value.trim();
        
        // Show searching indicator
        if (query.length > 2) {
            showSearchingIndicator();
            
            // Set timer for delayed search execution
            searchTimer = setTimeout(() => {
                executeIntegratedSearch(query);
            }, searchTimeout);
        } else if (query.length === 0) {
            // Clear search results if query is empty
            clearSearchResults();
        }
    });

    // Handle form submission
    searchInput.closest('form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        
        if (query.length > 2) {
            executeIntegratedSearch(query);
        }
    });
}

/**
 * Execute integrated search using the Gemini API
 * Updates multiple dashboard components based on search results
 * 
 * @param {string} query - The search query
 */
function executeIntegratedSearch(query) {
    // Get active tab to determine which components to update
    const activeTab = document.querySelector('.tab-navigation .nav-link.active');
    const component = activeTab ? activeTab.id.replace('-tab', '') : 'all';

    // Default context is realestate
    const context = 'realestate';

    console.log(`Executing search with query: "${query}", component: ${component}, context: ${context}`);

    // Show loading state
    showLoadingState(component);

    // Make API request to our integrated search endpoint
    fetch('/api/integrated-search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            component: component,
            context: context
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Search API returned status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Process and display the search results
            updateDashboardComponents(data.updates);
            
            // Show success toast notification
            showToast('Search Complete', `Found ${data.results_count} results for "${query}"`, 'success');
        } else {
            // Handle error case
            console.error('Search API error:', data.error);
            showToast('Search Error', data.error || 'An error occurred during search', 'error');
        }
    })
    .catch(error => {
        console.error('Search request failed:', error);
        showToast('Search Failed', error.message, 'error');
    })
    .finally(() => {
        // Hide loading indicators
        hideLoadingState(component);
    });
}

/**
 * Update multiple dashboard components based on search results
 * 
 * @param {Object} updates - Component updates from search API
 */
function updateDashboardComponents(updates) {
    // Check which components have updates
    if (updates.breeam && updates.breeam.has_updates) {
        updateBREEAMMetrics(updates.breeam);
    }
    
    if (updates.energy && updates.energy.has_updates) {
        updateEnergyMetrics(updates.energy);
    }
    
    if (updates.carbon && updates.carbon.has_updates) {
        updateCarbonMetrics(updates.carbon);
    }
    
    if (updates.financial && updates.financial.has_updates) {
        updateFinancialMetrics(updates.financial);
    }
    
    if (updates.ai_insights && updates.ai_insights.has_updates) {
        updateAIInsights(updates.ai_insights);
    }
    
    // Always update search summary
    updateSearchSummary(updates.summary);
    
    // Highlight the tabs that have updates
    highlightTabsWithUpdates(updates);
}

/**
 * Update BREEAM metrics section based on search results
 * 
 * @param {Object} breeamUpdates - BREEAM-specific updates
 */
function updateBREEAMMetrics(breeamUpdates) {
    const breeamContainer = document.getElementById('breeam-results-container');
    
    if (!breeamContainer) return;
    
    if (breeamUpdates.highlighted_categories && breeamUpdates.highlighted_categories.length > 0) {
        // Highlight specific BREEAM categories
        const categories = breeamUpdates.highlighted_categories;
        
        // Highlight in UI
        document.querySelectorAll('.breeam-category').forEach(element => {
            const categoryName = element.getAttribute('data-category');
            if (categories.includes(categoryName)) {
                element.classList.add('highlight-category');
            } else {
                element.classList.remove('highlight-category');
            }
        });
        
        // Optionally update specific results display
        if (breeamUpdates.results && breeamUpdates.results.length > 0) {
            const resultsHtml = breeamUpdates.results.map(result => {
                return `
                    <div class="metric-breakdown-card">
                        <div class="metric-header">
                            <span>${result.title || 'BREEAM Result'}</span>
                            <span class="metric-badge certification">BREEAM</span>
                        </div>
                        <div class="metric-body">
                            ${result.description || 'No description available'}
                        </div>
                    </div>
                `;
            }).join('');
            
            const breeamResultsElement = document.getElementById('breeam-search-results');
            if (breeamResultsElement) {
                breeamResultsElement.innerHTML = resultsHtml;
                breeamResultsElement.style.display = 'block';
            }
        }
    } else {
        // No BREEAM-specific results
        const breeamResultsElement = document.getElementById('breeam-search-results');
        if (breeamResultsElement) {
            breeamResultsElement.innerHTML = `
                <div class="alert alert-info">
                    ${breeamUpdates.message || 'No BREEAM-specific information found for your search.'}
                </div>
            `;
            breeamResultsElement.style.display = 'block';
        }
        
        // Reset category highlights
        document.querySelectorAll('.breeam-category').forEach(element => {
            element.classList.remove('highlight-category');
        });
    }
}

/**
 * Update Energy metrics section based on search results
 * 
 * @param {Object} energyUpdates - Energy-specific updates
 */
function updateEnergyMetrics(energyUpdates) {
    const energyContainer = document.getElementById('energy-results-container');
    
    if (!energyContainer) return;
    
    if (energyUpdates.has_updates && energyUpdates.results && energyUpdates.results.length > 0) {
        const resultsHtml = energyUpdates.results.map(result => {
            return `
                <div class="metric-breakdown-card">
                    <div class="metric-header">
                        <span>${result.title || 'Energy Efficiency Result'}</span>
                        <span class="metric-badge energy">Energy</span>
                    </div>
                    <div class="metric-body">
                        ${result.description || 'No description available'}
                    </div>
                </div>
            `;
        }).join('');
        
        const energyResultsElement = document.getElementById('energy-search-results');
        if (energyResultsElement) {
            energyResultsElement.innerHTML = resultsHtml;
            energyResultsElement.style.display = 'block';
        }
    } else {
        // No energy-specific results
        const energyResultsElement = document.getElementById('energy-search-results');
        if (energyResultsElement) {
            energyResultsElement.innerHTML = `
                <div class="alert alert-info">
                    ${energyUpdates.message || 'No energy efficiency information found for your search.'}
                </div>
            `;
            energyResultsElement.style.display = 'block';
        }
    }
}

/**
 * Update Carbon metrics section based on search results
 * 
 * @param {Object} carbonUpdates - Carbon-specific updates
 */
function updateCarbonMetrics(carbonUpdates) {
    const carbonContainer = document.getElementById('carbon-results-container');
    
    if (!carbonContainer) return;
    
    if (carbonUpdates.has_updates && carbonUpdates.results && carbonUpdates.results.length > 0) {
        const resultsHtml = carbonUpdates.results.map(result => {
            return `
                <div class="metric-breakdown-card">
                    <div class="metric-header">
                        <span>${result.title || 'Carbon Footprint Result'}</span>
                        <span class="metric-badge carbon">Carbon</span>
                    </div>
                    <div class="metric-body">
                        ${result.description || 'No description available'}
                    </div>
                </div>
            `;
        }).join('');
        
        const carbonResultsElement = document.getElementById('carbon-search-results');
        if (carbonResultsElement) {
            carbonResultsElement.innerHTML = resultsHtml;
            carbonResultsElement.style.display = 'block';
        }
    } else {
        // No carbon-specific results
        const carbonResultsElement = document.getElementById('carbon-search-results');
        if (carbonResultsElement) {
            carbonResultsElement.innerHTML = `
                <div class="alert alert-info">
                    ${carbonUpdates.message || 'No carbon footprint information found for your search.'}
                </div>
            `;
            carbonResultsElement.style.display = 'block';
        }
    }
}

/**
 * Update Financial metrics section based on search results
 * 
 * @param {Object} financialUpdates - Financial-specific updates
 */
function updateFinancialMetrics(financialUpdates) {
    const financialContainer = document.getElementById('financial-results-container');
    
    if (!financialContainer) return;
    
    if (financialUpdates.has_updates && financialUpdates.results && financialUpdates.results.length > 0) {
        const resultsHtml = financialUpdates.results.map(result => {
            return `
                <div class="metric-breakdown-card">
                    <div class="metric-header">
                        <span>${result.title || 'Financial Impact Result'}</span>
                        <span class="metric-badge financing">Financial</span>
                    </div>
                    <div class="metric-body">
                        ${result.description || 'No description available'}
                    </div>
                </div>
            `;
        }).join('');
        
        const financialResultsElement = document.getElementById('financial-search-results');
        if (financialResultsElement) {
            financialResultsElement.innerHTML = resultsHtml;
            financialResultsElement.style.display = 'block';
        }
    } else {
        // No financial-specific results
        const financialResultsElement = document.getElementById('financial-search-results');
        if (financialResultsElement) {
            financialResultsElement.innerHTML = `
                <div class="alert alert-info">
                    ${financialUpdates.message || 'No financial impact information found for your search.'}
                </div>
            `;
            financialResultsElement.style.display = 'block';
        }
    }
}

/**
 * Update AI insights section based on search results
 * 
 * @param {Object} aiUpdates - AI-generated insights and analysis
 */
function updateAIInsights(aiUpdates) {
    const aiContainer = document.getElementById('ai-insights-container');
    
    if (!aiContainer) return;
    
    if (aiUpdates.has_updates) {
        // Insert the HTML directly - the server has already formatted it
        aiContainer.innerHTML = aiUpdates.insight_html || '';
        
        // Scroll to insights section if we're not already on the AI tab
        if (!document.getElementById('ai-tab').classList.contains('active')) {
            // Add notification indicator to AI tab
            document.getElementById('ai-tab').classList.add('has-update');
        }
    } else {
        // No AI insights available
        aiContainer.innerHTML = `
            <div class="alert alert-info">
                ${aiUpdates.message || 'Not enough information to generate AI insights for your query.'}
            </div>
        `;
    }
}

/**
 * Update search summary section
 * 
 * @param {Object} summary - Search summary data
 */
function updateSearchSummary(summary) {
    const summaryContainer = document.getElementById('search-summary');
    
    if (!summaryContainer) return;
    
    if (summary.query && summary.result_count >= 0) {
        summaryContainer.innerHTML = `
            <div class="alert alert-primary">
                <strong>Search Results:</strong> Found ${summary.result_count} results for "${summary.query}" 
                in context: ${summary.context || 'general'}
                ${summary.top_result ? `<br><strong>Top result:</strong> ${summary.top_result.title}` : ''}
            </div>
        `;
        summaryContainer.style.display = 'block';
    } else {
        summaryContainer.style.display = 'none';
    }
}

/**
 * Highlight tabs that contain updated content
 * 
 * @param {Object} updates - All component updates
 */
function highlightTabsWithUpdates(updates) {
    // Remove existing highlights
    document.querySelectorAll('.nav-link').forEach(tab => {
        tab.classList.remove('has-update');
    });
    
    // Add highlights based on which components have updates
    if (updates.breeam && updates.breeam.has_updates) {
        document.getElementById('breeam-tab').classList.add('has-update');
    }
    
    if (updates.energy && updates.energy.has_updates) {
        document.getElementById('energy-tab').classList.add('has-update');
    }
    
    if (updates.carbon && updates.carbon.has_updates) {
        document.getElementById('carbon-tab').classList.add('has-update');
    }
    
    if (updates.financial && updates.financial.has_updates) {
        document.getElementById('financial-tab').classList.add('has-update');
    }
    
    if (updates.ai_insights && updates.ai_insights.has_updates) {
        document.getElementById('ai-tab').classList.add('has-update');
    }
}

/**
 * Show loading state for search components
 * 
 * @param {string} component - The component being searched (or 'all')
 */
function showLoadingState(component) {
    // Set global active search flag
    activeSearchResults = true;
    
    // Create loading indicators for each relevant section
    const components = component === 'all' ? 
        ['breeam', 'energy', 'carbon', 'financial', 'ai'] : 
        [component];
    
    components.forEach(comp => {
        const container = document.getElementById(`${comp}-results-container`);
        if (container) {
            const loadingElement = document.createElement('div');
            loadingElement.classList.add('search-loading-indicator');
            loadingElement.innerHTML = `
                <div class="d-flex justify-content-center my-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
                <p class="text-center text-muted">Searching ${comp} data...</p>
            `;
            
            // Clear previous results
            const resultsElement = document.getElementById(`${comp}-search-results`);
            if (resultsElement) {
                resultsElement.innerHTML = '';
                resultsElement.style.display = 'none';
            }
            
            // Add loading indicator
            container.prepend(loadingElement);
        }
    });
}

/**
 * Hide loading state for search components
 * 
 * @param {string} component - The component being searched (or 'all')
 */
function hideLoadingState(component) {
    // Remove loading indicators
    const components = component === 'all' ? 
        ['breeam', 'energy', 'carbon', 'financial', 'ai'] : 
        [component];
    
    components.forEach(comp => {
        const container = document.getElementById(`${comp}-results-container`);
        if (container) {
            const loadingElements = container.querySelectorAll('.search-loading-indicator');
            loadingElements.forEach(element => element.remove());
        }
    });
}

/**
 * Clear all search results and reset the dashboard state
 */
function clearSearchResults() {
    // Reset global search flag
    activeSearchResults = false;
    
    // Clear all search result containers
    ['breeam', 'energy', 'carbon', 'financial', 'ai'].forEach(component => {
        const resultsElement = document.getElementById(`${component}-search-results`);
        if (resultsElement) {
            resultsElement.innerHTML = '';
            resultsElement.style.display = 'none';
        }
    });
    
    // Remove all tab highlights
    document.querySelectorAll('.nav-link').forEach(tab => {
        tab.classList.remove('has-update');
    });
    
    // Hide search summary
    const summaryContainer = document.getElementById('search-summary');
    if (summaryContainer) {
        summaryContainer.style.display = 'none';
    }
    
    // Show default AI insight
    showDefaultAIInsight();
}

/**
 * Show searching indicator while user is typing
 */
function showSearchingIndicator() {
    const searchInput = document.getElementById('integrated-search');
    if (searchInput) {
        searchInput.classList.add('searching');
        
        // Add loading icon to the right of the input if it doesn't exist
        let searchingIcon = document.querySelector('.search-typing-indicator');
        if (!searchingIcon) {
            searchingIcon = document.createElement('span');
            searchingIcon.classList.add('search-typing-indicator');
            searchingIcon.innerHTML = '<i class="bi bi-three-dots"></i>';
            searchInput.parentNode.appendChild(searchingIcon);
        }
    }
}

/**
 * Show default AI insight on initial page load
 */
function showDefaultAIInsight() {
    const aiContainer = document.getElementById('ai-insights-container');
    
    if (!aiContainer) return;
    
    aiContainer.innerHTML = `
        <div class="ai-insight-card medium">
            <div class="ai-insight-header">
                <div class="ai-insight-title">Real Estate Sustainability Overview</div>
                <span class="badge bg-success">AI-Generated</span>
            </div>
            <div class="ai-insight-body">
                <p>Welcome to your real estate sustainability dashboard. Here's a summary of your portfolio:</p>
                <ul>
                    <li>Your portfolio's average BREEAM score is in the top 30% of the market</li>
                    <li>Energy efficiency is 22% better than industry benchmark</li>
                    <li>Carbon reduction initiatives have decreased emissions by 18% since 2020</li>
                </ul>
                <p>Try searching for specific sustainability metrics or trends to get more detailed insights.</p>
            </div>
        </div>
    `;
}

/**
 * Initialize value chain filter functionality
 */
function initializeValueChainFilters() {
    const valueChainItems = document.querySelectorAll('.value-chain-item');
    
    valueChainItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            valueChainItems.forEach(i => i.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Get chain value
            const chain = this.getAttribute('data-chain');
            
            // Filter dashboard content based on chain
            filterDashboardByChain(chain);
        });
    });
}

/**
 * Filter dashboard content by value chain
 * 
 * @param {string} chain - Value chain identifier
 */
function filterDashboardByChain(chain) {
    // In a real implementation, this would filter the dashboard data
    // For now, we'll just show a notification
    showToast('Filter Applied', `Filtering by value chain: ${chain}`, 'info');
    
    // Simulate content update
    if (chain !== 'all') {
        document.querySelectorAll('.chain-filterable').forEach(element => {
            if (element.getAttribute('data-chain') === chain) {
                element.style.display = 'block';
            } else {
                element.style.display = 'none';
            }
        });
    } else {
        // Show all elements when "all" is selected
        document.querySelectorAll('.chain-filterable').forEach(element => {
            element.style.display = 'block';
        });
    }
}

/**
 * Initialize dashboard charts and visualizations
 */
function initializeCharts() {
    // This function would initialize all charts in the dashboard
    // For now, it's a placeholder - will be implemented as needed
    
    try {
        initializeBREEAMCharts();
        initializeEnergyCharts();
        initializeCarbonCharts();
        initializeFinancialCharts();
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
}

/**
 * Initialize tab navigation functionality
 */
function initializeTabNavigation() {
    // Make sure tabs switch correctly
    const tabLinks = document.querySelectorAll('.tab-navigation .nav-link');
    
    tabLinks.forEach(tabLink => {
        tabLink.addEventListener('click', function() {
            // Remove active class from all tabs
            tabLinks.forEach(link => link.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Remove has-update indicator when a tab is clicked
            this.classList.remove('has-update');
            
            // Show corresponding tab content
            const tabId = this.getAttribute('data-bs-target');
            
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            document.querySelector(tabId).classList.add('show', 'active');
        });
    });
}

/**
 * Initialize BREEAM-specific charts
 */
function initializeBREEAMCharts() {
    // This is a placeholder for BREEAM-specific chart initialization
    // Would be implemented based on specific visualization needs
}

/**
 * Initialize Energy-specific charts
 */
function initializeEnergyCharts() {
    // This is a placeholder for Energy-specific chart initialization
    // Would be implemented based on specific visualization needs
}

/**
 * Initialize Carbon-specific charts
 */
function initializeCarbonCharts() {
    // This is a placeholder for Carbon-specific chart initialization
    // Would be implemented based on specific visualization needs
}

/**
 * Initialize Financial-specific charts
 */
function initializeFinancialCharts() {
    // This is a placeholder for Financial-specific chart initialization
    // Would be implemented based on specific visualization needs
}

/**
 * Initialize real-time updates using Server-Sent Events (SSE)
 * Establishes connection with our SSE endpoint and processes updates
 */
function initializeRealtimeUpdates() {
    // Check if EventSource is supported in the browser
    if (typeof EventSource === 'undefined') {
        console.warn('Server-Sent Events not supported in this browser. Real-time updates disabled.');
        return;
    }

    // Create the SSE connection
    const eventSource = new EventSource('/api/realestate-realtime-updates');
    
    // Connection opened successfully
    eventSource.addEventListener('open', function() {
        console.info('Real-time updates connection established');
        showToast('Real-time Updates', 'Connected to live data stream', 'info');
    });

    // Handle incoming messages
    eventSource.addEventListener('message', function(event) {
        try {
            // Parse the JSON data
            const updateData = JSON.parse(event.data);
            console.log('Received real-time update:', updateData);
            
            // Process updates based on event type
            switch (updateData.event) {
                case 'connected':
                    console.info('Real-time updates stream connected:', updateData.message);
                    break;
                    
                case 'breeam_update':
                    processRealtimeBREEAMUpdate(updateData.data);
                    break;
                    
                case 'energy_update':
                    processRealtimeEnergyUpdate(updateData.data);
                    break;
                    
                case 'carbon_update':
                    processRealtimeCarbonUpdate(updateData.data);
                    break;
                    
                case 'sustainability_alert':
                    processRealtimeSustainabilityAlert(updateData.data);
                    break;
                    
                default:
                    console.warn('Unknown real-time update type:', updateData.event);
            }
        } catch (error) {
            console.error('Error processing real-time update:', error);
        }
    });

    // Error handling
    eventSource.addEventListener('error', function(event) {
        console.error('SSE connection error:', event);
        
        if (event.target.readyState === EventSource.CLOSED) {
            console.warn('SSE connection closed');
            // Try to reconnect after a delay
            setTimeout(() => {
                console.info('Attempting to reconnect to real-time updates...');
                initializeRealtimeUpdates();
            }, 5000);
        }
    });
}

/**
 * Process real-time metric updates with standardized approach
 * 
 * @param {string} type - Type of update (breeam, energy, carbon)
 * @param {Object} data - Update data
 * @param {Object} options - Processing options
 */
function processRealtimeMetricUpdate(type, data, options = {}) {
    // Default options
    const defaults = {
        container: `${type}-realtime-updates`,
        tabId: `${type}-tab`,
        title: `${capitalizeFirstLetter(type)} Update`,
        mainLabel: capitalizeFirstLetter(type),
        mainValue: data[Object.keys(data).find(key => 
            ['score', 'consumption', 'emissions'].includes(key))],
        unit: data.unit || '',
        secondaryLabel: data.category ? 'Category' : (data.trend ? 'Trend' : 'Status'),
        secondaryValue: data.category || data.trend || 'Active',
        changeReversed: type === 'carbon' // For carbon, negative change is good
    };
    
    // Merge defaults with options
    const config = {...defaults, ...options};
    
    // Get the updates container
    const realtimeUpdatesContainer = document.getElementById(config.container);
    if (!realtimeUpdatesContainer) return;
    
    // Create a new update card using standardized CSS classes
    const updateCard = document.createElement('div');
    updateCard.className = `realtime-update ${type}`;
    
    // Determine change/trend direction for styling
    let changeDirection, changeIcon, changeValue;
    
    if (type === 'energy' && data.trend) {
        // Energy uses 'trend' field
        changeDirection = data.trend === 'decreasing' ? 'improved' : 
                         (data.trend === 'increasing' ? 'declined' : 'neutral');
        changeIcon = changeDirection === 'improved' ? 'bi-arrow-down' : 
                    (changeDirection === 'declined' ? 'bi-arrow-up' : 'bi-dash');
        changeValue = data.change || '0';
    } else {
        // BREEAM and Carbon use 'change' field
        const change = parseFloat(data.change || 0);
        const isPositive = change >= 0;
        
        // For carbon, negative change is good; for others, positive change is good
        changeDirection = (isPositive !== config.changeReversed) ? 'improved' : 'declined';
        
        // Icon direction depends on the type and change value
        if (config.changeReversed) {
            // For carbon, down arrow means improvement
            changeIcon = isPositive ? 'bi-arrow-up' : 'bi-arrow-down';
        } else {
            // For BREEAM, up arrow means improvement
            changeIcon = isPositive ? 'bi-arrow-up' : 'bi-arrow-down';
        }
        
        changeValue = config.changeReversed ? Math.abs(change) : change;
    }
    
    // Build the update card HTML
    updateCard.innerHTML = `
        <div class="realtime-update-header">
            <span>Property ${data.property_id} - ${config.title}</span>
            <span class="badge bg-danger live">LIVE</span>
        </div>
        <div class="realtime-update-body">
            <div><strong>${config.mainLabel}:</strong> ${config.mainValue} ${config.unit}
                <span class="update-badge ${changeDirection}">
                    <i class="bi ${changeIcon}"></i>
                    ${changeValue}%
                </span>
            </div>
            <div><strong>${config.secondaryLabel}:</strong> ${config.secondaryValue}</div>
            ${data.reduction ? `<div><strong>Reduction Target:</strong> ${data.reduction}%</div>` : ''}
            <div class="realtime-update-timestamp">${new Date(data.timestamp).toLocaleTimeString()}</div>
        </div>
    `;
    
    // Add the new update to the container (at the top)
    realtimeUpdatesContainer.prepend(updateCard);
    
    // Limit the number of displayed updates
    const maxUpdates = 5;
    const updates = realtimeUpdatesContainer.querySelectorAll('.realtime-update');
    if (updates.length > maxUpdates) {
        for (let i = maxUpdates; i < updates.length; i++) {
            updates[i].remove();
        }
    }
    
    // If not already on the relevant tab, add notification indicator
    const tabElement = document.getElementById(config.tabId);
    if (tabElement && !tabElement.classList.contains('active')) {
        tabElement.classList.add('has-update');
    }
    
    // Play notification sound if enabled
    playNotificationSound('update');
}

/**
 * Process real-time BREEAM metric updates
 * 
 * @param {Object} data - BREEAM update data
 */
function processRealtimeBREEAMUpdate(data) {
    processRealtimeMetricUpdate('breeam', data, {
        mainLabel: 'BREEAM Score',
        changeReversed: false // For BREEAM, positive change is good
    });
}

/**
 * Process real-time Energy metric updates
 * 
 * @param {Object} data - Energy update data
 */
function processRealtimeEnergyUpdate(data) {
    processRealtimeMetricUpdate('energy', data, {
        mainLabel: 'Consumption',
        secondaryLabel: 'Trend'
    });
}

/**
 * Process real-time Carbon metric updates
 * 
 * @param {Object} data - Carbon update data
 */
function processRealtimeCarbonUpdate(data) {
    processRealtimeMetricUpdate('carbon', data, {
        mainLabel: 'Emissions',
        changeReversed: true // For carbon, negative change is good
    });
}

/**
 * Process real-time sustainability alerts
 * 
 * @param {Object} data - Sustainability alert data
 */
function processRealtimeSustainabilityAlert(data) {
    // Get the alerts container (shared across all tabs)
    const alertsContainer = document.getElementById('sustainability-alerts');
    if (!alertsContainer) return;
    
    // Create a new alert card using standardized CSS classes
    const alertCard = document.createElement('div');
    alertCard.className = `realtime-alert ${data.severity.toLowerCase()}`;
    
    // Get the appropriate icon for the alert severity
    const severityIcon = getAlertIcon(data.severity.toLowerCase());
    
    alertCard.innerHTML = `
        <div class="realtime-alert-header">
            <span>
                <i class="bi ${severityIcon}"></i>
                ${capitalizeFirstLetter(data.severity)} Alert
            </span>
            <span class="badge bg-danger live">LIVE</span>
        </div>
        <div class="realtime-alert-body">
            <div class="alert-title">${data.title}</div>
            <div class="alert-message">${data.message}</div>
            <div class="alert-properties">
                ${data.properties ? `Affected properties: ${data.properties.join(', ')}` : ''}
            </div>
            <div class="realtime-alert-timestamp">${new Date(data.timestamp).toLocaleTimeString()}</div>
        </div>
    `;
    
    // Add the new alert to the container (at the top)
    alertsContainer.prepend(alertCard);
    
    // Limit the number of displayed alerts
    const maxAlerts = 5;
    const alerts = alertsContainer.querySelectorAll('.realtime-alert');
    if (alerts.length > maxAlerts) {
        for (let i = maxAlerts; i < alerts.length; i++) {
            alerts[i].remove();
        }
    }
    
    // Add visual indicator to all tabs since alerts are global
    document.querySelectorAll('.nav-link').forEach(tab => {
        if (!tab.classList.contains('active')) {
            tab.classList.add('has-alert');
        }
    });
    
    // Show a toast notification for the alert
    showToast(
        `${capitalizeFirstLetter(data.severity)} Alert`, 
        data.title,
        data.severity.toLowerCase()
    );
    
    // Play alert notification sound
    playNotificationSound('alert');
}

/**
 * Get HTML for loading spinner
 * 
 * @returns {string} HTML for loading spinner
 */
function getLoadingSpinnerHTML() {
    return `
        <div class="ai-loading-indicator">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
}

/**
 * Show toast notification
 * 
 * @param {string} title - Toast title
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, error, info, warning)
 */
function showToast(title, message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) return;
    
    const toastId = 'toast-' + Date.now();
    const toastClass = 'toast-' + type;
    
    const toast = document.createElement('div');
    toast.className = `toast ${toastClass} show`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.id = toastId;
    
    const toastHeader = document.createElement('div');
    toastHeader.className = 'toast-header';
    
    const icon = document.createElement('i');
    icon.className = getToastIcon(type);
    icon.style.marginRight = '0.5rem';
    
    const titleElement = document.createElement('strong');
    titleElement.className = 'me-auto';
    titleElement.textContent = title;
    
    const closeButton = document.createElement('button');
    closeButton.className = 'btn-close';
    closeButton.setAttribute('type', 'button');
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');
    closeButton.addEventListener('click', function() {
        toast.remove();
    });
    
    toastHeader.appendChild(icon);
    toastHeader.appendChild(titleElement);
    toastHeader.appendChild(closeButton);
    
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body';
    toastBody.textContent = message;
    
    toast.appendChild(toastHeader);
    toast.appendChild(toastBody);
    
    toastContainer.appendChild(toast);
    
    // Auto-remove toast after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

/**
 * Get icon class for toast notification
 * 
 * @param {string} type - Toast type
 * @returns {string} Icon class
 */
function getToastIcon(type) {
    switch (type) {
        case 'success':
            return 'bi bi-check-circle-fill text-success';
        case 'error':
            return 'bi bi-exclamation-circle-fill text-danger';
        case 'warning':
            return 'bi bi-exclamation-triangle-fill text-warning';
        case 'info':
        default:
            return 'bi bi-info-circle-fill text-info';
    }
}

/**
 * Get alert icon based on alert type
 * 
 * @param {string} type - Alert type
 * @returns {string} Icon class
 */
function getAlertIcon(type) {
    switch (type) {
        case 'success':
            return 'bi-check-circle-fill';
        case 'error':
            return 'bi-exclamation-circle-fill';
        case 'warning':
            return 'bi-exclamation-triangle-fill';
        case 'info':
        default:
            return 'bi-info-circle-fill';
    }
}

/**
 * Capitalize first letter of a string
 * 
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
function capitalizeFirstLetter(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Play notification sound based on notification type
 * 
 * @param {string} type - Notification type (update, alert, success)
 * @param {boolean} enabled - Whether notification sounds are enabled
 */
function playNotificationSound(type = 'update', enabled = true) {
    // Check if notification sounds are enabled
    if (!enabled) return;
    
    // Check if Audio API is supported
    if (typeof Audio === 'undefined') return;
    
    // Define sound files (would be actual sound files in production)
    const soundFiles = {
        update: '/static/sounds/update-notification.mp3',
        alert: '/static/sounds/alert-notification.mp3',
        success: '/static/sounds/success-notification.mp3'
    };
    
    // Use a silent MP3 as fallback since we don't actually have sound files in this demo
    const soundFile = soundFiles[type] || '/static/sounds/silent.mp3';
    
    // Try to play the notification sound
    try {
        // Log instead of playing actual sound for demo purposes
        console.log(`[SOUND] Would play notification sound: ${type}`);
        
        // Uncomment in production when sound files are available
        // const audio = new Audio(soundFile);
        // audio.volume = 0.5;
        // audio.play();
    } catch (error) {
        console.warn('Failed to play notification sound:', error);
    }
}