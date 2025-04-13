/**
 * Strategy Card Component JavaScript
 * 
 * This script handles the interactive functionality for the AI Strategy Card
 * including dynamic recommendation categorization by timeframe (Quick Wins, Medium-term, Long-term).
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize strategy card interactions
    initStrategyCard();
    
    // Set up event listeners for form submission
    if (document.getElementById('aiConsultantForm')) {
        document.getElementById('aiConsultantForm').addEventListener('submit', function(e) {
            e.preventDefault();
            generateStrategyAnalysis();
        });
    }
    
    // Toggle framework selection pills
    document.querySelectorAll('.framework-badge').forEach(badge => {
        badge.addEventListener('click', function() {
            this.classList.toggle('active');
            const framework = this.getAttribute('data-framework');
            const checkbox = document.getElementById('framework' + framework.replace(/[^a-zA-Z0-9]/g, ''));
            if (checkbox) {
                checkbox.checked = this.classList.contains('active');
            }
        });
    });
    
    // Set up document generation button
    if (document.getElementById('generateDocumentBtn')) {
        document.getElementById('generateDocumentBtn').addEventListener('click', generateStrategyDocument);
    }
    
    // Set up export button
    if (document.getElementById('exportStrategyBtn')) {
        document.getElementById('exportStrategyBtn').addEventListener('click', exportStrategyData);
    }
    
    // Set up back to analysis button
    if (document.getElementById('backToAnalysisBtn')) {
        document.getElementById('backToAnalysisBtn').addEventListener('click', resetAnalysisForm);
    }
});

/**
 * Initialize the strategy card components and interactions
 */
function initStrategyCard() {
    // Implement any initialization code here
    console.log('Strategy Card initialized');
}

/**
 * Generate strategy analysis based on form inputs
 */
function generateStrategyAnalysis() {
    const trendInput = document.getElementById('trendInput').value;
    const industryInput = document.getElementById('industryInput').value;
    const timeframeInput = document.getElementById('timeframeInput').value;
    const outputFormat = document.getElementById('outputFormatInput').value;
    
    // Validate inputs
    if (!trendInput || !industryInput) {
        alert('Please enter both trend and industry information.');
        return;
    }
    
    // Get selected frameworks
    const frameworks = [];
    document.querySelectorAll('.framework-badge.active').forEach(badge => {
        frameworks.push(badge.getAttribute('data-framework'));
    });
    
    // Show loading animation
    document.getElementById('consultantInputContainer').style.display = 'none';
    document.getElementById('analysisLoading').style.display = 'block';
    
    // Prepare request data
    const requestData = {
        companyName: "SustainaTrend", // Default company name
        industry: industryInput,
        focusAreas: trendInput,
        trendInput: trendInput,
        frameworks: frameworks,
        timeframe: timeframeInput,
        outputFormat: outputFormat
    };
    
    // Make API request
    fetch('/api/strategy/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            displayStrategyResults(data, trendInput, industryInput, timeframeInput);
        } else {
            alert('Error generating analysis: ' + data.message);
            resetAnalysisForm();
        }
    })
    .catch(error => {
        console.error('Error generating strategy analysis:', error);
        alert('An error occurred while generating the analysis. Please try again.');
        resetAnalysisForm();
    });
}

/**
 * Display strategy analysis results with timeframe categorization
 */
function displayStrategyResults(data, trendInput, industryInput, timeframeInput) {
    // Hide loading animation
    document.getElementById('analysisLoading').style.display = 'none';
    document.getElementById('analysisResults').style.display = 'block';
    
    // Set title and industry badge
    document.getElementById('resultsTrendTitle').textContent = trendInput;
    document.getElementById('resultIndustryBadge').textContent = industryInput;
    
    // Set timeframe badge
    const timeframeBadge = document.getElementById('resultTimeframeBadge');
    if (timeframeBadge) {
        const timeframeText = document.getElementById('timeframeInput').options[document.getElementById('timeframeInput').selectedIndex].text;
        timeframeBadge.textContent = timeframeText;
    }
    
    // Set analysis summary
    document.getElementById('analysisSummary').textContent = data.summary || 'Analysis completed successfully.';
    
    // Categorize recommendations by timeframe
    categorizeRecommendationsByTimeframe(data);
    
    // Populate other sections
    populateOpportunitiesAndThreats(data);
    
    // Populate frameworks section
    populateFrameworksAnalysis(data);
    
    // Populate KPIs section
    populateKPIs(data);
}

/**
 * Categorize recommendations by timeframe (Quick Wins, Medium-term, Long-term)
 */
function categorizeRecommendationsByTimeframe(data) {
    // Clear existing lists
    const quickWinsList = document.getElementById('quickWinsList');
    const mediumTermList = document.getElementById('mediumTermList');
    const longTermList = document.getElementById('longTermList');
    
    if (quickWinsList) quickWinsList.innerHTML = '';
    if (mediumTermList) mediumTermList.innerHTML = '';
    if (longTermList) longTermList.innerHTML = '';
    
    // Helper function to create recommendation item
    function createRecommendationItem(text) {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent border-0 py-2 ps-0';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'd-flex align-items-start';
        
        const iconSpan = document.createElement('span');
        iconSpan.className = 'me-2 text-success';
        iconSpan.innerHTML = '<i class="fas fa-check-circle"></i>';
        
        const textSpan = document.createElement('span');
        textSpan.textContent = text;
        
        contentDiv.appendChild(iconSpan);
        contentDiv.appendChild(textSpan);
        li.appendChild(contentDiv);
        
        return li;
    }
    
    // Process recommendations if available
    if (data.recommendations && Array.isArray(data.recommendations)) {
        // Categorize recommendations based on timeframe keywords
        data.recommendations.forEach(rec => {
            let recommendation = typeof rec === 'string' ? rec : rec.text || '';
            
            // Simplified categorization logic based on keywords and phrases
            const lowerRec = recommendation.toLowerCase();
            
            if (lowerRec.includes('immediate') || lowerRec.includes('quick') || 
                lowerRec.includes('short-term') || lowerRec.includes('first step') ||
                lowerRec.includes('right away') || lowerRec.includes('immediately')) {
                
                if (quickWinsList) quickWinsList.appendChild(createRecommendationItem(recommendation));
            }
            else if (lowerRec.includes('long-term') || lowerRec.includes('future') || 
                    lowerRec.includes('eventually') || lowerRec.includes('5 year') ||
                    lowerRec.includes('transform') || lowerRec.includes('strategy')) {
                
                if (longTermList) longTermList.appendChild(createRecommendationItem(recommendation));
            }
            else {
                // Default to medium-term
                if (mediumTermList) mediumTermList.appendChild(createRecommendationItem(recommendation));
            }
        });
    }
    
    // If any list is empty, add a placeholder item
    if (quickWinsList && quickWinsList.children.length === 0) {
        const placeholderItem = document.createElement('li');
        placeholderItem.className = 'list-group-item bg-transparent border-0 py-2 ps-0 text-muted';
        placeholderItem.textContent = 'No quick wins identified for this trend.';
        quickWinsList.appendChild(placeholderItem);
    }
    
    if (mediumTermList && mediumTermList.children.length === 0) {
        const placeholderItem = document.createElement('li');
        placeholderItem.className = 'list-group-item bg-transparent border-0 py-2 ps-0 text-muted';
        placeholderItem.textContent = 'No medium-term actions identified for this trend.';
        mediumTermList.appendChild(placeholderItem);
    }
    
    if (longTermList && longTermList.children.length === 0) {
        const placeholderItem = document.createElement('li');
        placeholderItem.className = 'list-group-item bg-transparent border-0 py-2 ps-0 text-muted';
        placeholderItem.textContent = 'No long-term strategic actions identified for this trend.';
        longTermList.appendChild(placeholderItem);
    }
}

/**
 * Populate opportunities and threats sections
 */
function populateOpportunitiesAndThreats(data) {
    const opportunitiesList = document.getElementById('opportunitiesList');
    const threatsList = document.getElementById('threatsList');
    
    if (opportunitiesList) opportunitiesList.innerHTML = '';
    if (threatsList) threatsList.innerHTML = '';
    
    // Helper function to create list item
    function createListItem(text, iconClass, colorClass) {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent border-0 py-2 ps-0';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'd-flex align-items-start';
        
        const iconSpan = document.createElement('span');
        iconSpan.className = `me-2 ${colorClass}`;
        iconSpan.innerHTML = `<i class="${iconClass}"></i>`;
        
        const textSpan = document.createElement('span');
        textSpan.textContent = text;
        
        contentDiv.appendChild(iconSpan);
        contentDiv.appendChild(textSpan);
        li.appendChild(contentDiv);
        
        return li;
    }
    
    // Process opportunities
    if (data.opportunities && Array.isArray(data.opportunities)) {
        data.opportunities.forEach(opp => {
            const opportunity = typeof opp === 'string' ? opp : opp.text || '';
            if (opportunitiesList) {
                opportunitiesList.appendChild(createListItem(opportunity, 'fas fa-arrow-up', 'text-success'));
            }
        });
    }
    
    // Process threats
    if (data.threats && Array.isArray(data.threats)) {
        data.threats.forEach(threat => {
            const threatText = typeof threat === 'string' ? threat : threat.text || '';
            if (threatsList) {
                threatsList.appendChild(createListItem(threatText, 'fas fa-exclamation-triangle', 'text-warning'));
            }
        });
    }
    
    // If lists are empty, add placeholders
    if (opportunitiesList && opportunitiesList.children.length === 0) {
        const placeholderItem = document.createElement('li');
        placeholderItem.className = 'list-group-item bg-transparent border-0 py-2 ps-0 text-muted';
        placeholderItem.textContent = 'No specific opportunities identified for this trend.';
        opportunitiesList.appendChild(placeholderItem);
    }
    
    if (threatsList && threatsList.children.length === 0) {
        const placeholderItem = document.createElement('li');
        placeholderItem.className = 'list-group-item bg-transparent border-0 py-2 ps-0 text-muted';
        placeholderItem.textContent = 'No specific risks identified for this trend.';
        threatsList.appendChild(placeholderItem);
    }
}

/**
 * Populate frameworks analysis section with visualizations
 */
function populateFrameworksAnalysis(data) {
    const frameworksContent = document.getElementById('frameworkAnalysisContent');
    if (!frameworksContent) return;
    
    // Clear existing content
    frameworksContent.innerHTML = '';
    
    // Add STEPPS spider chart if available and container exists
    const steppsChartContainer = document.getElementById('steppsSpiderChart');
    if (steppsChartContainer && data.steppsAnalysis) {
        renderSteppsSpiderChart(steppsChartContainer, data.steppsAnalysis);
    }
    
    // Add framework analysis text
    if (data.frameworkAnalysis) {
        const frameworkTexts = Array.isArray(data.frameworkAnalysis) ? 
            data.frameworkAnalysis : 
            [data.frameworkAnalysis];
            
        frameworkTexts.forEach(framework => {
            const frameworkCard = document.createElement('div');
            frameworkCard.className = 'card bg-darker border-0 rounded-4 shadow-sm mb-3';
            
            const cardBody = document.createElement('div');
            cardBody.className = 'card-body p-3';
            
            const frameworkName = typeof framework === 'object' && framework.name ? 
                framework.name : 'Framework Analysis';
                
            const frameworkText = typeof framework === 'object' && framework.analysis ? 
                framework.analysis : (typeof framework === 'string' ? framework : '');
            
            const titleHeading = document.createElement('h6');
            titleHeading.className = 'mb-3';
            titleHeading.innerHTML = `<i class="fas fa-chart-line me-2"></i>${frameworkName}`;
            
            const contentPara = document.createElement('p');
            contentPara.className = 'mb-0';
            contentPara.textContent = frameworkText;
            
            cardBody.appendChild(titleHeading);
            cardBody.appendChild(contentPara);
            frameworkCard.appendChild(cardBody);
            
            frameworksContent.appendChild(frameworkCard);
        });
    } else {
        // Add placeholder if no framework analysis available
        const placeholderDiv = document.createElement('div');
        placeholderDiv.className = 'alert alert-info bg-info bg-opacity-10 border-0';
        placeholderDiv.innerHTML = '<i class="fas fa-info-circle me-2"></i> Detailed framework analysis will appear here when generated.';
        frameworksContent.appendChild(placeholderDiv);
    }
}

/**
 * Render a STEPPS spider chart
 */
function renderSteppsSpiderChart(container, steppsData) {
    // Check if chart libraries are available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js library not loaded');
        container.innerHTML = '<div class="alert alert-warning">Chart visualization library not available</div>';
        return;
    }
    
    // Clear the container
    container.innerHTML = '';
    
    // Create canvas for chart
    const canvas = document.createElement('canvas');
    canvas.id = 'steppsChart';
    canvas.height = 300;
    container.appendChild(canvas);
    
    // Prepare data from STEPPS analysis
    let labels = [];
    let dataPoints = [];
    
    // Check if steppsData is in component format
    if (typeof steppsData === 'object' && steppsData.components) {
        Object.entries(steppsData.components).forEach(([key, value]) => {
            labels.push(key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' '));
            dataPoints.push(value.score || value);
        });
    } 
    // Check if steppsData is in direct object format
    else if (typeof steppsData === 'object') {
        Object.entries(steppsData).forEach(([key, value]) => {
            if (key !== 'overall_score' && key !== 'virality_rating') {
                labels.push(key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' '));
                dataPoints.push(typeof value === 'object' ? value.score : value);
            }
        });
    }
    
    // Create the chart
    new Chart(canvas, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'STEPPS Analysis',
                data: dataPoints,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    ticks: {
                        backdropColor: 'transparent',
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            }
        }
    });
}

/**
 * Populate KPIs section
 */
function populateKPIs(data) {
    const kpisList = document.getElementById('kpisList');
    if (!kpisList) return;
    
    // Clear existing content
    kpisList.innerHTML = '';
    
    // Check if KPIs are available
    if (data.kpis && Array.isArray(data.kpis) && data.kpis.length > 0) {
        data.kpis.forEach(kpi => {
            const kpiText = typeof kpi === 'string' ? kpi : (kpi.name || kpi.text || '');
            const kpiDescription = typeof kpi === 'object' ? (kpi.description || '') : '';
            
            const kpiCol = document.createElement('div');
            kpiCol.className = 'col-md-6 col-lg-4';
            
            const kpiCard = document.createElement('div');
            kpiCard.className = 'card bg-darker border-0 rounded-4 shadow-sm h-100';
            
            const cardBody = document.createElement('div');
            cardBody.className = 'card-body p-3';
            
            const kpiHeading = document.createElement('h6');
            kpiHeading.className = 'mb-2 d-flex align-items-center text-primary';
            kpiHeading.innerHTML = `<i class="fas fa-chart-line me-2"></i>${kpiText}`;
            
            cardBody.appendChild(kpiHeading);
            
            if (kpiDescription) {
                const descriptionPara = document.createElement('p');
                descriptionPara.className = 'mb-0 small text-muted';
                descriptionPara.textContent = kpiDescription;
                cardBody.appendChild(descriptionPara);
            }
            
            kpiCard.appendChild(cardBody);
            kpiCol.appendChild(kpiCard);
            kpisList.appendChild(kpiCol);
        });
    } else {
        // Add default KPIs if none provided
        const defaultKpis = [
            { name: 'Carbon Reduction', description: 'Track direct emissions reduction over time' },
            { name: 'Resource Efficiency', description: 'Measure change in resource consumption per unit' },
            { name: 'Stakeholder Engagement', description: 'Monitor engagement rate with sustainability initiatives' }
        ];
        
        defaultKpis.forEach(kpi => {
            const kpiCol = document.createElement('div');
            kpiCol.className = 'col-md-6 col-lg-4';
            
            const kpiCard = document.createElement('div');
            kpiCard.className = 'card bg-darker border-0 rounded-4 shadow-sm h-100';
            
            const cardBody = document.createElement('div');
            cardBody.className = 'card-body p-3';
            
            const kpiHeading = document.createElement('h6');
            kpiHeading.className = 'mb-2 d-flex align-items-center text-primary';
            kpiHeading.innerHTML = `<i class="fas fa-chart-line me-2"></i>${kpi.name}`;
            
            const descriptionPara = document.createElement('p');
            descriptionPara.className = 'mb-0 small text-muted';
            descriptionPara.textContent = kpi.description;
            
            cardBody.appendChild(kpiHeading);
            cardBody.appendChild(descriptionPara);
            kpiCard.appendChild(cardBody);
            kpiCol.appendChild(kpiCard);
            kpisList.appendChild(kpiCol);
        });
    }
}

/**
 * Generate complete strategy document
 */
function generateStrategyDocument() {
    const trendInput = document.getElementById('resultsTrendTitle').textContent;
    const industryInput = document.getElementById('resultIndustryBadge').textContent;
    
    alert('Generating complete strategy document for: ' + trendInput + ' in ' + industryInput + ' industry.');
    // TODO: Implement actual document generation
}

/**
 * Export strategy data to CSV/JSON
 */
function exportStrategyData() {
    const trendInput = document.getElementById('resultsTrendTitle').textContent;
    
    // Create a simple JSON object with the strategy data
    const strategyData = {
        trend: trendInput,
        industry: document.getElementById('resultIndustryBadge').textContent,
        summary: document.getElementById('analysisSummary').textContent,
        quickWins: Array.from(document.querySelectorAll('#quickWinsList .list-group-item:not(.text-muted)')).map(item => {
            return item.textContent.trim();
        }),
        mediumTerm: Array.from(document.querySelectorAll('#mediumTermList .list-group-item:not(.text-muted)')).map(item => {
            return item.textContent.trim();
        }),
        longTerm: Array.from(document.querySelectorAll('#longTermList .list-group-item:not(.text-muted)')).map(item => {
            return item.textContent.trim();
        }),
        opportunities: Array.from(document.querySelectorAll('#opportunitiesList .list-group-item:not(.text-muted)')).map(item => {
            return item.textContent.trim();
        }),
        threats: Array.from(document.querySelectorAll('#threatsList .list-group-item:not(.text-muted)')).map(item => {
            return item.textContent.trim();
        }),
        exportDate: new Date().toISOString()
    };
    
    // Convert to JSON string
    const jsonData = JSON.stringify(strategyData, null, 2);
    
    // Create a blob and download link
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Create temporary link and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = `strategy-${trendInput.toLowerCase().replace(/\s+/g, '-')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Reset analysis form to initial state
 */
function resetAnalysisForm() {
    document.getElementById('analysisResults').style.display = 'none';
    document.getElementById('consultantInputContainer').style.display = 'block';
    document.getElementById('trendInput').value = '';
}