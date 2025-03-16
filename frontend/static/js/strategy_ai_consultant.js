/**
 * Strategy AI Consultant JavaScript
 * 
 * Provides client-side functionality for the AI-driven management consultant
 * that analyzes sustainability trends and generates strategic recommendations.
 * 
 * Enhanced for minimalist UI with improved interactions and animations.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AI Consultant component
    initAIConsultant();
});

/**
 * Initialize the AI Consultant component
 */
function initAIConsultant() {
    const consultantForm = document.getElementById('aiConsultantForm');
    const generateDocumentBtn = document.getElementById('generateDocumentBtn');
    const backToAnalysisBtn = document.getElementById('backToAnalysisBtn');
    const frameworkBadges = document.querySelectorAll('.framework-badge');
    
    // Main form submission handler
    if (consultantForm) {
        consultantForm.addEventListener('submit', handleAnalysisSubmit);
    }
    
    // Document generation button
    if (generateDocumentBtn) {
        generateDocumentBtn.addEventListener('click', handleDocumentGeneration);
    }
    
    // Back to analysis button
    if (backToAnalysisBtn) {
        backToAnalysisBtn.addEventListener('click', function() {
            document.getElementById('analysisResults').style.display = 'none';
            document.getElementById('consultantInputContainer').style.display = 'block';
        });
    }
    
    // Framework badges toggle
    if (frameworkBadges.length > 0) {
        frameworkBadges.forEach(badge => {
            badge.addEventListener('click', function() {
                const framework = this.getAttribute('data-framework');
                const checkbox = document.getElementById('framework' + framework.replace(/[^a-zA-Z0-9]/g, ''));
                
                // Toggle active class
                this.classList.toggle('active');
                
                // Update corresponding checkbox
                if (checkbox) {
                    checkbox.checked = this.classList.contains('active');
                }
                
                // Visual feedback
                if (this.classList.contains('active')) {
                    this.classList.remove('bg-primary-subtle');
                    this.classList.add('bg-primary');
                    this.classList.remove('text-primary');
                    this.classList.add('text-white');
                } else {
                    this.classList.add('bg-primary-subtle');
                    this.classList.remove('bg-primary');
                    this.classList.add('text-primary');
                    this.classList.remove('text-white');
                }
            });
        });
    }
}

/**
 * Handle form submission for trend analysis
 */
function handleAnalysisSubmit(event) {
    event.preventDefault();
    
    // Get form values
    const trendName = document.getElementById('trendInput').value;
    const industry = document.getElementById('industryInput').value;
    const timeframe = document.getElementById('timeframeInput').value;
    const outputFormat = document.getElementById('outputFormatInput').value;
    
    // Get selected frameworks
    const frameworks = [];
    const frameworkCheckboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    frameworkCheckboxes.forEach(checkbox => {
        frameworks.push(checkbox.value);
    });
    
    // Hide input container and show loading indicator
    document.getElementById('consultantInputContainer').style.display = 'none';
    document.getElementById('analysisLoading').style.display = 'block';
    document.getElementById('analysisResults').style.display = 'none';
    
    // Show a progress notification
    showNotification('Analyzing trend: ' + trendName, 'info');
    
    // Prepare request data
    const requestData = {
        trend_name: trendName,
        industry: industry,
        timeframe: timeframe,
        frameworks: frameworks
    };
    
    // Call API to analyze trend
    fetch('/api/strategy/analyze-trend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading indicator
        document.getElementById('analysisLoading').style.display = 'none';
        
        // Store analysis for document generation
        window.currentAnalysis = data;
        
        // Display results based on output format
        if (outputFormat === 'summary') {
            displaySummaryResults(data);
        } else if (outputFormat === 'detailed') {
            displayDetailedResults(data);
        } else if (outputFormat === 'document') {
            // Generate document immediately
            handleDocumentGeneration();
            return;
        }
        
        // Show results container with animation
        const resultsContainer = document.getElementById('analysisResults');
        resultsContainer.style.display = 'block';
        resultsContainer.classList.add('fade-in');
        
        // Show success notification
        showNotification('Analysis completed successfully!', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('analysisLoading').style.display = 'none';
        document.getElementById('consultantInputContainer').style.display = 'block';
        
        // Show error message
        showNotification('Error analyzing trend: ' + error.message, 'error');
    });
}

/**
 * Display summary results from trend analysis
 * Enhanced for minimalist UI with tabbed interface
 */
function displaySummaryResults(analysis) {
    // Hide the input container
    document.getElementById('consultantInputContainer').style.display = 'none';
    
    // Set trend title and industry badge
    document.getElementById('resultsTrendTitle').textContent = analysis.trend_name;
    document.getElementById('resultIndustryBadge').textContent = analysis.industry;
    
    // Set summary with animation
    const summaryElement = document.getElementById('analysisSummary');
    summaryElement.textContent = analysis.summary;
    summaryElement.classList.add('fade-in');
    
    // For summary view, only populate the recommendations tab
    populateRecommendations(analysis.recommendations);
    
    // Hide other tabs for summary view
    document.querySelectorAll('#analysisResultsTabs .nav-item').forEach(tab => {
        if (!tab.querySelector('button').id.includes('recommendations')) {
            tab.style.display = 'none';
        }
    });
    
    // Activate recommendations tab
    const recommendationsTab = new bootstrap.Tab(document.getElementById('recommendations-tab'));
    recommendationsTab.show();
    
    // Add animation classes
    document.querySelectorAll('#analysisResults .card').forEach(card => {
        card.classList.add('fade-in-up');
    });
}

/**
 * Display detailed results from trend analysis
 * Enhanced for minimalist UI with tabbed interface
 */
function displayDetailedResults(analysis) {
    // Hide the input container
    document.getElementById('consultantInputContainer').style.display = 'none';
    
    // Set trend title and industry badge
    document.getElementById('resultsTrendTitle').textContent = analysis.trend_name;
    document.getElementById('resultIndustryBadge').textContent = analysis.industry;
    
    // Set summary with animation
    const summaryElement = document.getElementById('analysisSummary');
    summaryElement.textContent = analysis.summary;
    summaryElement.classList.add('fade-in');
    
    // Show all tabs for detailed view
    document.querySelectorAll('#analysisResultsTabs .nav-item').forEach(tab => {
        tab.style.display = 'block';
    });
    
    // Populate all tabs
    populateRecommendations(analysis.recommendations);
    populateActions(analysis.strategic_actions);
    populateOpportunities(analysis.opportunities);
    populateThreats(analysis.threats);
    populateFrameworks(analysis.assessment);
    
    // Activate recommendations tab
    const recommendationsTab = new bootstrap.Tab(document.getElementById('recommendations-tab'));
    recommendationsTab.show();
    
    // Add animation classes
    document.querySelectorAll('#analysisResults .card').forEach((card, index) => {
        card.classList.add('fade-in-up');
        card.style.animationDelay = `${index * 0.1}s`;
    });
}

/**
 * Populate recommendations tab
 */
function populateRecommendations(recommendations) {
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    
    if (recommendations && recommendations.length > 0) {
        recommendations.forEach((recommendation, index) => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent border-0 py-3';
            li.innerHTML = `
                <div class="d-flex">
                    <div class="me-3 text-success">
                        <i class="fas fa-check-circle fa-lg"></i>
                    </div>
                    <div>
                        <strong class="d-block mb-1">Recommendation ${index + 1}</strong>
                        <span>${recommendation}</span>
                    </div>
                </div>
            `;
            recommendationsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent border-0 py-3 text-center';
        li.innerHTML = '<i class="fas fa-info-circle me-2"></i> No recommendations available';
        recommendationsList.appendChild(li);
    }
}

/**
 * Populate actions tab
 */
function populateActions(actions) {
    const actionsList = document.getElementById('actionsList');
    actionsList.innerHTML = '';
    
    if (actions && actions.length > 0) {
        actions.forEach((action, index) => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent border-0 py-3';
            li.innerHTML = `
                <div class="d-flex">
                    <div class="me-3 text-primary">
                        <i class="fas fa-play-circle fa-lg"></i>
                    </div>
                    <div>
                        <strong class="d-block mb-1">Action ${index + 1}</strong>
                        <span>${action}</span>
                    </div>
                </div>
            `;
            actionsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent border-0 py-3 text-center';
        li.innerHTML = '<i class="fas fa-info-circle me-2"></i> No strategic actions available';
        actionsList.appendChild(li);
    }
}

/**
 * Populate opportunities tab
 */
function populateOpportunities(opportunities) {
    const opportunitiesList = document.getElementById('opportunitiesList');
    opportunitiesList.innerHTML = '';
    
    if (opportunities && opportunities.length > 0) {
        opportunities.forEach((opportunity, index) => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent border-0 py-3';
            li.innerHTML = `
                <div class="d-flex">
                    <div class="me-3 text-success">
                        <i class="fas fa-arrow-up fa-lg"></i>
                    </div>
                    <div>
                        <strong class="d-block mb-1">Opportunity ${index + 1}</strong>
                        <span>${opportunity}</span>
                    </div>
                </div>
            `;
            opportunitiesList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent border-0 py-3 text-center';
        li.innerHTML = '<i class="fas fa-info-circle me-2"></i> No opportunities available';
        opportunitiesList.appendChild(li);
    }
}

/**
 * Populate threats tab
 */
function populateThreats(threats) {
    const threatsList = document.getElementById('threatsList');
    threatsList.innerHTML = '';
    
    if (threats && threats.length > 0) {
        threats.forEach((threat, index) => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent border-0 py-3';
            li.innerHTML = `
                <div class="d-flex">
                    <div class="me-3 text-danger">
                        <i class="fas fa-arrow-down fa-lg"></i>
                    </div>
                    <div>
                        <strong class="d-block mb-1">Threat ${index + 1}</strong>
                        <span>${threat}</span>
                    </div>
                </div>
            `;
            threatsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent border-0 py-3 text-center';
        li.innerHTML = '<i class="fas fa-info-circle me-2"></i> No threats available';
        threatsList.appendChild(li);
    }
}

/**
 * Populate frameworks tab
 */
function populateFrameworks(assessment) {
    const frameworkAnalysisContent = document.getElementById('frameworkAnalysisContent');
    frameworkAnalysisContent.innerHTML = '';
    
    if (assessment && Object.keys(assessment).length > 0) {
        Object.keys(assessment).forEach(framework => {
            const frameworkDiv = document.createElement('div');
            frameworkDiv.className = 'mb-4 p-3 border-bottom border-secondary';
            
            const frameworkTitle = document.createElement('h5');
            frameworkTitle.className = 'mb-3 text-primary';
            frameworkTitle.innerHTML = `<i class="fas fa-chart-pie me-2"></i>${framework} Analysis`;
            frameworkDiv.appendChild(frameworkTitle);
            
            const frameworkContent = assessment[framework];
            
            if (typeof frameworkContent === 'string') {
                const p = document.createElement('p');
                p.className = 'lead';
                p.textContent = frameworkContent;
                frameworkDiv.appendChild(p);
            } else if (typeof frameworkContent === 'object') {
                // Create accordion for each component
                const accordionId = `accordion-${framework.replace(/\s+/g, '-').toLowerCase()}`;
                const accordion = document.createElement('div');
                accordion.className = 'accordion';
                accordion.id = accordionId;
                
                Object.keys(frameworkContent).forEach((key, index) => {
                    const itemId = `${accordionId}-item-${index}`;
                    const component = document.createElement('div');
                    component.className = 'accordion-item bg-transparent border-0 mb-2';
                    
                    component.innerHTML = `
                        <h6 class="accordion-header" id="heading-${itemId}">
                            <button class="accordion-button bg-darker text-white collapsed rounded-3" type="button" 
                                    data-bs-toggle="collapse" data-bs-target="#collapse-${itemId}" 
                                    aria-expanded="false" aria-controls="collapse-${itemId}">
                                ${key}
                            </button>
                        </h6>
                        <div id="collapse-${itemId}" class="accordion-collapse collapse" 
                             aria-labelledby="heading-${itemId}" data-bs-parent="#${accordionId}">
                            <div class="accordion-body pt-2 pb-3 px-4">
                                ${frameworkContent[key]}
                            </div>
                        </div>
                    `;
                    
                    accordion.appendChild(component);
                });
                
                frameworkDiv.appendChild(accordion);
            }
            
            frameworkAnalysisContent.appendChild(frameworkDiv);
        });
    } else {
        const alert = document.createElement('div');
        alert.className = 'alert alert-secondary bg-dark text-center border-0';
        alert.innerHTML = '<i class="fas fa-info-circle me-2"></i> No framework analysis available';
        frameworkAnalysisContent.appendChild(alert);
    }
}

/**
 * Handle document generation request
 */
function handleDocumentGeneration() {
    // Check if we have analysis data
    if (!window.currentAnalysis) {
        showNotification('No analysis data available. Please generate an analysis first.', 'warning');
        return;
    }
    
    // Show loading indicator
    showNotification('Generating strategy document...', 'info');
    
    // Prepare request data
    const requestData = {
        analysis: window.currentAnalysis,
        format: 'html'
    };
    
    // Call API to generate document
    fetch('/api/strategy/generate-document', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.document) {
            // Create a modal to display the document
            const modalId = 'strategyDocumentModal';
            
            // Check if modal already exists
            let modal = document.getElementById(modalId);
            
            if (!modal) {
                // Create new modal
                modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.id = modalId;
                modal.tabIndex = '-1';
                modal.setAttribute('aria-labelledby', `${modalId}Label`);
                modal.setAttribute('aria-hidden', 'true');
                
                modal.innerHTML = `
                    <div class="modal-dialog modal-xl modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="${modalId}Label">Strategy Document: ${window.currentAnalysis.trend_name}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div id="${modalId}Content"></div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="button" class="btn btn-primary" id="${modalId}PrintBtn">
                                    <i class="fas fa-print me-2"></i> Print Document
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                
                // Add print functionality
                document.getElementById(`${modalId}PrintBtn`).addEventListener('click', function() {
                    const printWindow = window.open('', '_blank');
                    printWindow.document.write(`
                        <html>
                            <head>
                                <title>Strategy Document: ${window.currentAnalysis.trend_name}</title>
                                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                                <style>
                                    body { padding: 20px; }
                                    @media print {
                                        .no-print { display: none; }
                                    }
                                </style>
                            </head>
                            <body>
                                <div class="container">
                                    <div class="no-print mb-4">
                                        <button class="btn btn-primary" onclick="window.print()">Print</button>
                                        <button class="btn btn-secondary ms-2" onclick="window.close()">Close</button>
                                    </div>
                                    ${data.document}
                                </div>
                            </body>
                        </html>
                    `);
                    printWindow.document.close();
                });
            }
            
            // Update modal content
            document.getElementById(`${modalId}Content`).innerHTML = data.document;
            
            // Show the modal
            new bootstrap.Modal(modal).show();
        } else {
            showNotification('Error: Document generation failed', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error generating document: ' + error.message, 'error');
    });
}

/**
 * Show a notification to the user
 */
function showNotification(message, type = 'info') {
    // Check if we have toast container
    let toastContainer = document.getElementById('toastContainer');
    
    if (!toastContainer) {
        // Create toast container
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.id = 'toastContainer';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast ${type === 'error' ? 'bg-danger text-white' : type === 'warning' ? 'bg-warning' : type === 'success' ? 'bg-success text-white' : 'bg-info text-white'}`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">Strategy AI Consultant</strong>
            <small>Just now</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show the toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}