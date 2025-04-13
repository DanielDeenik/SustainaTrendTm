// SustainaTrend™ Intelligence Platform - Frontend JavaScript
// This module provides shared functionality for the frontend application

// Import error handler
import ErrorHandler from './error-handler.js';

// Constants
const API_ENDPOINTS = {
    metrics: '/api/metrics',
    strategy: '/api/strategy/data',
    analytics: '/api/analytics/data',
    realestate: '/api/realestate/data'
};

// Chart configuration cache with TTL
const chartConfigCache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes in milliseconds

// DOM element cache
const domCache = {
    elements: new Map(),
    get(selector) {
        if (!this.elements.has(selector)) {
            this.elements.set(selector, document.querySelector(selector));
        }
        return this.elements.get(selector);
    },
    getAll(selector) {
        if (!this.elements.has(selector)) {
            this.elements.set(selector, document.querySelectorAll(selector));
        }
        return this.elements.get(selector);
    },
    clear() {
        this.elements.clear();
    }
};

// Main application object
const SustainaTrend = {
    // State management
    state: {
        data: null,
        loading: false,
        error: null,
        charts: new Map(),
        lastUpdate: null
    },

    // Initialize the application
    init() {
        this.setupEventListeners();
        this.loadInitialData();
        
        // Set up periodic data refresh
        this.setupDataRefresh();
    },

    // Set up event listeners
    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            // Mobile menu toggle
            const menuToggle = domCache.get('.mobile-menu-toggle');
            if (menuToggle) {
                menuToggle.addEventListener('click', () => {
                    const sidebar = domCache.get('.sidebar');
                    if (sidebar) sidebar.classList.toggle('show');
                });
            }

            // Setup other event listeners
            this.setupChartUpdates();
            this.setupFormHandlers();
            
            // Clear DOM cache on page unload
            window.addEventListener('unload', () => {
                domCache.clear();
            });
        });
    },

    // Set up periodic data refresh
    setupDataRefresh() {
        // Refresh data every 5 minutes
        setInterval(() => {
            this.loadInitialData();
        }, 5 * 60 * 1000);
    },

    // Load initial data
    async loadInitialData() {
        try {
            this.setLoadingState(true);
            const response = await fetchData(API_ENDPOINTS.metrics);
            this.state.data = response;
            this.state.lastUpdate = new Date();
            this.updateUI();
        } catch (error) {
            ErrorHandler.handle(error);
        } finally {
            this.setLoadingState(false);
        }
    },

    // Update UI with current state
    updateUI() {
        if (!this.state.data) return;

        // Update metrics
        this.updateMetrics();
        
        // Update charts
        this.updateCharts();
        
        // Update status indicators
        this.updateStatus();
        
        // Update last refresh time
        this.updateLastRefreshTime();
    },
    
    // Update last refresh time
    updateLastRefreshTime() {
        const lastRefreshElement = domCache.get('.last-refresh-time');
        if (lastRefreshElement && this.state.lastUpdate) {
            lastRefreshElement.textContent = this.state.lastUpdate.toLocaleTimeString();
        }
    },

    // Update metrics display
    updateMetrics() {
        const metrics = this.state.data;
        if (!metrics) return;

        // Update each metric card
        Object.entries(metrics).forEach(([key, value]) => {
            const element = domCache.get(`[data-metric="${key}"]`);
            if (element) {
                const valueElement = element.querySelector('.metric-value');
                const changeElement = element.querySelector('.metric-change');
                
                if (valueElement) valueElement.textContent = value.value;
                if (changeElement) {
                    changeElement.textContent = `${value.change > 0 ? '+' : ''}${value.change}%`;
                    changeElement.classList.toggle('text-success', value.change > 0);
                    changeElement.classList.toggle('text-danger', value.change < 0);
                }
            }
        });
    },

    // Create and update charts
    updateCharts() {
        const chartElements = domCache.getAll('[data-chart]');
        chartElements.forEach(element => {
            const chartType = element.dataset.chart;
            const chartId = element.id;
            
            // Get chart configuration
            const chartData = this.getChartData(chartType);
            if (!chartData) return;
            
            // Create or update chart
            this.createChart(element, chartData, chartId);
        });
    },

    // Get chart configuration based on type
    getChartData(type) {
        // Check cache first
        if (chartConfigCache.has(type)) {
            const cachedConfig = chartConfigCache.get(type);
            // Check if cache is still valid
            if (Date.now() - cachedConfig.timestamp < CACHE_TTL) {
                return cachedConfig.config;
            }
            // Cache expired, remove it
            chartConfigCache.delete(type);
        }
        
        const defaultOptions = {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        };

        let chartConfig = null;
        
        switch (type) {
            case 'sustainability':
                chartConfig = {
                    type: 'line',
                    data: {
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                        datasets: [{
                            label: 'Emissions',
                            data: this.state.data?.emissions_trend || [],
                            borderColor: '#2ecc71',
                            tension: 0.1
                        }, {
                            label: 'Energy',
                            data: this.state.data?.energy_trend || [],
                            borderColor: '#3498db',
                            tension: 0.1
                        }]
                    },
                    options: defaultOptions
                };
                break;
            case 'analytics':
                chartConfig = {
                    type: 'line',
                    data: {
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                        datasets: [{
                            label: 'Documents Processed',
                            data: this.state.data?.documents_trend || [120, 150, 180, 200, 190, 160],
                            borderColor: '#2ecc71',
                            tension: 0.1
                        }, {
                            label: 'Analysis Complete',
                            data: this.state.data?.analysis_trend || [100, 130, 150, 170, 160, 140],
                            borderColor: '#3498db',
                            tension: 0.1
                        }]
                    },
                    options: defaultOptions
                };
                break;
            case 'document_types':
                chartConfig = {
                    type: 'doughnut',
                    data: {
                        labels: ['Sustainability Reports', 'Financial Statements', 'Environmental Data', 'Social Impact', 'Governance'],
                        datasets: [{
                            data: this.state.data?.document_types || [30, 25, 20, 15, 10],
                            backgroundColor: [
                                '#2ecc71',
                                '#3498db',
                                '#e74c3c',
                                '#f1c40f',
                                '#9b59b6'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'right',
                            }
                        }
                    }
                };
                break;
            case 'strategy_performance':
                chartConfig = {
                    type: 'line',
                    data: {
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                        datasets: [{
                            label: 'Strategy Success Rate',
                            data: this.state.data?.success_rate_trend || [65, 70, 75, 80, 85, 90],
                            borderColor: '#2ecc71',
                            tension: 0.1
                        }, {
                            label: 'ROI',
                            data: this.state.data?.roi_trend || [20, 25, 30, 35, 40, 45],
                            borderColor: '#3498db',
                            tension: 0.1
                        }]
                    },
                    options: defaultOptions
                };
                break;
            case 'recent_strategies':
                chartConfig = {
                    type: 'bar',
                    data: {
                        labels: ['Carbon Reduction', 'Energy Efficiency', 'Waste Management', 'Water Conservation'],
                        datasets: [{
                            label: 'Progress',
                            data: this.state.data?.strategy_progress || [75, 60, 45, 30],
                            backgroundColor: [
                                '#2ecc71',
                                '#3498db',
                                '#e74c3c',
                                '#f1c40f'
                            ]
                        }]
                    },
                    options: {
                        ...defaultOptions,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                };
                break;
        }
        
        // Cache the configuration with timestamp
        if (chartConfig) {
            chartConfigCache.set(type, {
                config: chartConfig,
                timestamp: Date.now()
            });
        }
        
        return chartConfig;
    },

    // Create a chart
    createChart(element, config, chartId) {
        // Check if chart already exists
        if (this.state.charts.has(chartId)) {
            // Update existing chart
            const chart = this.state.charts.get(chartId);
            chart.data = config.data;
            chart.update('none'); // Use 'none' mode for better performance
            return;
        }
        
        // Create new chart
        const ctx = element.getContext('2d');
        const chart = new Chart(ctx, config);
        this.state.charts.set(chartId, chart);
    },

    // Set loading state
    setLoadingState(isLoading) {
        this.state.loading = isLoading;
        document.body.classList.toggle('loading', isLoading);
        
        const loader = domCache.get('.loader');
        if (loader) {
            loader.style.display = isLoading ? 'block' : 'none';
        }
    },

    // Setup form handlers
    setupFormHandlers() {
        const forms = domCache.getAll('form[data-api]');
        forms.forEach(form => {
            this.handleFormSubmit(form, form.dataset.api);
        });
    },

    // Handle form submission
    handleFormSubmit(form, url, options = {}) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            try {
                this.setLoadingState(true);
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                
                const response = await fetchData(url, {
                    method: options.method || 'POST',
                    body: JSON.stringify(data)
                });
                
                if (response.errors) {
                    ErrorHandler.handleFormErrors(form, response.errors);
                    return;
                }
                
                if (options.onSuccess) {
                    options.onSuccess(response);
                }
                
                // Show success message
                this.showSuccessMessage('Operation completed successfully');
                
                // Reset form
                form.reset();
                
                // Refresh data if needed
                if (form.dataset.refresh === 'true') {
                    this.loadInitialData();
                }
            } catch (error) {
                ErrorHandler.handle(error);
            } finally {
                this.setLoadingState(false);
            }
        });
    },
    
    // Show success message
    showSuccessMessage(message) {
        const successElement = domCache.get('.success-notification');
        if (successElement) {
            successElement.textContent = message;
            successElement.style.display = 'block';
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                successElement.style.display = 'none';
            }, 3000);
        }
    },
    
    // Update status indicators
    updateStatus() {
        // Update status indicators based on the current state
        const statusIndicators = domCache.getAll('.status-indicator');
        statusIndicators.forEach(indicator => {
            const status = indicator.dataset.status;
            if (status === 'online') {
                indicator.classList.add('status-online');
                indicator.classList.remove('status-offline');
            } else if (status === 'offline') {
                indicator.classList.add('status-offline');
                indicator.classList.remove('status-online');
            }
        });
    },
    
    // Setup chart updates
    setupChartUpdates() {
        // Set up periodic chart updates for real-time data
        const chartUpdateInterval = 60 * 1000; // 1 minute
        
        setInterval(() => {
            // Only update charts if they're visible
            this.state.charts.forEach((chart, id) => {
                const element = document.getElementById(id);
                if (element && isElementInViewport(element)) {
                    // Fetch new data for this chart
                    this.updateChartData(id);
                }
            });
        }, chartUpdateInterval);
    },
    
    // Update chart data
    async updateChartData(chartId) {
        try {
            const chart = this.state.charts.get(chartId);
            if (!chart) return;
            
            // Determine which endpoint to use based on chart type
            let endpoint = API_ENDPOINTS.metrics;
            if (chartId.includes('strategy')) {
                endpoint = API_ENDPOINTS.strategy;
            } else if (chartId.includes('analytics')) {
                endpoint = API_ENDPOINTS.analytics;
            } else if (chartId.includes('realestate')) {
                endpoint = API_ENDPOINTS.realestate;
            }
            
            // Fetch new data
            const response = await fetchData(endpoint);
            
            // Update chart with new data
            if (response && chart) {
                // Update chart data based on chart type
                // This is a simplified example - actual implementation would depend on chart structure
                if (chartId.includes('sustainability')) {
                    chart.data.datasets[0].data = response.emissions_trend || chart.data.datasets[0].data;
                    chart.data.datasets[1].data = response.energy_trend || chart.data.datasets[1].data;
                }
                
                // Update the chart
                chart.update('none');
            }
        } catch (error) {
            // Silently handle errors for background updates
            console.error(`Error updating chart ${chartId}:`, error);
        }
    }
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    SustainaTrend.init();
});

// Fetch data with error handling
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        // Handle API errors
        ErrorHandler.handleApiError(response);
        
        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            throw ErrorHandler.handle(error, ErrorHandler.types.NETWORK_ERROR);
        }
        throw error;
    }
}

// Helper function to check if element is in viewport
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
} 