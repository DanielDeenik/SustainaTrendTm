/**
 * Strategy Simulation & McKinsey-Style Reporting Module
 * JavaScript functionality for framework selection, data processing, 
 * and visualization of strategic insights
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the page
    initStrategySimulation();
    
    // Add event listeners
    setupEventListeners();
});

/**
 * Initialize the strategy simulation page
 */
function initStrategySimulation() {
    console.log('Initializing Strategy Simulation Module');
    
    // Initialize framework selection
    initFrameworkSelection();
    
    // Initialize data source options
    initDataSourceOptions();
    
    // Initialize lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

/**
 * Initialize framework selection with interactive UI
 */
function initFrameworkSelection() {
    const frameworkOptions = document.querySelectorAll('.framework-option');
    
    frameworkOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selection from all options
            frameworkOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selection to clicked option
            this.classList.add('selected');
            
            // Update hidden input value
            const frameworkId = this.dataset.framework;
            console.log(`Selected framework: ${frameworkId}`);
        });
    });
}

/**
 * Initialize data source options
 */
function initDataSourceOptions() {
    const dataSourceRadios = document.querySelectorAll('input[name="dataSource"]');
    const uploadForm = document.getElementById('uploadForm');
    
    dataSourceRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'upload') {
                uploadForm.style.display = 'block';
            } else {
                uploadForm.style.display = 'none';
            }
        });
    });
}

/**
 * Setup all event listeners for the page
 */
function setupEventListeners() {
    // Run analysis button
    const runAnalysisBtn = document.getElementById('runAnalysisBtn');
    if (runAnalysisBtn) {
        runAnalysisBtn.addEventListener('click', runStrategyAnalysis);
    }
    
    // Export buttons
    setupExportButtons();
    
    // File upload
    const uploadButton = document.getElementById('uploadButton');
    if (uploadButton) {
        uploadButton.addEventListener('click', handleFileUpload);
    }
}

/**
 * Setup export buttons for each framework
 */
function setupExportButtons() {
    const exportBtns = document.querySelectorAll('[id$="ExportBtn"]');
    exportBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const frameworkId = this.id.replace('ExportBtn', '');
            exportAnalysis(frameworkId);
        });
    });
    
    const printBtns = document.querySelectorAll('[id$="PrintBtn"]');
    printBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            window.print();
        });
    });
}

/**
 * Handle file upload for custom data
 */
function handleFileUpload() {
    const fileInput = document.getElementById('fileUpload');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select a file to upload', 'alert-triangle', 'warning');
        return;
    }
    
    const allowedTypes = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Please upload an Excel or CSV file', 'alert-triangle', 'warning');
        return;
    }
    
    // In a real implementation, we would upload the file to the server
    // For demo purposes, we'll just show a success message
    showNotification('File uploaded successfully', 'check-circle', 'success');
}

/**
 * Run strategy analysis based on selected framework
 */
function runStrategyAnalysis() {
    const selectedFramework = document.querySelector('.framework-option.selected');
    
    if (!selectedFramework) {
        showNotification('Please select a strategic framework', 'alert-triangle', 'warning');
        return;
    }
    
    const frameworkId = selectedFramework.dataset.framework;
    const companyName = document.getElementById('companyName').value;
    const industry = document.getElementById('industry').value;
    const timeframe = document.getElementById('timeframeSelector').value;
    const focus = document.getElementById('focusSelector').value;
    const dataSource = document.querySelector('input[name="dataSource"]:checked').value;
    
    // Show loading state
    showLoadingState(true);
    
    // Fetch sample data for the selected framework
    fetch(`/api/sample-data?framework_id=${frameworkId}`)
        .then(response => response.json())
        .then(sampleData => {
            // Prepare analysis request
            const analysisRequest = {
                framework_id: frameworkId,
                company_name: companyName,
                industry: industry,
                data: sampleData,
                timeframe: timeframe,
                focus: focus
            };
            
            // Send analysis request to the server
            return fetch('/api/framework-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(analysisRequest)
            });
        })
        .then(response => response.json())
        .then(analysis => {
            // Process and display analysis results
            displayAnalysisResults(frameworkId, analysis);
        })
        .catch(error => {
            console.error('Error running analysis:', error);
            showNotification('Error running analysis', 'alert-circle', 'error');
        })
        .finally(() => {
            showLoadingState(false);
        });
}

/**
 * Display analysis results based on framework type
 */
function displayAnalysisResults(frameworkId, analysis) {
    console.log('Analysis results:', analysis);
    
    // Hide all framework results
    const resultContainers = document.querySelectorAll('.framework-results');
    resultContainers.forEach(container => {
        container.style.display = 'none';
    });
    
    // Show the appropriate framework results
    const resultsContainer = document.getElementById(`${frameworkId}Results`);
    if (resultsContainer) {
        resultsContainer.style.display = 'block';
    }
    
    // Dispatch to specific display function based on framework
    switch (frameworkId) {
        case 'porters':
            displayPortersResults(analysis);
            break;
        case 'swot':
            displaySwotResults(analysis);
            break;
        case 'bcg':
            displayBcgResults(analysis);
            break;
        case 'mckinsey':
            displayMcKinseyResults(analysis);
            break;
        case 'strategy_pyramid':
            displayStrategyPyramidResults(analysis);
            break;
        case 'blue_ocean':
            displayBlueOceanResults(analysis);
            break;
        default:
            showNotification('Unknown framework type', 'alert-circle', 'error');
    }
}

/**
 * Display Porter's Five Forces analysis results
 */
function displayPortersResults(analysis) {
    const attractivenessScore = analysis.attractiveness_score;
    const fiveForces = analysis.five_forces;
    const insights = analysis.strategic_insights;
    const opportunities = analysis.strategic_opportunities;
    
    // Update attractiveness meter
    const attractivenessMeter = document.getElementById('portersAttractivenessValue');
    if (attractivenessMeter) {
        const percentage = (attractivenessScore / 5) * 100;
        attractivenessMeter.style.width = `${percentage}%`;
    }
    
    // Update main insight
    const mainInsightElement = document.getElementById('portersMainInsight');
    if (mainInsightElement && insights && insights.length > 0) {
        mainInsightElement.textContent = insights[0];
    }
    
    // Update forces list
    const forcesListElement = document.getElementById('portersForcesList');
    if (forcesListElement) {
        forcesListElement.innerHTML = '';
        
        for (const [force, data] of Object.entries(fiveForces)) {
            const forceItem = document.createElement('li');
            const forceName = force.replace(/_/g, ' ');
            const scorePercentage = (data.score / 5) * 100;
            
            forceItem.innerHTML = `
                <span class="metric-name">${forceName.charAt(0).toUpperCase() + forceName.slice(1)}</span>
                <div class="metric-bar-container">
                    <div class="metric-bar" style="width: ${scorePercentage}%"></div>
                </div>
                <span class="metric-value">${data.score.toFixed(1)}</span>
            `;
            
            forcesListElement.appendChild(forceItem);
        }
    }
    
    // Update opportunities list
    const opportunitiesElement = document.getElementById('portersOpportunitiesList');
    if (opportunitiesElement && opportunities) {
        opportunitiesElement.innerHTML = '';
        
        opportunities.forEach(opportunity => {
            const opportunityItem = document.createElement('div');
            opportunityItem.className = 'opportunity-card';
            
            opportunityItem.innerHTML = `
                <h5>${opportunity.name}</h5>
                <p>${opportunity.description}</p>
                <div class="opportunity-meta">
                    <span class="badge bg-primary">Impact: ${opportunity.impact.toFixed(1)}</span>
                    <span class="badge bg-secondary">${opportunity.timeframe}</span>
                    <span class="badge bg-info">Resources: ${opportunity.resources_required}</span>
                </div>
            `;
            
            opportunitiesElement.appendChild(opportunityItem);
        });
    }
    
    // Create forces visualization using D3.js
    createForcesVisualization(fiveForces);
}

/**
 * Create the Porter's Five Forces visualization using D3.js
 */
function createForcesVisualization(fiveForces) {
    const visualizationContainer = document.getElementById('forcesVisualization');
    if (!visualizationContainer) return;
    
    // Clear previous visualization
    visualizationContainer.innerHTML = '';
    
    // Create SVG container
    const width = visualizationContainer.clientWidth;
    const height = 500;
    const svg = d3.select(visualizationContainer)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');
    
    // Define colors based on score (red = high force = bad, green = low force = good)
    const colorScale = d3.scaleLinear()
        .domain([1, 3, 5])
        .range(['#4CAF50', '#FFC107', '#F44336']);
    
    // Create a forces array from the fiveForces object
    const forcesArray = Object.entries(fiveForces).map(([key, value]) => ({
        id: key,
        name: key.replace(/_/g, ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
        score: value.score,
        factors: value.factors,
        summary: value.summary
    }));
    
    // Add central circle
    svg.append('circle')
        .attr('cx', width / 2)
        .attr('cy', height / 2)
        .attr('r', 100)
        .attr('fill', '#1976D2')
        .attr('opacity', 0.8);
    
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('fill', 'white')
        .attr('font-weight', 'bold')
        .text('Industry');
    
    // Calculate positions for five forces
    const angleStep = (2 * Math.PI) / forcesArray.length;
    const radius = 180;
    
    // Draw forces
    forcesArray.forEach((force, i) => {
        const angle = i * angleStep - Math.PI / 2; // Start from top
        const x = width / 2 + radius * Math.cos(angle);
        const y = height / 2 + radius * Math.sin(angle);
        
        // Connect to center with arrow
        const startX = width / 2 + 100 * Math.cos(angle);
        const startY = height / 2 + 100 * Math.sin(angle);
        
        svg.append('line')
            .attr('x1', startX)
            .attr('y1', startY)
            .attr('x2', x)
            .attr('y2', y)
            .attr('stroke', colorScale(force.score))
            .attr('stroke-width', 3 + force.score / 2)
            .attr('marker-end', 'url(#arrowhead)')
            .attr('opacity', 0.7);
        
        // Force circle
        svg.append('circle')
            .attr('cx', x)
            .attr('cy', y)
            .attr('r', 60)
            .attr('fill', colorScale(force.score))
            .attr('opacity', 0.8)
            .attr('class', 'force-circle')
            .attr('data-force-id', force.id)
            .attr('data-toggle', 'tooltip')
            .attr('title', force.summary);
        
        // Force name
        const words = force.name.split(' ');
        if (words.length === 1) {
            svg.append('text')
                .attr('x', x)
                .attr('y', y)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'middle')
                .attr('fill', 'white')
                .attr('font-weight', 'bold')
                .text(force.name);
        } else {
            // Multi-line text for longer names
            svg.append('text')
                .attr('x', x)
                .attr('y', y - 10)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'middle')
                .attr('fill', 'white')
                .attr('font-weight', 'bold')
                .text(words.slice(0, words.length / 2).join(' '));
                
            svg.append('text')
                .attr('x', x)
                .attr('y', y + 10)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'middle')
                .attr('fill', 'white')
                .attr('font-weight', 'bold')
                .text(words.slice(words.length / 2).join(' '));
        }
        
        // Force score
        svg.append('text')
            .attr('x', x)
            .attr('y', y + 30)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('fill', 'white')
            .attr('font-size', '18px')
            .text(force.score.toFixed(1));
    });
    
    // Add arrow marker definition
    svg.append('defs')
        .append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 8)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#555');
}

/**
 * Display SWOT analysis results
 */
function displaySwotResults(analysis) {
    // Implementation for SWOT analysis display
    console.log('Displaying SWOT analysis');
    
    // Set strategic posture
    document.getElementById('strategicPosture').textContent = analysis.strategic_posture || 'Growth-Oriented';
    
    // Set main insight
    document.getElementById('swotMainInsight').textContent = analysis.main_insight || 'Sustainability initiatives show strong growth potential with key advantages in energy efficiency and certification leadership.';
    
    // Populate SWOT quadrants
    populateSwotList('strengthsList', analysis.strengths || []);
    populateSwotList('weaknessesList', analysis.weaknesses || []);
    populateSwotList('opportunitiesList', analysis.opportunities || []);
    populateSwotList('threatsList', analysis.threats || []);
    
    // Populate cross-strategies
    populateCrossStrategies(analysis.cross_strategies || []);
}

/**
 * Populate a SWOT quadrant list
 */
function populateSwotList(elementId, items) {
    const listElement = document.getElementById(elementId);
    if (!listElement) return;
    
    listElement.innerHTML = '';
    
    items.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'swot-item';
        
        itemDiv.innerHTML = `
            <h6>${item.title}</h6>
            <p>${item.description}</p>
            <div class="impact-meter">
                <div class="impact-fill" style="width: ${(item.impact / 5) * 100}%"></div>
            </div>
            <div class="item-evidence">
                <small>${item.evidence || ''}</small>
            </div>
        `;
        
        listElement.appendChild(itemDiv);
    });
}

/**
 * Populate cross-strategies
 */
function populateCrossStrategies(strategies) {
    const strategiesElement = document.getElementById('crossStrategiesList');
    if (!strategiesElement) return;
    
    strategiesElement.innerHTML = '';
    
    strategies.forEach(strategy => {
        const strategyDiv = document.createElement('div');
        strategyDiv.className = 'cross-strategy-card';
        
        strategyDiv.innerHTML = `
            <div class="strategy-header">
                <h5>${strategy.title}</h5>
                <span class="strategy-type">${strategy.type}</span>
            </div>
            <p>${strategy.description}</p>
            <div class="strategy-elements">
                <span class="badge bg-success">${strategy.strength || 'S: Energy Efficiency'}</span>
                <span class="badge bg-danger">${strategy.weakness || 'W: Implementation Costs'}</span>
                <span class="badge bg-primary">${strategy.opportunity || 'O: Green Premium'}</span>
                <span class="badge bg-warning">${strategy.threat || 'T: Regulatory Changes'}</span>
            </div>
        `;
        
        strategiesElement.appendChild(strategyDiv);
    });
}

/**
 * Display BCG Growth-Share Matrix analysis results
 */
function displayBcgResults(analysis) {
    // Implementation for BCG Matrix display
    console.log('Displaying BCG Matrix analysis');
    
    // Set main insight
    document.getElementById('bcgMainInsight').textContent = analysis.main_insight || 'Portfolio shows strong growth potential in urban office properties, with significant star assets in energy-efficient buildings.';
    
    // Populate metrics list
    populateMetricsList('bcgMetricsList', analysis.metrics || [
        { name: 'Stars', value: '35%', description: 'High growth, high share properties' },
        { name: 'Cash Cows', value: '28%', description: 'Low growth, high share properties' },
        { name: 'Question Marks', value: '22%', description: 'High growth, low share properties' },
        { name: 'Dogs', value: '15%', description: 'Low growth, low share properties' }
    ]);
    
    // Create BCG Matrix visualization
    createBcgMatrixVisualization(analysis.properties || generateMockBcgData());
    
    // Populate property categories table
    populatePropertyCategoriesTable(analysis.property_categories || generateMockBcgData());
    
    // Populate recommendations
    populateRecommendationsList('bcgRecommendationsList', analysis.recommendations || []);
}

/**
 * Generate mock BCG data for visualization
 */
function generateMockBcgData() {
    return [
        { name: 'Urban Office A', quadrant: 'star', growth: 12.5, share: 1.8, size: 35, category: 'Office' },
        { name: 'Suburban Office B', quadrant: 'cashcow', growth: 3.2, share: 1.6, size: 25, category: 'Office' },
        { name: 'Retail C', quadrant: 'questionmark', growth: 9.8, share: 0.7, size: 15, category: 'Retail' },
        { name: 'Industrial D', quadrant: 'dog', growth: 1.5, share: 0.5, size: 10, category: 'Industrial' },
        { name: 'Residential E', quadrant: 'star', growth: 15.2, share: 1.2, size: 15, category: 'Residential' }
    ];
}

/**
 * Create the BCG Matrix visualization using D3.js
 */
function createBcgMatrixVisualization(properties) {
    const container = document.getElementById('bcgMatrixVisualization');
    if (!container) return;
    
    // Clear previous visualization
    container.innerHTML = '';
    
    // Create SVG container
    const width = container.clientWidth;
    const height = 500;
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');
    
    // Define margins
    const margin = { top: 40, right: 40, bottom: 60, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    // Create scales
    const xScale = d3.scaleLinear()
        .domain([0, 2])
        .range([0, innerWidth]);
    
    const yScale = d3.scaleLinear()
        .domain([0, 20])
        .range([innerHeight, 0]);
    
    const sizeScale = d3.scaleLinear()
        .domain([0, 100])
        .range([10, 50]);
    
    // Create axes
    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);
    
    // Add group for inner content
    const g = svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);
    
    // Add quadrant lines
    g.append('line')
        .attr('x1', xScale(1))
        .attr('y1', 0)
        .attr('x2', xScale(1))
        .attr('y2', innerHeight)
        .attr('stroke', '#aaa')
        .attr('stroke-dasharray', '5,5');
    
    g.append('line')
        .attr('x1', 0)
        .attr('y1', yScale(10))
        .attr('x2', innerWidth)
        .attr('y2', yScale(10))
        .attr('stroke', '#aaa')
        .attr('stroke-dasharray', '5,5');
    
    // Add quadrant labels
    g.append('text')
        .attr('x', innerWidth * 0.25)
        .attr('y', innerHeight * 0.25)
        .attr('text-anchor', 'middle')
        .attr('fill', '#555')
        .text('QUESTION MARKS');
    
    g.append('text')
        .attr('x', innerWidth * 0.75)
        .attr('y', innerHeight * 0.25)
        .attr('text-anchor', 'middle')
        .attr('fill', '#555')
        .text('STARS');
    
    g.append('text')
        .attr('x', innerWidth * 0.25)
        .attr('y', innerHeight * 0.75)
        .attr('text-anchor', 'middle')
        .attr('fill', '#555')
        .text('DOGS');
    
    g.append('text')
        .attr('x', innerWidth * 0.75)
        .attr('y', innerHeight * 0.75)
        .attr('text-anchor', 'middle')
        .attr('fill', '#555')
        .text('CASH COWS');
    
    // Add axes
    g.append('g')
        .attr('transform', `translate(0, ${innerHeight})`)
        .call(xAxis);
    
    g.append('g')
        .call(yAxis);
    
    // Add axis labels
    g.append('text')
        .attr('x', innerWidth / 2)
        .attr('y', innerHeight + 40)
        .attr('text-anchor', 'middle')
        .text('Relative Market Share');
    
    g.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -innerHeight / 2)
        .attr('y', -40)
        .attr('text-anchor', 'middle')
        .text('Market Growth Rate (%)');
    
    // Define color mapping for quadrants
    const colorMap = {
        'star': '#FFD700',
        'cashcow': '#4CAF50',
        'questionmark': '#2196F3',
        'dog': '#F44336'
    };
    
    // Add data points
    g.selectAll('.bcg-bubble')
        .data(properties)
        .enter()
        .append('circle')
        .attr('class', 'bcg-bubble')
        .attr('cx', d => xScale(d.share))
        .attr('cy', d => yScale(d.growth))
        .attr('r', d => sizeScale(d.size))
        .attr('fill', d => colorMap[d.quadrant] || '#999')
        .attr('opacity', 0.7)
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .attr('data-toggle', 'tooltip')
        .attr('title', d => `${d.name}: Growth ${d.growth}%, Share ${d.share}`);
    
    // Add property labels
    g.selectAll('.bcg-label')
        .data(properties)
        .enter()
        .append('text')
        .attr('class', 'bcg-label')
        .attr('x', d => xScale(d.share))
        .attr('y', d => yScale(d.growth) - sizeScale(d.size) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '12px')
        .text(d => d.name);
}

/**
 * Populate property categories table
 */
function populatePropertyCategoriesTable(properties) {
    const tableBody = document.querySelector('#propertyCategories tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    properties.forEach(property => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${property.name}</td>
            <td><span class="badge bg-${getBadgeColorForQuadrant(property.quadrant)}">${capitalizeFirstLetter(property.quadrant)}</span></td>
            <td>${property.growth.toFixed(1)}%</td>
            <td>${property.share.toFixed(1)}</td>
            <td>${property.size}%</td>
            <td>${property.category}</td>
            <td>${getRecommendationForQuadrant(property.quadrant)}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Get badge color for BCG quadrant
 */
function getBadgeColorForQuadrant(quadrant) {
    const colorMap = {
        'star': 'warning',
        'cashcow': 'success',
        'questionmark': 'info',
        'dog': 'danger'
    };
    
    return colorMap[quadrant] || 'secondary';
}

/**
 * Get recommendation for BCG quadrant
 */
function getRecommendationForQuadrant(quadrant) {
    const recommendationMap = {
        'star': 'Invest & Grow',
        'cashcow': 'Harvest & Maintain',
        'questionmark': 'Analyze & Selectively Invest',
        'dog': 'Divest or Reposition'
    };
    
    return recommendationMap[quadrant] || '';
}

/**
 * Display McKinsey 9-Box Matrix analysis results
 */
function displayMcKinseyResults(analysis) {
    // Implementation for McKinsey Matrix display
    console.log('Displaying McKinsey 9-Box Matrix analysis');
    
    // Set main insight
    document.getElementById('mckinseyMainInsight').textContent = analysis.main_insight || 'Portfolio shows strong potential in high sustainability performance assets, with clear competitive advantage in energy-efficient buildings.';
    
    // Create McKinsey Matrix visualization
    createMcKinseyMatrixVisualization(analysis.properties || generateMockMcKinseyData());
    
    // Populate investment strategies
    populateInvestmentStrategies(analysis.investment_strategies || []);
}

/**
 * Generate mock McKinsey data
 */
function generateMockMcKinseyData() {
    return [
        { name: 'Urban Office A', market_attractiveness: 4.2, competitive_position: 3.8, size: 30 },
        { name: 'Suburban Office B', market_attractiveness: 3.5, competitive_position: 4.2, size: 25 },
        { name: 'Retail C', market_attractiveness: 2.8, competitive_position: 1.9, size: 15 },
        { name: 'Industrial D', market_attractiveness: 1.5, competitive_position: 2.2, size: 10 },
        { name: 'Residential E', market_attractiveness: 4.5, competitive_position: 3.2, size: 20 }
    ];
}

/**
 * Display Strategy Pyramid results
 */
function displayStrategyPyramidResults(analysis) {
    // Implementation for Strategy Pyramid display
    console.log('Displaying Strategy Pyramid analysis');
    
    // Update the pyramid visualization (simplified implementation)
    document.getElementById('pyramidMission').textContent = analysis.mission || 'Lead sustainable real estate transformation';
    document.getElementById('pyramidObjectives').textContent = analysis.objectives?.[0] || 'Reduce carbon footprint by 50% by 2030';
    document.getElementById('pyramidStrategies').textContent = analysis.strategies?.[0] || 'Implement energy efficiency across portfolio';
    
    // Populate KPIs
    populateKpiTable(analysis.kpis || []);
    
    // Populate action items
    populateActionItems(analysis.action_items || []);
}

/**
 * Populate KPI table
 */
function populateKpiTable(kpis) {
    const kpiTableBody = document.querySelector('#kpiTable tbody');
    if (!kpiTableBody) return;
    
    kpiTableBody.innerHTML = '';
    
    kpis.forEach(kpi => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${kpi.name}</td>
            <td>${kpi.category}</td>
            <td>${kpi.current}</td>
            <td>${kpi.target}</td>
            <td>${kpi.timeframe}</td>
            <td>${getStatusBadge(kpi.status)}</td>
        `;
        kpiTableBody.appendChild(row);
    });
}

/**
 * Display Blue Ocean Strategy results
 */
function displayBlueOceanResults(analysis) {
    // Implementation for Blue Ocean Strategy display
    console.log('Displaying Blue Ocean Strategy analysis');
    
    // Update strategy canvas
    createBlueOceanCanvas(analysis.factors || []);
    
    // Populate ERRC grid
    populateErrcGrid(analysis.errc_grid || {});
    
    // Populate implementation initiatives
    populateInitiativesList(analysis.implementation_initiatives || []);
    
    // Populate non-customer opportunities
    populateOpportunitiesList(analysis.noncustomer_opportunities || []);
}

/**
 * Toggle visibility of the loading state
 */
function showLoadingState(show) {
    const initialState = document.querySelector('.initial-state');
    const loadingState = document.getElementById('loadingState');
    const resultContainers = document.querySelectorAll('.framework-results');
    
    if (show) {
        if (initialState) initialState.style.display = 'none';
        if (loadingState) loadingState.style.display = 'block';
        resultContainers.forEach(container => {
            container.style.display = 'none';
        });
    } else {
        if (loadingState) loadingState.style.display = 'none';
    }
}

/**
 * Export analysis results to PDF or Excel
 */
function exportAnalysis(frameworkId) {
    console.log(`Exporting ${frameworkId} analysis`);
    showNotification('Export feature will be available in the next update', 'info', 'info');
}

/**
 * Show a notification toast message
 */
function showNotification(message, icon, type) {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type || 'info'}`;
    toast.innerHTML = `
        <div class="toast-icon">
            <i data-lucide="${icon || 'info'}"></i>
        </div>
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="this.parentNode.remove()">×</button>
    `;
    
    document.body.appendChild(toast);
    
    // Initialize the Lucide icon
    if (typeof lucide !== 'undefined') {
        lucide.createIcons({
            attrs: {
                class: ["toast-icon-svg"]
            }
        }, document.querySelectorAll('.toast-icon svg'));
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.classList.add('toast-hiding');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }, 5000);
}

/**
 * Helper function to capitalize the first letter of a string
 */
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Populate a metrics list
 */
function populateMetricsList(elementId, metrics) {
    const listElement = document.getElementById(elementId);
    if (!listElement) return;
    
    listElement.innerHTML = '';
    
    metrics.forEach(metric => {
        const metricItem = document.createElement('li');
        
        metricItem.innerHTML = `
            <span class="metric-name">${metric.name}</span>
            <span class="metric-value">${metric.value}</span>
            <small class="metric-description">${metric.description || ''}</small>
        `;
        
        listElement.appendChild(metricItem);
    });
}

/**
 * Get a status badge HTML
 */
function getStatusBadge(status) {
    const colorMap = {
        'on_track': 'success',
        'at_risk': 'warning',
        'off_track': 'danger',
        'not_started': 'secondary',
        'completed': 'info'
    };
    
    const color = colorMap[status] || 'secondary';
    const label = status.replace('_', ' ');
    
    return `<span class="badge bg-${color}">${capitalizeFirstLetter(label)}</span>`;
}