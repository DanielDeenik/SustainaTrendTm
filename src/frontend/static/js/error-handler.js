// SustainaTrend™ Intelligence Platform - Error Handler
// This module provides centralized error handling functionality

// Error types enum
const ErrorTypes = {
    API_ERROR: 'API_ERROR',
    VALIDATION_ERROR: 'VALIDATION_ERROR',
    NETWORK_ERROR: 'NETWORK_ERROR',
    AUTH_ERROR: 'AUTH_ERROR',
    UNKNOWN_ERROR: 'UNKNOWN_ERROR'
};

// Error messages map
const ErrorMessages = {
    [ErrorTypes.API_ERROR]: 'An error occurred while communicating with the server.',
    [ErrorTypes.VALIDATION_ERROR]: 'Please check your input and try again.',
    [ErrorTypes.NETWORK_ERROR]: 'Unable to connect to the server. Please check your internet connection.',
    [ErrorTypes.AUTH_ERROR]: 'Authentication failed. Please log in again.',
    [ErrorTypes.UNKNOWN_ERROR]: 'An unexpected error occurred. Please try again.'
};

// Error tracking
const ErrorTracker = {
    errors: [],
    maxErrors: 50,
    
    add(error) {
        this.errors.push({
            ...error,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent
        });
        
        // Limit the number of errors stored
        if (this.errors.length > this.maxErrors) {
            this.errors.shift();
        }
        
        // Log to console in development
        if (process.env.NODE_ENV === 'development') {
            console.group('Error Details');
            console.table(error);
            console.groupEnd();
        }
    },
    
    getErrors() {
        return [...this.errors];
    },
    
    clear() {
        this.errors = [];
    }
};

// Notification manager
const NotificationManager = {
    activeNotifications: new Set(),
    
    show(message, type, duration = 5000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification alert alert-${this.getAlertClass(type)}`;
        notification.textContent = message;
        
        // Add to DOM
        const container = document.querySelector('.notification-container') || this.createContainer();
        container.appendChild(notification);
        
        // Track active notification
        this.activeNotifications.add(notification);
        
        // Auto-hide after duration
        setTimeout(() => {
            this.hide(notification);
        }, duration);
        
        return notification;
    },
    
    hide(notification) {
        if (notification && notification.parentNode) {
            notification.classList.add('fade-out');
            
            // Remove from DOM after animation
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                this.activeNotifications.delete(notification);
            }, 300);
        }
    },
    
    hideAll() {
        this.activeNotifications.forEach(notification => {
            this.hide(notification);
        });
    },
    
    createContainer() {
        const container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
        return container;
    },
    
    getAlertClass(type) {
        switch (type) {
            case ErrorTypes.API_ERROR:
                return 'danger';
            case ErrorTypes.VALIDATION_ERROR:
                return 'warning';
            case ErrorTypes.NETWORK_ERROR:
                return 'danger';
            case ErrorTypes.AUTH_ERROR:
                return 'warning';
            default:
                return 'danger';
        }
    }
};

// Main error handler
const ErrorHandler = {
    // Error types
    types: ErrorTypes,
    
    // Error messages
    messages: ErrorMessages,
    
    // Handle error
    handle(error, type = ErrorTypes.UNKNOWN_ERROR) {
        console.error('Application error:', error);
        
        // Get error message
        const message = this.messages[type] || this.messages[ErrorTypes.UNKNOWN_ERROR];
        
        // Create error object
        const errorObj = {
            type,
            message,
            details: error.message || error,
            stack: error.stack
        };
        
        // Track error
        ErrorTracker.add(errorObj);
        
        // Show notification
        this.showNotification(message, type);
        
        // Log error to analytics
        this.logError(errorObj);
        
        // Return error object
        return errorObj;
    },
    
    // Show error notification
    showNotification(message, type) {
        return NotificationManager.show(message, type);
    },
    
    // Log error to analytics
    logError(error) {
        // Send to analytics service
        fetch('/api/log-error', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(error)
        }).catch(err => {
            console.error('Failed to log error:', err);
        });
    },
    
    // Handle API errors
    handleApiError(response) {
        if (!response.ok) {
            switch (response.status) {
                case 400:
                    throw this.handle(new Error('Bad Request'), ErrorTypes.VALIDATION_ERROR);
                case 401:
                    throw this.handle(new Error('Unauthorized'), ErrorTypes.AUTH_ERROR);
                case 403:
                    throw this.handle(new Error('Forbidden'), ErrorTypes.AUTH_ERROR);
                case 404:
                    throw this.handle(new Error('Not Found'), ErrorTypes.API_ERROR);
                case 500:
                    throw this.handle(new Error('Internal Server Error'), ErrorTypes.API_ERROR);
                default:
                    throw this.handle(new Error(`HTTP Error ${response.status}`), ErrorTypes.API_ERROR);
            }
        }
        return response;
    },
    
    // Handle form validation errors
    handleFormErrors(form, errors) {
        // Clear existing error messages
        form.querySelectorAll('.is-invalid').forEach(element => {
            element.classList.remove('is-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(element => {
            element.remove();
        });
        
        // Add new error messages
        Object.entries(errors).forEach(([field, message]) => {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = message;
                input.parentNode.appendChild(feedback);
            }
        });
        
        // Show error notification
        this.handle(new Error('Please correct the errors in the form.'), ErrorTypes.VALIDATION_ERROR);
    },
    
    // Get tracked errors
    getTrackedErrors() {
        return ErrorTracker.getErrors();
    },
    
    // Clear tracked errors
    clearTrackedErrors() {
        ErrorTracker.clear();
    },
    
    // Hide all notifications
    hideAllNotifications() {
        NotificationManager.hideAll();
    }
};

// Export the module
export default ErrorHandler; 