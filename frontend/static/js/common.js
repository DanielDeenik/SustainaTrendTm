/**
 * SustainaTrend™ Common JavaScript Functions
 * This file contains shared functionality used across the platform
 */

/**
 * Initialize dark mode toggle functionality
 */
function initDarkMode() {
  const darkModeToggle = document.getElementById('darkModeToggle');
  const htmlElement = document.documentElement;
  const darkModeIcon = darkModeToggle.querySelector('i');
  
  // Check for saved dark mode preference or system preference
  const savedDarkMode = localStorage.getItem('darkMode');
  const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  // Apply dark mode based on saved preference or system preference
  if (savedDarkMode === 'enabled' || (savedDarkMode === null && prefersDarkMode)) {
    document.body.classList.add('dark-mode');
    darkModeIcon.classList.remove('bi-moon');
    darkModeIcon.classList.add('bi-sun');
    updateChartsTheme(true);
  }
  
  // Add event listener for dark mode toggle
  if (darkModeToggle) {
    darkModeToggle.addEventListener('click', (e) => {
      e.preventDefault();
      
      // Toggle dark mode class on body
      document.body.classList.toggle('dark-mode');
      
      // Toggle icon between moon and sun
      if (document.body.classList.contains('dark-mode')) {
        darkModeIcon.classList.remove('bi-moon');
        darkModeIcon.classList.add('bi-sun');
        localStorage.setItem('darkMode', 'enabled');
        updateChartsTheme(true);
      } else {
        darkModeIcon.classList.remove('bi-sun');
        darkModeIcon.classList.add('bi-moon');
        localStorage.setItem('darkMode', 'disabled');
        updateChartsTheme(false);
      }
    });
  }
}

/**
 * Update charts theme based on dark mode
 */
function updateChartsTheme(isDarkMode) {
  // Set Chart.js defaults based on dark mode
  if (window.Chart) {
    Chart.defaults.color = isDarkMode ? '#e0e0e0' : '#666';
    Chart.defaults.borderColor = isDarkMode ? '#444' : '#e0e0e0';
    
    // Find and update all active charts
    Object.values(Chart.instances || {}).forEach(chart => {
      if (chart.options.plugins && chart.options.plugins.legend) {
        chart.options.plugins.legend.labels.color = isDarkMode ? '#e0e0e0' : '#666';
      }
      
      if (chart.options.scales) {
        Object.values(chart.options.scales).forEach(scale => {
          scale.grid = scale.grid || {};
          scale.grid.color = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
          scale.ticks = scale.ticks || {};
          scale.ticks.color = isDarkMode ? '#adb5bd' : '#666';
        });
      }
      
      chart.update();
    });
  }
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * Initialize mobile sidebar behavior
 */
function initSidebar() {
  const sidebarToggle = document.querySelector('.navbar-toggler');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function () {
      const sidebar = document.getElementById('sidebarMenu');
      if (sidebar) {
        sidebar.classList.toggle('show');
      }
    });
    
    // Close sidebar when clicking outside of it on mobile
    document.addEventListener('click', function (event) {
      const sidebar = document.getElementById('sidebarMenu');
      if (sidebar && sidebar.classList.contains('show') && 
          !sidebar.contains(event.target) && 
          !sidebarToggle.contains(event.target)) {
        sidebar.classList.remove('show');
      }
    });
  }
}

/**
 * Initialize filter dropdowns
 */
function initFilterDropdowns() {
  const filterDropdowns = document.querySelectorAll('.filter-dropdown');
  
  filterDropdowns.forEach(dropdown => {
    const dropdownItems = dropdown.querySelectorAll('.dropdown-item');
    const dropdownButton = dropdown.querySelector('.dropdown-toggle');
    const filterType = dropdown.dataset.filterType;
    
    dropdownItems.forEach(item => {
      item.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Update active state in dropdown
        dropdownItems.forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        
        // Update button text
        dropdownButton.textContent = this.textContent.trim();
        
        // Trigger filter event
        const filterValue = this.dataset.value;
        const filterEvent = new CustomEvent('filter-changed', {
          detail: {
            type: filterType,
            value: filterValue
          }
        });
        document.dispatchEvent(filterEvent);
      });
    });
  });
}

/**
 * Initialize export menu
 */
function initExportMenu() {
  const exportLinks = document.querySelectorAll('[data-export-format]');
  
  exportLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      const format = this.dataset.exportFormat;
      
      // Trigger export event
      const exportEvent = new CustomEvent('export-requested', {
        detail: {
          format: format
        }
      });
      document.dispatchEvent(exportEvent);
    });
  });
}

/**
 * Initialize notification system
 */
function initNotifications() {
  // Create a reusable function to show notifications
  window.showNotification = function(message, icon = 'bi-info-circle', type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) return;
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast toast-${type} align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Generate unique ID for the toast
    const toastId = 'toast-' + Date.now();
    toastEl.id = toastId;
    
    // Create toast content
    toastEl.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          <i class="bi ${icon} me-2"></i>
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    `;
    
    // Append toast to container
    toastContainer.appendChild(toastEl);
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastEl, {
      delay: 5000,
      autohide: true
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastEl.addEventListener('hidden.bs.toast', function () {
      this.remove();
    });
    
    return toast;
  };
}

/**
 * Initialize card animations
 */
function initCardAnimation() {
  const cards = document.querySelectorAll('.card');
  
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      if (!this.classList.contains('no-hover-effect')) {
        this.style.transform = 'translateY(-5px)';
        this.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.1)';
      }
    });
    
    card.addEventListener('mouseleave', function() {
      if (!this.classList.contains('no-hover-effect')) {
        this.style.transform = '';
        this.style.boxShadow = '';
      }
    });
  });
}

/**
 * Format number with appropriate unit prefixes (K, M, B)
 * @param {number} value - Number to format
 * @param {number} decimals - Decimal places to show
 * @return {string} Formatted number
 */
function formatNumber(value, decimals = 1) {
  if (value === null || value === undefined) return '-';
  
  if (value === 0) return '0';
  
  const absValue = Math.abs(value);
  const sign = value < 0 ? '-' : '';
  
  if (absValue >= 1000000000) {
    return sign + (absValue / 1000000000).toFixed(decimals) + 'B';
  } else if (absValue >= 1000000) {
    return sign + (absValue / 1000000).toFixed(decimals) + 'M';
  } else if (absValue >= 1000) {
    return sign + (absValue / 1000).toFixed(decimals) + 'K';
  } else {
    return sign + absValue.toFixed(decimals);
  }
}

/**
 * Format date for display
 * @param {string} dateStr - Date string
 * @param {string} format - Output format ('short', 'medium', 'long')
 * @return {string} Formatted date
 */
function formatDate(dateStr, format = 'medium') {
  if (!dateStr) return '';
  
  const date = new Date(dateStr);
  
  if (isNaN(date.getTime())) return dateStr;
  
  if (format === 'short') {
    return date.toLocaleDateString();
  } else if (format === 'long') {
    return date.toLocaleDateString(undefined, { 
      weekday: 'long',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  } else {
    return date.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  }
}

/**
 * Helper function to create a debounced function
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @return {Function} Debounced function
 */
function debounce(func, delay = 300) {
  let timeoutId;
  
  return function(...args) {
    clearTimeout(timeoutId);
    
    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
}

/**
 * Get appropriate icon for a category
 * @param {string} category - Category name
 * @return {string} Icon class
 */
function getCategoryIcon(category) {
  switch (category.toLowerCase()) {
    case 'energy':
      return 'bi-lightning';
    case 'emissions':
      return 'bi-cloud';
    case 'water':
      return 'bi-droplet';
    case 'waste':
      return 'bi-trash';
    case 'social':
      return 'bi-people';
    case 'governance':
      return 'bi-clipboard-check';
    default:
      return 'bi-graph-up';
  }
}