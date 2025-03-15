/**
 * Strategy AI Consultant JavaScript
 * 
 * Provides client-side functionality for the AI-driven management consultant
 * that analyzes sustainability trends and generates strategic recommendations.
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
    
    if (consultantForm) {
        consultantForm.addEventListener('submit', handleAnalysisSubmit);
    }
    
    if (generateDocumentBtn) {
        generateDocumentBtn.addEventListener('click', handleDocumentGeneration);
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
    
    // Show loading indicator
    document.getElementById('analysisLoading').style.display = 'block';
    document.getElementById('analysisResults').style.display = 'none';
    
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
        
        // Show results container
        document.getElementById('analysisResults').style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('analysisLoading').style.display = 'none';
        
        // Show error message
        showNotification('Error analyzing trend: ' + error.message, 'error');
    });
}

/**
 * Display summary results from trend analysis
 */
function displaySummaryResults(analysis) {
    // Set trend title and industry badge
    document.getElementById('resultsTrendTitle').textContent = analysis.trend_name;
    document.getElementById('resultIndustryBadge').textContent = analysis.industry;
    
    // Set summary
    document.getElementById('analysisSummary').textContent = analysis.summary;
    
    // Populate recommendations
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        analysis.recommendations.forEach(recommendation => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent';
            li.innerHTML = `<i class="fas fa-check-circle text-success me-2"></i> ${recommendation}`;
            recommendationsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent text-muted';
        li.textContent = 'No recommendations available';
        recommendationsList.appendChild(li);
    }
    
    // Hide detailed sections for summary view
    document.getElementById('actionsList').closest('.col-md-6').style.display = 'none';
    document.getElementById('opportunitiesList').closest('.row').style.display = 'none';
    document.getElementById('frameworkAnalysisCard').style.display = 'none';
}

/**
 * Display detailed results from trend analysis
 */
function displayDetailedResults(analysis) {
    // Set trend title and industry badge
    document.getElementById('resultsTrendTitle').textContent = analysis.trend_name;
    document.getElementById('resultIndustryBadge').textContent = analysis.industry;
    
    // Set summary
    document.getElementById('analysisSummary').textContent = analysis.summary;
    
    // Show all detailed sections
    document.getElementById('actionsList').closest('.col-md-6').style.display = 'block';
    document.getElementById('opportunitiesList').closest('.row').style.display = 'flex';
    document.getElementById('frameworkAnalysisCard').style.display = 'block';
    
    // Populate recommendations
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        analysis.recommendations.forEach(recommendation => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent';
            li.innerHTML = `<i class="fas fa-check-circle text-success me-2"></i> ${recommendation}`;
            recommendationsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent text-muted';
        li.textContent = 'No recommendations available';
        recommendationsList.appendChild(li);
    }
    
    // Populate strategic actions
    const actionsList = document.getElementById('actionsList');
    actionsList.innerHTML = '';
    
    if (analysis.strategic_actions && analysis.strategic_actions.length > 0) {
        analysis.strategic_actions.forEach(action => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent';
            li.innerHTML = `<i class="fas fa-play-circle text-primary me-2"></i> ${action}`;
            actionsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent text-muted';
        li.textContent = 'No strategic actions available';
        actionsList.appendChild(li);
    }
    
    // Populate opportunities
    const opportunitiesList = document.getElementById('opportunitiesList');
    opportunitiesList.innerHTML = '';
    
    if (analysis.opportunities && analysis.opportunities.length > 0) {
        analysis.opportunities.forEach(opportunity => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent';
            li.innerHTML = `<i class="fas fa-plus-circle text-success me-2"></i> ${opportunity}`;
            opportunitiesList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent text-muted';
        li.textContent = 'No opportunities available';
        opportunitiesList.appendChild(li);
    }
    
    // Populate threats
    const threatsList = document.getElementById('threatsList');
    threatsList.innerHTML = '';
    
    if (analysis.threats && analysis.threats.length > 0) {
        analysis.threats.forEach(threat => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent';
            li.innerHTML = `<i class="fas fa-exclamation-circle text-danger me-2"></i> ${threat}`;
            threatsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent text-muted';
        li.textContent = 'No threats available';
        threatsList.appendChild(li);
    }
    
    // Populate framework analysis
    const frameworkAnalysisContent = document.getElementById('frameworkAnalysisContent');
    frameworkAnalysisContent.innerHTML = '';
    
    if (analysis.assessment && Object.keys(analysis.assessment).length > 0) {
        Object.keys(analysis.assessment).forEach(framework => {
            const frameworkDiv = document.createElement('div');
            frameworkDiv.className = 'mb-4';
            
            const frameworkTitle = document.createElement('h5');
            frameworkTitle.className = 'mb-3';
            frameworkTitle.textContent = `${framework} Analysis`;
            frameworkDiv.appendChild(frameworkTitle);
            
            const frameworkContent = analysis.assessment[framework];
            
            if (typeof frameworkContent === 'string') {
                const p = document.createElement('p');
                p.textContent = frameworkContent;
                frameworkDiv.appendChild(p);
            } else if (typeof frameworkContent === 'object') {
                const dl = document.createElement('dl');
                dl.className = 'row';
                
                Object.keys(frameworkContent).forEach(key => {
                    const dt = document.createElement('dt');
                    dt.className = 'col-sm-3';
                    dt.textContent = key;
                    dl.appendChild(dt);
                    
                    const dd = document.createElement('dd');
                    dd.className = 'col-sm-9';
                    dd.textContent = frameworkContent[key];
                    dl.appendChild(dd);
                });
                
                frameworkDiv.appendChild(dl);
            }
            
            frameworkAnalysisContent.appendChild(frameworkDiv);
        });
    } else {
        const p = document.createElement('p');
        p.className = 'text-muted';
        p.textContent = 'No framework analysis available';
        frameworkAnalysisContent.appendChild(p);
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