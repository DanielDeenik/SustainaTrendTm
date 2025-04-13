// SustainaTrend™ Intelligence Platform - Performance Monitor
// This module provides performance monitoring and optimization functionality

/**
 * Performance Monitor
 * Tracks and reports on application performance metrics
 */
class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoad: 0,
            apiCalls: {},
            renderTimes: {},
            memoryUsage: [],
            longTasks: []
        };
        
        this.observers = {
            performance: null,
            longTasks: null,
            memory: null
        };
        
        this.config = {
            longTaskThreshold: 50, // ms
            memorySampleInterval: 30000, // 30 seconds
            maxMemorySamples: 20
        };
        
        this.init();
    }
    
    /**
     * Initialize performance monitoring
     */
    init() {
        // Track page load time
        this.trackPageLoad();
        
        // Set up performance observer for long tasks
        this.setupLongTaskObserver();
        
        // Set up memory monitoring if available
        if (performance.memory) {
            this.setupMemoryMonitoring();
        }
        
        // Track API call performance
        this.interceptFetch();
        
        // Track render times
        this.trackRenderTimes();
    }
    
    /**
     * Track page load time
     */
    trackPageLoad() {
        window.addEventListener('load', () => {
            const timing = performance.timing;
            this.metrics.pageLoad = timing.loadEventEnd - timing.navigationStart;
            
            // Log to console in development
            if (process.env.NODE_ENV === 'development') {
                console.log(`Page load time: ${this.metrics.pageLoad}ms`);
            }
            
            // Send to analytics
            this.logMetric('page_load', this.metrics.pageLoad);
        });
    }
    
    /**
     * Set up observer for long tasks
     */
    setupLongTaskObserver() {
        if ('PerformanceObserver' in window) {
            try {
                this.observers.longTasks = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach(entry => {
                        if (entry.duration > this.config.longTaskThreshold) {
                            this.metrics.longTasks.push({
                                name: entry.name,
                                duration: entry.duration,
                                startTime: entry.startTime,
                                timestamp: new Date().toISOString()
                            });
                            
                            // Log to console in development
                            if (process.env.NODE_ENV === 'development') {
                                console.warn(`Long task detected: ${entry.name} (${entry.duration}ms)`);
                            }
                            
                            // Send to analytics
                            this.logMetric('long_task', {
                                name: entry.name,
                                duration: entry.duration
                            });
                        }
                    });
                });
                
                this.observers.longTasks.observe({ entryTypes: ['longtask'] });
            } catch (e) {
                console.error('Failed to set up long task observer:', e);
            }
        }
    }
    
    /**
     * Set up memory monitoring
     */
    setupMemoryMonitoring() {
        // Initial memory usage
        this.metrics.memoryUsage.push({
            used: performance.memory.usedJSHeapSize,
            total: performance.memory.totalJSHeapSize,
            limit: performance.memory.jsHeapSizeLimit,
            timestamp: new Date().toISOString()
        });
        
        // Sample memory usage periodically
        setInterval(() => {
            this.metrics.memoryUsage.push({
                used: performance.memory.usedJSHeapSize,
                total: performance.memory.totalJSHeapSize,
                limit: performance.memory.jsHeapSizeLimit,
                timestamp: new Date().toISOString()
            });
            
            // Limit the number of samples
            if (this.metrics.memoryUsage.length > this.config.maxMemorySamples) {
                this.metrics.memoryUsage.shift();
            }
            
            // Check for memory leaks
            this.checkMemoryLeaks();
        }, this.config.memorySampleInterval);
    }
    
    /**
     * Check for potential memory leaks
     */
    checkMemoryLeaks() {
        if (this.metrics.memoryUsage.length < 2) return;
        
        const latest = this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1];
        const previous = this.metrics.memoryUsage[this.metrics.memoryUsage.length - 2];
        
        // If memory usage has increased by more than 50% between samples
        if (latest.used > previous.used * 1.5) {
            console.warn('Potential memory leak detected');
            
            // Send to analytics
            this.logMetric('memory_leak', {
                increase: latest.used - previous.used,
                percentage: ((latest.used / previous.used) - 1) * 100
            });
        }
    }
    
    /**
     * Intercept fetch calls to track API performance
     */
    interceptFetch() {
        const originalFetch = window.fetch;
        
        window.fetch = async (url, options = {}) => {
            const startTime = performance.now();
            const apiName = this.getApiNameFromUrl(url);
            
            try {
                const response = await originalFetch(url, options);
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                // Track API call
                this.trackApiCall(apiName, duration, response.ok);
                
                return response;
            } catch (error) {
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                // Track failed API call
                this.trackApiCall(apiName, duration, false);
                
                throw error;
            }
        };
    }
    
    /**
     * Track API call performance
     */
    trackApiCall(apiName, duration, success) {
        if (!this.metrics.apiCalls[apiName]) {
            this.metrics.apiCalls[apiName] = {
                count: 0,
                totalDuration: 0,
                successCount: 0,
                failureCount: 0,
                avgDuration: 0,
                minDuration: Infinity,
                maxDuration: 0
            };
        }
        
        const api = this.metrics.apiCalls[apiName];
        api.count++;
        api.totalDuration += duration;
        api.avgDuration = api.totalDuration / api.count;
        
        if (duration < api.minDuration) api.minDuration = duration;
        if (duration > api.maxDuration) api.maxDuration = duration;
        
        if (success) {
            api.successCount++;
        } else {
            api.failureCount++;
        }
        
        // Log slow API calls
        if (duration > 1000) { // More than 1 second
            console.warn(`Slow API call: ${apiName} (${duration}ms)`);
            
            // Send to analytics
            this.logMetric('slow_api', {
                api: apiName,
                duration: duration
            });
        }
    }
    
    /**
     * Track render times for components
     */
    trackRenderTimes() {
        // Use MutationObserver to detect DOM changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check if any added nodes have data-render-time attribute
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1 && node.hasAttribute('data-render-time')) {
                            const componentName = node.getAttribute('data-component');
                            const renderTime = parseFloat(node.getAttribute('data-render-time'));
                            
                            if (!this.metrics.renderTimes[componentName]) {
                                this.metrics.renderTimes[componentName] = {
                                    count: 0,
                                    totalTime: 0,
                                    avgTime: 0,
                                    minTime: Infinity,
                                    maxTime: 0
                                };
                            }
                            
                            const component = this.metrics.renderTimes[componentName];
                            component.count++;
                            component.totalTime += renderTime;
                            component.avgTime = component.totalTime / component.count;
                            
                            if (renderTime < component.minTime) component.minTime = renderTime;
                            if (renderTime > component.maxTime) component.maxTime = renderTime;
                            
                            // Log slow renders
                            if (renderTime > 100) { // More than 100ms
                                console.warn(`Slow render: ${componentName} (${renderTime}ms)`);
                                
                                // Send to analytics
                                this.logMetric('slow_render', {
                                    component: componentName,
                                    time: renderTime
                                });
                            }
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    /**
     * Get API name from URL
     */
    getApiNameFromUrl(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.pathname;
        } catch (e) {
            return url;
        }
    }
    
    /**
     * Log metric to analytics
     */
    logMetric(name, value) {
        // Send to analytics service
        fetch('/api/log-metric', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                value,
                timestamp: new Date().toISOString(),
                url: window.location.href
            })
        }).catch(err => {
            console.error('Failed to log metric:', err);
        });
    }
    
    /**
     * Get performance report
     */
    getReport() {
        return {
            pageLoad: this.metrics.pageLoad,
            apiCalls: this.metrics.apiCalls,
            renderTimes: this.metrics.renderTimes,
            longTasks: this.metrics.longTasks.length,
            memoryUsage: this.metrics.memoryUsage.length > 0 ? 
                this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1] : null
        };
    }
    
    /**
     * Clean up observers
     */
    cleanup() {
        if (this.observers.longTasks) {
            this.observers.longTasks.disconnect();
        }
    }
}

// Create singleton instance
const performanceMonitor = new PerformanceMonitor();

// Export the module
export default performanceMonitor; 