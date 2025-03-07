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
 * Process real-time BREEAM metric updates
 * 
 * @param {Object} data - BREEAM update data
 */
function processRealtimeBREEAMUpdate(data) {
    // Get the BREEAM real-time updates container
    const realtimeUpdatesContainer = document.getElementById('breeam-realtime-updates');
    if (!realtimeUpdatesContainer) return;
    
    // Create a new update card
    const updateCard = document.createElement('div');
    updateCard.className = 'metric-breakdown-card realtime-update';
    
    updateCard.innerHTML = `
        <div class="metric-header">
            <span>Property ${data.property_id} - ${data.category} Update</span>
            <span class="metric-badge certification">LIVE</span>
        </div>
        <div class="metric-body">
            <div><strong>BREEAM Score:</strong> ${data.score}</div>
            <div><strong>Category:</strong> ${data.category}</div>
            <div><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleTimeString()}</div>
        </div>
    `;
    
    // Add the new update to the container (at the top)
    realtimeUpdatesContainer.prepend(updateCard);
    
    // Limit the number of displayed updates to prevent overflow
    const maxUpdates = 5;
    const updates = realtimeUpdatesContainer.querySelectorAll('.realtime-update');
    if (updates.length > maxUpdates) {
        for (let i = maxUpdates; i < updates.length; i++) {
            updates[i].remove();
        }
    }
    
    // If not already on BREEAM tab, add notification indicator
    if (!document.getElementById('breeam-tab').classList.contains('active')) {
        document.getElementById('breeam-tab').classList.add('has-update');
    }
    
    // Animate the update notification
    updateCard.style.animation = 'highlight-update 2s ease-in-out';
}

/**
 * Process real-time Energy metric updates
 * 
 * @param {Object} data - Energy update data
 */
function processRealtimeEnergyUpdate(data) {
    // Get the Energy real-time updates container
    const realtimeUpdatesContainer = document.getElementById('energy-realtime-updates');
    if (!realtimeUpdatesContainer) return;
    
    // Create a new update card
    const updateCard = document.createElement('div');
    updateCard.className = 'metric-breakdown-card realtime-update';
    
    updateCard.innerHTML = `
        <div class="metric-header">
            <span>Property ${data.property_id} - Energy Update</span>
            <span class="metric-badge energy">LIVE</span>
        </div>
        <div class="metric-body">
            <div><strong>Consumption:</strong> ${data.consumption} ${data.unit}</div>
            <div><strong>Trend:</strong> ${data.trend}</div>
            <div><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleTimeString()}</div>
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
    
    // If not already on Energy tab, add notification indicator
    if (!document.getElementById('energy-tab').classList.contains('active')) {
        document.getElementById('energy-tab').classList.add('has-update');
    }
    
    // Animate the update notification
    updateCard.style.animation = 'highlight-update 2s ease-in-out';
}

/**
 * Process real-time Carbon metric updates
 * 
 * @param {Object} data - Carbon update data
 */
function processRealtimeCarbonUpdate(data) {
    // Get the Carbon real-time updates container
    const realtimeUpdatesContainer = document.getElementById('carbon-realtime-updates');
    if (!realtimeUpdatesContainer) return;
    
    // Create a new update card
    const updateCard = document.createElement('div');
    updateCard.className = 'metric-breakdown-card realtime-update carbon';
    
    // Determine change direction for styling
    const changeClass = data.change < 0 ? 'improved' : (data.change > 0 ? 'declined' : 'neutral');
    const changeIcon = data.change < 0 ? 'bi-arrow-down' : (data.change > 0 ? 'bi-arrow-up' : 'bi-dash');
    
    updateCard.innerHTML = `
        <div class="metric-header">
            <span>Property ${data.property_id} - Carbon Update</span>
            <span class="metric-badge carbon">LIVE</span>
        </div>
        <div class="metric-body">
            <div><strong>Emissions:</strong> ${data.emissions} ${data.unit}</div>
            <div><strong>Reduction:</strong> ${data.reduction}%</div>
            <div><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleTimeString()}</div>
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
    
    // If not already on Carbon tab, add notification indicator
    if (!document.getElementById('carbon-tab').classList.contains('active')) {
        document.getElementById('carbon-tab').classList.add('has-update');
    }
    
    // Animate the update notification
    updateCard.style.animation = 'highlight-update 2s ease-in-out';
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