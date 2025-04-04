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