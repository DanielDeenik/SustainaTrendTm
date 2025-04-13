/**
 * TrendSense™ VC Dashboard JavaScript
 * Handles interactive features of the VC dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initFundSelector();
    initReportUpload();
    initStrategyGenerator();
    initThemeToggle();
    initDataTable();
});

/**
 * Initialize the fund selector dropdown
 */
function initFundSelector() {
    const fundSelector = document.getElementById('fund-selector');
    if (!fundSelector) return;

    fundSelector.addEventListener('change', async function() {
        const fundId = this.value;
        try {
            // Show loading state
            showLoadingState();
            
            // In a real application, this would fetch data for the selected fund
            // For demo purposes, we'll simulate a delay
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Update the dashboard with the selected fund's data
            updateDashboardData(fundId);
            
            // Hide loading state
            hideLoadingState();
        } catch (error) {
            console.error('Error changing fund:', error);
            showError('Failed to load fund data. Please try again.');
        }
    });
}

/**
 * Initialize the report upload functionality
 */
function initReportUpload() {
    const uploadButton = document.querySelector('button:contains("Upload PDF Report")');
    if (!uploadButton) return;

    // Create a hidden file input
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.pdf';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);

    // Handle button click
    uploadButton.addEventListener('click', function() {
        fileInput.click();
    });

    // Handle file selection
    fileInput.addEventListener('change', async function() {
        if (this.files.length === 0) return;
        
        const file = this.files[0];
        if (!file.name.endsWith('.pdf')) {
            showError('Please select a PDF file.');
            return;
        }

        try {
            // Show loading state
            showLoadingState();
            
            // Create form data
            const formData = new FormData();
            formData.append('file', file);
            
            // Upload the file
            const response = await fetch('/api/vc-dashboard/upload-report', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to upload report');
            }
            
            // Show success message
            showSuccess('Report uploaded successfully');
            
            // Update dashboard with new data if needed
            if (result.analysis) {
                updateMetricsFromReport(result.analysis);
            }
            
            // Reset file input
            this.value = '';
            
            // Hide loading state
            hideLoadingState();
        } catch (error) {
            console.error('Error uploading report:', error);
            showError(error.message || 'Failed to upload report. Please try again.');
            hideLoadingState();
        }
    });
}

/**
 * Initialize the strategy generator
 */
function initStrategyGenerator() {
    const strategyButton = document.querySelector('button:contains("Generate GPT Strategy")');
    if (!strategyButton) return;

    strategyButton.addEventListener('click', async function() {
        try {
            // Show loading state
            showLoadingState();
            
            // Generate strategy
            const response = await fetch('/api/vc-dashboard/generate-strategy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to generate strategy');
            }
            
            // Update the GPT score and metrics
            if (result.strategy && result.strategy.metrics) {
                updateGPTMetrics(result.strategy.metrics);
                
                // Show strategy recommendations
                showStrategyRecommendations(result.strategy);
            }
            
            // Hide loading state
            hideLoadingState();
        } catch (error) {
            console.error('Error generating strategy:', error);
            showError(error.message || 'Failed to generate strategy. Please try again.');
            hideLoadingState();
        }
    });
}

/**
 * Initialize the theme toggle
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;

    // Check for saved theme preference
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }

    // Toggle theme on button click
    themeToggle.addEventListener('click', function() {
        document.documentElement.classList.toggle('dark');
        const isDark = document.documentElement.classList.contains('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
}

/**
 * Initialize the data table with sorting and filtering
 */
function initDataTable() {
    const table = document.querySelector('table');
    if (!table) return;

    // Add sorting functionality to table headers
    const headers = table.querySelectorAll('th');
    headers.forEach(header => {
        header.addEventListener('click', function() {
            const column = this.dataset.column;
            if (!column) return;
            
            // Toggle sort direction
            const currentDirection = this.dataset.direction === 'asc' ? 'desc' : 'asc';
            
            // Reset all headers
            headers.forEach(h => {
                h.dataset.direction = '';
                h.classList.remove('sort-asc', 'sort-desc');
            });
            
            // Set current header
            this.dataset.direction = currentDirection;
            this.classList.add(`sort-${currentDirection}`);
            
            // Sort the table
            sortTable(table, column, currentDirection);
        });
    });
}

/**
 * Sort the table by the specified column and direction
 */
function sortTable(table, column, direction) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.querySelector(`td[data-column="${column}"]`).textContent.trim();
        const bValue = b.querySelector(`td[data-column="${column}"]`).textContent.trim();
        
        // Handle numeric values
        if (!isNaN(aValue) && !isNaN(bValue)) {
            return direction === 'asc' ? aValue - bValue : bValue - aValue;
        }
        
        // Handle string values
        return direction === 'asc' 
            ? aValue.localeCompare(bValue) 
            : bValue.localeCompare(aValue);
    });
    
    // Reorder rows
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Update dashboard data based on selected fund
 */
function updateDashboardData(fundId) {
    // In a real application, this would update the dashboard with data from the selected fund
    console.log(`Updating dashboard for fund ID: ${fundId}`);
    
    // For demo purposes, we'll just update some metrics
    const totalCompaniesElement = document.querySelector('.text-2xl.font-bold:contains("Total Portfolio")');
    if (totalCompaniesElement) {
        totalCompaniesElement.textContent = Math.floor(Math.random() * 20) + 10;
    }
}

/**
 * Update metrics from uploaded report
 */
function updateMetricsFromReport(analysis) {
    // Update ESG score
    const esgScoreElement = document.querySelector('.text-2xl.font-bold:contains("Avg ESG Score")');
    if (esgScoreElement && analysis.esg_score) {
        esgScoreElement.textContent = analysis.esg_score;
        
        // Update progress bar
        const progressBar = document.querySelector('.bg-blue-600.h-2.rounded-full');
        if (progressBar) {
            progressBar.style.width = `${analysis.esg_score}%`;
        }
    }
    
    // Update carbon intensity
    const carbonElement = document.querySelector('.text-2xl.font-bold:contains("Carbon Intensity")');
    if (carbonElement && analysis.carbon_intensity) {
        carbonElement.textContent = `${analysis.carbon_intensity} tCO2e`;
    }
}

/**
 * Update GPT metrics
 */
function updateGPTMetrics(metrics) {
    // Update overall score
    const scoreElement = document.querySelector('.text-2xl.font-bold:contains("/100")');
    if (scoreElement && metrics.overall_score) {
        scoreElement.textContent = `${metrics.overall_score}/100`;
        
        // Update circular progress
        const circle = document.querySelector('.text-primary-600.dark\\:text-primary-400');
        if (circle) {
            circle.setAttribute('stroke-dasharray', `${metrics.overall_score * 3.64}`);
        }
    }
    
    // Update individual metrics
    if (metrics.market_fit) {
        const marketFitBar = document.querySelector('.bg-blue-600.h-2.rounded-full:first-of-type');
        if (marketFitBar) {
            marketFitBar.style.width = `${metrics.market_fit}%`;
        }
        
        const marketFitValue = document.querySelector('.font-medium:contains("%"):first-of-type');
        if (marketFitValue) {
            marketFitValue.textContent = `${metrics.market_fit}%`;
        }
    }
    
    if (metrics.sustainability_impact) {
        const impactBar = document.querySelector('.bg-green-600.h-2.rounded-full');
        if (impactBar) {
            impactBar.style.width = `${metrics.sustainability_impact}%`;
        }
        
        const impactValue = document.querySelector('.font-medium:contains("%"):nth-of-type(2)');
        if (impactValue) {
            impactValue.textContent = `${metrics.sustainability_impact}%`;
        }
    }
    
    if (metrics.financial_potential) {
        const potentialBar = document.querySelector('.bg-purple-600.h-2.rounded-full');
        if (potentialBar) {
            potentialBar.style.width = `${metrics.financial_potential}%`;
        }
        
        const potentialValue = document.querySelector('.font-medium:contains("%"):last-of-type');
        if (potentialValue) {
            potentialValue.textContent = `${metrics.financial_potential}%`;
        }
    }
}

/**
 * Show strategy recommendations
 */
function showStrategyRecommendations(strategy) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('strategy-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'strategy-modal';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50';
        modal.innerHTML = `
            <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white dark:bg-gray-800">
                <div class="flex justify-between items-center pb-3">
                    <p class="text-2xl font-bold text-gray-900 dark:text-white">Investment Strategy</p>
                    <button id="close-modal" class="text-gray-400 hover:text-gray-500">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="mt-2 text-gray-700 dark:text-gray-300">
                    <p class="text-lg mb-4">${strategy.summary}</p>
                    <h3 class="font-bold mb-2">Recommendations:</h3>
                    <ul class="list-disc pl-5 mb-4">
                        ${strategy.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
                <div class="flex justify-end mt-4">
                    <button id="dismiss-modal" class="px-4 py-2 bg-primary-600 text-white text-base font-medium rounded-md shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500">
                        Close
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Add event listeners to close buttons
        document.getElementById('close-modal').addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        document.getElementById('dismiss-modal').addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
    
    // Show the modal
    modal.style.display = 'block';
}

/**
 * Show loading state
 */
function showLoadingState() {
    // Create loading overlay if it doesn't exist
    let loadingOverlay = document.getElementById('loading-overlay');
    if (!loadingOverlay) {
        loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'loading-overlay';
        loadingOverlay.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center';
        loadingOverlay.innerHTML = `
            <div class="bg-white dark:bg-gray-800 p-5 rounded-md shadow-xl">
                <div class="flex flex-col items-center">
                    <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 dark:border-primary-400"></div>
                    <p class="mt-2 text-gray-700 dark:text-gray-300">Loading...</p>
                </div>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }
    
    // Show the overlay
    loadingOverlay.style.display = 'flex';
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

/**
 * Show error message
 */
function showError(message) {
    // Create toast if it doesn't exist
    let toast = document.getElementById('error-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'error-toast';
        toast.className = 'fixed bottom-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-transform duration-300 translate-y-20';
        document.body.appendChild(toast);
    }
    
    // Update message and show toast
    toast.textContent = message;
    toast.classList.remove('translate-y-20');
    
    // Hide toast after 5 seconds
    setTimeout(() => {
        toast.classList.add('translate-y-20');
    }, 5000);
}

/**
 * Show success message
 */
function showSuccess(message) {
    // Create toast if it doesn't exist
    let toast = document.getElementById('success-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'success-toast';
        toast.className = 'fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-transform duration-300 translate-y-20';
        document.body.appendChild(toast);
    }
    
    // Update message and show toast
    toast.textContent = message;
    toast.classList.remove('translate-y-20');
    
    // Hide toast after 5 seconds
    setTimeout(() => {
        toast.classList.add('translate-y-20');
    }, 5000);
}

// Helper function to select elements by text content
Element.prototype.contains = function(text) {
    return this.textContent.includes(text);
};

// Helper function to select elements by text content
document.querySelector = function(selector) {
    if (selector.includes(':contains(')) {
        const parts = selector.split(':contains(');
        const baseSelector = parts[0];
        const text = parts[1].slice(0, -1);
        
        const elements = document.querySelectorAll(baseSelector);
        for (let i = 0; i < elements.length; i++) {
            if (elements[i].textContent.includes(text)) {
                return elements[i];
            }
        }
        return null;
    }
    
    return document.querySelector.call(document, selector);
}; 