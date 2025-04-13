/**
 * Strategy Hub JavaScript
 * 
 * Provides client-side functionality for the Strategy Hub, including interactions
 * with the AI Strategy Consultant and monetization strategies visualization.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Strategy Hub components
    initStrategyHub();
    initAIConsultant();
    initEthicalAI();
    initMonetizationStrategies();
    initCharts();
});

/**
 * Initialize the Strategy Hub components
 */
function initStrategyHub() {
    // Handle category selection
    const categoryLinks = document.querySelectorAll('.strategy-category');
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all category links
            categoryLinks.forEach(item => item.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Get the category ID
            const categoryId = this.getAttribute('data-category');
            
            // Show/hide strategy cards based on category
            const strategyCards = document.querySelectorAll('.strategy-card');
            strategyCards.forEach(card => {
                if (categoryId === 'all' || card.getAttribute('data-category') === categoryId) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

/**
 * Initialize the AI Consultant functionality
 */
function initAIConsultant() {
    const strategizeForm = document.getElementById('aiConsultantForm');
    const generateButton = document.getElementById('generateInsightsBtn');
    const resultContainer = document.getElementById('aiConsultantResults');
    const loadingIndicator = document.getElementById('aiConsultantLoading');
    
    if (!strategizeForm || !generateButton) return;
    
    strategizeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }
        
        // Get form values
        const companyName = document.getElementById('companyName').value || 'Your Company';
        const industry = document.getElementById('industry').value || 'Technology';
        const focusAreas = Array.from(document.querySelectorAll('input[name="focusAreas"]:checked'))
            .map(checkbox => checkbox.value)
            .join(',');
        const challengeDescription = document.getElementById('challengeDescription').value || '';
        
        // Prepare request data
        const requestData = {
            company_name: companyName,
            industry: industry,
            focus_areas: focusAreas,
            challenge_description: challengeDescription
        };
        
        // Call the AI Strategy Consultant API
        fetch('/api/strategy/ai-consultant/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                companyName: requestData.company_name,
                industry: requestData.industry,
                focusAreas: requestData.focus_areas,
                challengeDescription: requestData.challenge_description
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            // Display results
            if (resultContainer) {
                if (data.success) {
                    // Format and display the strategy
                    resultContainer.innerHTML = formatStrategyResults(data.strategy);
                    resultContainer.style.display = 'block';
                } else {
                    // Display error message
                    resultContainer.innerHTML = `
                        <div class="alert alert-danger">
                            <h5>Error Generating Strategy</h5>
                            <p>${data.message || 'An unknown error occurred'}</p>
                        </div>
                    `;
                    resultContainer.style.display = 'block';
                }
            }
        })
        .catch(error => {
            console.error('Error calling AI Strategy Consultant:', error);
            
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            // Display error message
            if (resultContainer) {
                resultContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <h5>Error Generating Strategy</h5>
                        <p>Could not connect to the AI Strategy Consultant. Please try again later.</p>
                    </div>
                `;
                resultContainer.style.display = 'block';
            }
        });
    });
}

/**
 * Format strategy results for display
 */
function formatStrategyResults(strategy) {
    if (!strategy) return '<div class="alert alert-warning">No strategy data received</div>';
    
    let html = `
        <div class="strategy-result">
            <h4 class="mb-3 mt-4">Strategic Recommendations for ${strategy.company || 'Your Company'}</h4>
            <div class="strategy-section">
                <h5><i class="fas fa-lightbulb text-warning me-2"></i>Strategy Overview</h5>
                <p>${strategy.overview || 'No overview provided'}</p>
            </div>
    `;
    
    // Add objectives if available
    if (strategy.objectives && strategy.objectives.length) {
        html += `
            <div class="strategy-section">
                <h5><i class="fas fa-bullseye text-primary me-2"></i>Strategic Objectives</h5>
                <div class="row">
        `;
        
        strategy.objectives.forEach(objective => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-body">
                            <h6>${objective.title || 'Objective'}</h6>
                            <p>${objective.description || 'No description provided'}</p>
                            <div class="d-flex flex-column gap-1 mt-2">
                                ${objective.kpis && objective.kpis.map(kpi => 
                                    `<span class="badge bg-light text-dark"><i class="fas fa-chart-line me-1"></i>${kpi}</span>`
                                ).join('') || ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    // Add recommendations if available
    if (strategy.recommendations && strategy.recommendations.length) {
        html += `
            <div class="strategy-section">
                <h5><i class="fas fa-check-circle text-success me-2"></i>Actionable Recommendations</h5>
                <ul class="list-group">
        `;
        
        strategy.recommendations.forEach(recommendation => {
            html += `
                <li class="list-group-item">
                    <div class="d-flex align-items-center">
                        <div class="text-primary me-3">
                            <i class="fas fa-arrow-right"></i>
                        </div>
                        <div>
                            ${recommendation.title ? `<strong>${recommendation.title}</strong>: ` : ''}
                            ${recommendation.description || recommendation}
                        </div>
                    </div>
                </li>
            `;
        });
        
        html += `
                </ul>
            </div>
        `;
    }
    
    // Add implementation timeline if available
    if (strategy.timeline) {
        html += `
            <div class="strategy-section">
                <h5><i class="fas fa-calendar-alt text-info me-2"></i>Implementation Timeline</h5>
                <p>${strategy.timeline}</p>
            </div>
        `;
    }
    
    // Add export and action buttons
    html += `
        <div class="mt-4 d-flex justify-content-end">
            <button class="btn btn-outline-secondary me-2">
                <i class="fas fa-file-export me-2"></i> Export Strategy
            </button>
            <button class="btn btn-primary">
                <i class="fas fa-play me-2"></i> Implement Strategy
            </button>
        </div>
    `;
    
    html += `</div>`;
    return html;
}

/**
 * Initialize the Ethical AI functionality
 */
function initEthicalAI() {
    const ethicalAiForm = document.getElementById('ethicalAiForm');
    const resultContainer = document.getElementById('ethicalAiResults');
    const loadingIndicator = document.getElementById('ethicalAiLoading');
    
    if (!ethicalAiForm) return;
    
    ethicalAiForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }
        
        // Hide any previous results
        if (resultContainer) {
            resultContainer.style.display = 'none';
        }
        
        // Get form values
        const strategyDocument = document.getElementById('strategyDocument').value;
        const assessmentTypes = Array.from(document.querySelectorAll('input[name="assessmentType"]:checked'))
            .map(checkbox => checkbox.value);
        const context = document.getElementById('ethicalContext').value || '';
        
        // Validate inputs
        if (!strategyDocument) {
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            if (resultContainer) {
                resultContainer.innerHTML = `
                    <div class="alert alert-warning">
                        <h5>Missing Information</h5>
                        <p>Please select a strategy document to assess.</p>
                    </div>
                `;
                resultContainer.style.display = 'block';
            }
            return;
        }
        
        if (assessmentTypes.length === 0) {
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            if (resultContainer) {
                resultContainer.innerHTML = `
                    <div class="alert alert-warning">
                        <h5>Missing Information</h5>
                        <p>Please select at least one assessment type.</p>
                    </div>
                `;
                resultContainer.style.display = 'block';
            }
            return;
        }
        
        // Prepare request data
        const requestData = {
            document_id: strategyDocument,
            assessment_types: assessmentTypes,
            context: context
        };
        
        // Call the Ethical AI Assessment API
        fetch('/api/ethical-ai/analyze-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            // Display results
            if (resultContainer) {
                if (data.status === 'success') {
                    // Format and display the assessment results
                    resultContainer.innerHTML = formatEthicalAiResults(data);
                    resultContainer.style.display = 'block';
                } else {
                    // Display error message
                    resultContainer.innerHTML = `
                        <div class="alert alert-danger">
                            <h5>Error Running Assessment</h5>
                            <p>${data.message || 'An unknown error occurred'}</p>
                        </div>
                    `;
                    resultContainer.style.display = 'block';
                }
            }
        })
        .catch(error => {
            console.error('Error calling Ethical AI Assessment API:', error);
            
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            // Display error message
            if (resultContainer) {
                resultContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <h5>Error Running Assessment</h5>
                        <p>Could not connect to the Ethical AI service. Please try again later.</p>
                    </div>
                `;
                resultContainer.style.display = 'block';
            }
        });
    });
}

/**
 * Format ethical AI assessment results for display
 */
function formatEthicalAiResults(data) {
    if (!data || !data.results) {
        return '<div class="alert alert-warning">No assessment data received</div>';
    }
    
    const results = data.results;
    
    // Initialize HTML with header
    let html = `
        <div class="ethical-assessment-result">
            <h4 class="mb-3 mt-4">Ethical AI Assessment Results</h4>
    `;
    
    // Add overall score if available
    if (results.overall_score !== undefined) {
        const scoreColor = getScoreColor(results.overall_score);
        html += `
            <div class="d-flex align-items-center mb-4">
                <div class="me-3">
                    <div class="ethical-score-circle ${scoreColor}" style="width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">
                        ${Math.round(results.overall_score)}%
                    </div>
                </div>
                <div>
                    <h5 class="mb-1">Overall Ethical Assessment</h5>
                    <p class="mb-0 text-muted">${getScoreDescription(results.overall_score)}</p>
                </div>
            </div>
        `;
    }
    
    // Add bias detection results if available
    if (results.bias_detection) {
        html += `
            <div class="card mb-4">
                <div class="card-header d-flex align-items-center">
                    <i class="fas fa-balance-scale text-primary me-2"></i>
                    <h5 class="mb-0">Bias Detection</h5>
                </div>
                <div class="card-body">
                    <p>${results.bias_detection.summary || 'No bias detection summary available.'}</p>
                    
                    ${results.bias_detection.findings ? `
                        <h6 class="mt-3">Key Findings:</h6>
                        <ul class="list-group">
                            ${Array.isArray(results.bias_detection.findings) ? 
                                results.bias_detection.findings.map(finding => `
                                    <li class="list-group-item d-flex">
                                        <div class="me-3">
                                            <i class="fas ${finding.severity === 'high' ? 'fa-exclamation-circle text-danger' : 
                                                           finding.severity === 'medium' ? 'fa-exclamation-triangle text-warning' : 
                                                           'fa-info-circle text-info'}"></i>
                                        </div>
                                        <div>
                                            ${finding.description}
                                        </div>
                                    </li>
                                `).join('') : 
                                `<li class="list-group-item">No specific findings available.</li>`
                            }
                        </ul>
                    ` : ''}
                    
                    ${results.bias_detection.recommendations ? `
                        <h6 class="mt-3">Recommendations:</h6>
                        <div class="ps-3 border-start border-primary">
                            <p>${results.bias_detection.recommendations}</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // Add transparency assessment if available
    if (results.transparency) {
        html += `
            <div class="card mb-4">
                <div class="card-header d-flex align-items-center">
                    <i class="fas fa-eye text-primary me-2"></i>
                    <h5 class="mb-0">Transparency Assessment</h5>
                </div>
                <div class="card-body">
                    <p>${results.transparency.summary || 'No transparency assessment summary available.'}</p>
                    
                    ${results.transparency.score !== undefined ? `
                        <div class="progress mb-3" style="height: 8px;">
                            <div class="progress-bar ${getScoreColor(results.transparency.score)}" 
                                role="progressbar" style="width: ${results.transparency.score}%;" 
                                aria-valuenow="${results.transparency.score}" aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                        <p class="text-muted small mb-3">Transparency Score: ${results.transparency.score}%</p>
                    ` : ''}
                    
                    ${results.transparency.recommendations ? `
                        <h6 class="mt-3">Recommendations:</h6>
                        <div class="ps-3 border-start border-primary">
                            <p>${results.transparency.recommendations}</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // Add compliance assessment if available
    if (results.compliance) {
        html += `
            <div class="card mb-4">
                <div class="card-header d-flex align-items-center">
                    <i class="fas fa-check-circle text-primary me-2"></i>
                    <h5 class="mb-0">Regulatory Compliance</h5>
                </div>
                <div class="card-body">
                    <p>${results.compliance.summary || 'No compliance assessment summary available.'}</p>
                    
                    ${results.compliance.frameworks && results.compliance.frameworks.length > 0 ? `
                        <h6 class="mt-3">Framework Alignment:</h6>
                        <div class="row">
                            ${results.compliance.frameworks.map(framework => `
                                <div class="col-md-6 mb-3">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <span>${framework.name}</span>
                                        <span class="badge ${getScoreColor(framework.score)}">${Math.round(framework.score)}%</span>
                                    </div>
                                    <div class="progress" style="height: 5px;">
                                        <div class="progress-bar ${getScoreColor(framework.score)}" 
                                            role="progressbar" style="width: ${framework.score}%;" 
                                            aria-valuenow="${framework.score}" aria-valuemin="0" aria-valuemax="100">
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${results.compliance.issues ? `
                        <h6 class="mt-3">Compliance Issues:</h6>
                        <ul class="list-group">
                            ${Array.isArray(results.compliance.issues) ? 
                                results.compliance.issues.map(issue => `
                                    <li class="list-group-item d-flex">
                                        <div class="me-3">
                                            <i class="fas ${issue.severity === 'high' ? 'fa-exclamation-circle text-danger' : 
                                                           issue.severity === 'medium' ? 'fa-exclamation-triangle text-warning' : 
                                                           'fa-info-circle text-info'}"></i>
                                        </div>
                                        <div>
                                            <strong>${issue.title || 'Issue'}</strong>
                                            <p class="mb-0">${issue.description}</p>
                                        </div>
                                    </li>
                                `).join('') : 
                                `<li class="list-group-item">No specific compliance issues found.</li>`
                            }
                        </ul>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // Add additional resources or actions
    html += `
        <div class="mt-4 d-flex justify-content-end">
            <button class="btn btn-outline-secondary me-2">
                <i class="fas fa-file-export me-2"></i> Export Report
            </button>
            <button class="btn btn-primary">
                <i class="fas fa-tasks me-2"></i> Address Issues
            </button>
        </div>
    `;
    
    html += `</div>`;
    return html;
}

/**
 * Get color class based on score
 */
function getScoreColor(score) {
    if (score >= 80) return 'bg-success';
    if (score >= 60) return 'bg-primary';
    if (score >= 40) return 'bg-warning';
    return 'bg-danger';
}

/**
 * Get description based on score
 */
function getScoreDescription(score) {
    if (score >= 90) return 'Excellent - Meets highest ethical standards';
    if (score >= 80) return 'Very Good - Strong ethical alignment';
    if (score >= 70) return 'Good - Solid ethical foundation with minor improvements needed';
    if (score >= 60) return 'Satisfactory - Meets basic ethical requirements with areas for improvement';
    if (score >= 40) return 'Needs Improvement - Several ethical concerns identified';
    if (score >= 20) return 'Poor - Significant ethical issues requiring immediate attention';
    return 'Critical - Major ethical concerns requiring complete reassessment';
}

/**
 * Initialize monetization strategies visualization
 */
function initMonetizationStrategies() {
    const monetizationSection = document.getElementById('monetizationStrategies');
    if (!monetizationSection) return;
    
    // Add click handlers for strategy cards
    const strategyCards = document.querySelectorAll('.monetization-strategy-card');
    strategyCards.forEach(card => {
        card.addEventListener('click', function() {
            const strategyId = this.getAttribute('data-strategy-id');
            if (!strategyId) return;
            
            // Call API to get strategy details
            fetch(`/api/monetization/analyze?strategy_id=${strategyId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showStrategyDetails(data);
                    } else {
                        console.error('Error getting strategy details:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Error calling monetization API:', error);
                });
        });
    });
}

/**
 * Show strategy details in a modal
 */
function showStrategyDetails(data) {
    // Check if modal exists, create it if not
    let modal = document.getElementById('strategyDetailsModal');
    if (!modal) {
        const modalHtml = `
            <div class="modal fade" id="strategyDetailsModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Strategy Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body" id="strategyDetailsContent">
                            <!-- Content will be inserted here -->
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary">Apply Strategy</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        modal = document.getElementById('strategyDetailsModal');
    }
    
    // Populate modal content
    const contentElement = document.getElementById('strategyDetailsContent');
    if (contentElement) {
        contentElement.innerHTML = `
            <div class="strategy-detail">
                <h4 class="mb-3">${data.strategy_name || 'Strategy Details'}</h4>
                <div class="strategy-potential mb-4">
                    <h5>Potential Score</h5>
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: ${data.potential_score}%;" 
                            aria-valuenow="${data.potential_score}" aria-valuemin="0" aria-valuemax="100">
                            ${data.potential_score}%
                        </div>
                    </div>
                </div>
                <div class="strategy-recommendation mb-4">
                    <h5>Recommendation</h5>
                    <p>${data.recommendation || 'No recommendation available'}</p>
                </div>
            </div>
        `;
    }
    
    // Show the modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

/**
 * Initialize chart visualizations
 */
function initCharts() {
    // Department Chart
    const departmentCtx = document.getElementById('departmentChart');
    if (departmentCtx) {
        const departmentChart = new Chart(departmentCtx, {
            type: 'bar',
            data: {
                labels: ['Operations', 'Supply Chain', 'Product Dev', 'Marketing', 'HR', 'Finance'],
                datasets: [{
                    label: 'Strategy Adoption Rate',
                    data: [85, 72, 68, 45, 62, 53],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(249, 115, 22, 0.8)',
                        'rgba(236, 72, 153, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(245, 158, 11, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                maintainAspectRatio: false
            }
        });
    }
    
    // Timeline Chart
    const timelineCtx = document.getElementById('timelineChart');
    if (timelineCtx) {
        const timelineChart = new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Implementation Progress',
                    data: [10, 15, 25, 30, 35, 45, 55, 60, 65, 70, 75, 80],
                    fill: true,
                    backgroundColor: 'rgba(59, 130, 246, 0.3)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(59, 130, 246, 1)'
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                maintainAspectRatio: false
            }
        });
    }
}