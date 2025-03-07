/**
 * SustainaTrend™ Common JavaScript
 * Provides shared functionality across all pages
 */

/**
 * Initialize tooltips for the current page
 * Compatible with Bootstrap 5
 */
function initTooltips() {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  if (tooltipTriggerList.length > 0) {
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
  }
}

/**
 * Initialize dark mode functionality
 */
function initDarkMode() {
  // If ThemeManager is already initialized, skip this
  if (window.themeManager) return;
  
  // Otherwise, create a minimal dark mode toggle
  const darkModeToggle = document.getElementById('darkModeToggle');
  if (!darkModeToggle) return;
  
  const themeKey = 'sustainatrend-theme';
  const savedTheme = localStorage.getItem(themeKey) || 'light';
  
  // Apply theme from storage or system preference
  applyTheme(savedTheme);
  
  // Update toggle button icon
  updateToggleIcon(savedTheme);
  
  // Set up click handler
  darkModeToggle.addEventListener('click', function(e) {
    e.preventDefault();
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    applyTheme(newTheme);
    updateToggleIcon(newTheme);
    
    // Update charts if function is available
    if (typeof window.updateChartTheme === 'function') {
      window.updateChartTheme(newTheme === 'dark');
    }
  });
  
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem(themeKey, theme);
  }
  
  function updateToggleIcon(theme) {
    const icon = darkModeToggle.querySelector('i');
    if (!icon) return;
    
    if (theme === 'dark') {
      icon.classList.remove('bi-moon');
      icon.classList.add('bi-sun');
      darkModeToggle.setAttribute('title', 'Switch to light mode');
    } else {
      icon.classList.remove('bi-sun');
      icon.classList.add('bi-moon');
      darkModeToggle.setAttribute('title', 'Switch to dark mode');
    }
  }
}

/**
 * Initialize sidebar functionality
 */
function initSidebar() {
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  const main = document.querySelector('main');
  
  if (!sidebarToggle || !sidebar || !main) return;
  
  sidebarToggle.addEventListener('click', function() {
    sidebar.classList.toggle('collapsed');
    main.classList.toggle('sidebar-collapsed');
    
    // Store sidebar state in localStorage
    const isCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('sidebar-collapsed', isCollapsed ? 'true' : 'false');
  });
  
  // Apply saved sidebar state on load
  const savedState = localStorage.getItem('sidebar-collapsed');
  if (savedState === 'true') {
    sidebar.classList.add('collapsed');
    main.classList.add('sidebar-collapsed');
  }
}

/**
 * Initialize export menu functionality
 */
function initExportMenu() {
  const exportButton = document.getElementById('export-button');
  const exportDropdown = document.getElementById('export-dropdown');
  
  if (!exportButton || !exportDropdown) return;
  
  exportButton.addEventListener('click', function(e) {
    e.preventDefault();
    exportDropdown.classList.toggle('show');
  });
  
  // Close dropdown when clicking outside
  document.addEventListener('click', function(e) {
    if (!exportButton.contains(e.target) && !exportDropdown.contains(e.target)) {
      exportDropdown.classList.remove('show');
    }
  });
}

/**
 * Initialize notifications system
 */
function initNotifications() {
  // Create toast container if it doesn't exist
  if (!document.getElementById('toastContainer')) {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
  }
}

/**
 * Show a toast notification
 * @param {string} message - Toast message
 * @param {string} icon - Bootstrap icon class
 * @param {string} type - Toast type (success, error, warning, info)
 * @param {number} duration - Duration in ms
 */
function showToast(message, type = 'info', duration = 3000) {
  // Get icon based on type
  const iconClass = getToastIcon(type);
  
  // Create toast container if it doesn't exist
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(toastContainer);
  }
  
  // Create toast element
  const toastId = 'toast-' + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="toast-header ${type === 'error' ? 'bg-danger text-white' : `bg-${type}`}${type === 'info' ? '' : ' text-white'}">
        <i class="bi ${iconClass} me-2"></i>
        <strong class="me-auto">SustainaTrend™</strong>
        <small>${formatTime(new Date())}</small>
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, { delay: duration });
  toast.show();
  
  // Remove toast from DOM after it's hidden
  toastElement.addEventListener('hidden.bs.toast', () => {
    toastElement.remove();
  });
}

/**
 * Get icon class for toast notification
 * @param {string} type - Toast type
 * @returns {string} Icon class
 */
function getToastIcon(type) {
  switch (type) {
    case 'success': return 'bi-check-circle-fill';
    case 'error': return 'bi-exclamation-triangle-fill';
    case 'warning': return 'bi-exclamation-circle-fill';
    case 'info': 
    default: return 'bi-info-circle-fill';
  }
}

/**
 * Format time for notifications
 * @param {Date} date - Date to format
 * @returns {string} Formatted time string
 */
function formatTime(date) {
  return date.toLocaleTimeString(undefined, { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

/**
 * Format date
 * @param {Date|string} date - Date to format
 * @param {string} format - Display format (short, medium, long, time)
 * @returns {string} Formatted date string
 */
function formatDate(date, format = 'medium') {
  const dateObj = date instanceof Date ? date : new Date(date);
  
  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString();
    case 'long':
      return dateObj.toLocaleDateString(undefined, { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    case 'time':
      return dateObj.toLocaleTimeString(undefined, { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    case 'medium':
    default:
      return dateObj.toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
  }
}

/**
 * Initialize page functionality on DOM ready
 */
document.addEventListener('DOMContentLoaded', function() {
  // Initialize common functionality
  initTooltips();
  initDarkMode();
  initSidebar();
  initNotifications();
  
  // Check for specific page components and initialize them
  if (document.getElementById('export-button')) {
    initExportMenu();
  }
});

// Set global functions for accessibility from other scripts
window.showToast = showToast;
window.formatDate = formatDate;