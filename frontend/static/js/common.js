/**
 * SustainaTrend™ Common JavaScript
 * Provides shared functionality across all platform pages
 */

/**
 * Initialize tooltips
 */
function initTooltips() {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

/**
 * Initialize dark mode functionality
 */
function initDarkMode() {
  const darkModeToggle = document.getElementById('darkModeToggle');
  const darkModeIcon = darkModeToggle.querySelector('i');
  
  // Check stored preference
  const isDarkMode = localStorage.getItem('darkMode') === 'true';
  
  // Apply initial mode
  if (isDarkMode) {
    document.body.classList.add('dark-mode');
    darkModeIcon.classList.remove('bi-moon');
    darkModeIcon.classList.add('bi-sun');
  }
  
  // Toggle dark mode on click
  darkModeToggle.addEventListener('click', (e) => {
    e.preventDefault();
    
    const isDark = document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', isDark);
    
    if (isDark) {
      darkModeIcon.classList.remove('bi-moon');
      darkModeIcon.classList.add('bi-sun');
    } else {
      darkModeIcon.classList.remove('bi-sun');
      darkModeIcon.classList.add('bi-moon');
    }
    
    // Update charts if present
    updateChartsForTheme();
  });
}

/**
 * Initialize sidebar functionality
 */
function initSidebar() {
  const sidebarToggle = document.querySelector('.navbar-toggler');
  const sidebar = document.getElementById('sidebarMenu');
  
  // Toggle sidebar on mobile
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });
    
    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
      if (window.innerWidth < 768 && 
          sidebar.classList.contains('show') && 
          !sidebar.contains(e.target) && 
          !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('show');
      }
    });
  }
}

/**
 * Initialize card animations
 */
function initCardAnimation() {
  // Apply hover effects for cards
  const cards = document.querySelectorAll('.card, .analytics-card');
  cards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-5px)';
      card.style.boxShadow = '0 8px 15px rgba(0, 0, 0, 0.1)';
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'translateY(0)';
      card.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.05)';
    });
  });
}

/**
 * Initialize notifications system
 */
function initNotifications() {
  // Sample function to show toast notifications
  window.showNotification = function(message, type = 'info', duration = 5000) {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type} show`;
    toast.role = 'alert';
    toast.ariaLive = 'assertive';
    toast.ariaAtomic = 'true';
    
    let icon = 'info-circle';
    switch (type) {
      case 'success': icon = 'check-circle'; break;
      case 'warning': icon = 'exclamation-triangle'; break;
      case 'error': icon = 'x-circle'; break;
    }
    
    // Toast content
    toast.innerHTML = `
      <div class="toast-header">
        <i class="bi bi-${icon} me-2"></i>
        <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
        <small>Just now</small>
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Attach close handler
    const closeButton = toast.querySelector('.btn-close');
    closeButton.addEventListener('click', () => {
      toast.remove();
    });
    
    // Auto-remove after duration
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  };
}

/**
 * Update chart themes if Chart.js is used
 */
function updateChartsForTheme() {
  if (window.Chart) {
    Chart.helpers.each(Chart.instances, (instance) => {
      const isDark = document.body.classList.contains('dark-mode');
      
      // Update chart colors based on theme
      if (isDark) {
        instance.options.scales.x.grid.color = 'rgba(255, 255, 255, 0.1)';
        instance.options.scales.y.grid.color = 'rgba(255, 255, 255, 0.1)';
        instance.options.scales.x.ticks.color = '#a5a5a5';
        instance.options.scales.y.ticks.color = '#a5a5a5';
      } else {
        instance.options.scales.x.grid.color = 'rgba(0, 0, 0, 0.1)';
        instance.options.scales.y.grid.color = 'rgba(0, 0, 0, 0.1)';
        instance.options.scales.x.ticks.color = '#666';
        instance.options.scales.y.ticks.color = '#666';
      }
      
      instance.update();
    });
  }
}

/**
 * Format number with thousand separators and decimal places
 * @param {number} number - Number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number
 */
function formatNumber(number, decimals = 0) {
  return number.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

/**
 * Format date for display
 * @param {string|Date} date - Date to format
 * @param {string} format - Format type (short, medium, long)
 * @returns {string} Formatted date
 */
function formatDate(date, format = 'medium') {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString('en-US', { 
        month: 'numeric', 
        day: 'numeric', 
        year: '2-digit'
      });
    case 'long':
      return dateObj.toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'long', 
        day: 'numeric', 
        year: 'numeric'
      });
    case 'time':
      return dateObj.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit'
      });
    default: // medium
      return dateObj.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric'
      });
  }
}

/**
 * Handle file download
 * @param {string} data - Data to download
 * @param {string} filename - Filename
 * @param {string} type - MIME type
 */
function downloadFile(data, filename, type = 'text/plain') {
  const blob = new Blob([data], { type });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  
  a.href = url;
  a.download = filename;
  a.click();
  
  window.URL.revokeObjectURL(url);
}

/**
 * Initialize any export buttons functionality
 */
function initExportButtons() {
  const exportButtons = document.querySelectorAll('.export-button');
  const exportDropdowns = document.querySelectorAll('.export-dropdown');
  
  exportButtons.forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault();
      
      // Find the associated dropdown
      const targetId = button.getAttribute('data-target');
      const dropdown = document.getElementById(targetId);
      
      if (dropdown) {
        // Hide all other dropdowns first
        exportDropdowns.forEach(d => {
          if (d.id !== targetId) {
            d.classList.remove('show');
          }
        });
        
        // Toggle current dropdown
        dropdown.classList.toggle('show');
        
        // Position dropdown
        positionDropdown(dropdown, button);
      }
    });
  });
  
  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.export-button') && 
        !e.target.closest('.export-dropdown')) {
      exportDropdowns.forEach(d => d.classList.remove('show'));
    }
  });
}

/**
 * Position dropdown relative to its trigger button
 * @param {HTMLElement} dropdown - Dropdown element
 * @param {HTMLElement} button - Trigger button element
 */
function positionDropdown(dropdown, button) {
  const buttonRect = button.getBoundingClientRect();
  const dropdownRect = dropdown.getBoundingClientRect();
  
  // Check if dropdown would go off screen to the right
  if (buttonRect.right + dropdownRect.width > window.innerWidth) {
    dropdown.style.left = 'auto';
    dropdown.style.right = '0';
  } else {
    dropdown.style.left = '0';
    dropdown.style.right = 'auto';
  }
}

/**
 * Create dynamic filter modal
 * @param {Object} options - Modal options
 * @param {string} options.title - Modal title
 * @param {Array} options.filters - Filter definitions
 * @param {Function} options.onApply - Callback when filters are applied
 */
function createFilterModal(options) {
  const { title = 'Filter Options', filters = [], onApply = () => {} } = options;
  
  // Create modal element if it doesn't exist
  let modal = document.getElementById('filterModal');
  
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'filterModal';
    modal.className = 'filter-modal';
    document.body.appendChild(modal);
  }
  
  // Set modal content
  modal.innerHTML = `
    <div class="filter-modal-content">
      <div class="filter-modal-header">
        <h3>${title}</h3>
        <button class="close-modal" aria-label="Close">&times;</button>
      </div>
      <div class="filter-modal-body">
        ${filters.map(filter => createFilterGroup(filter)).join('')}
      </div>
      <div class="filter-modal-footer">
        <button class="btn btn-outline-secondary" id="resetFilters">Reset</button>
        <button class="btn btn-primary" id="applyFilters">Apply Filters</button>
      </div>
    </div>
  `;
  
  // Show modal
  modal.classList.add('show');
  
  // Close button handler
  const closeButton = modal.querySelector('.close-modal');
  closeButton.addEventListener('click', () => {
    modal.classList.remove('show');
  });
  
  // Reset button handler
  const resetButton = document.getElementById('resetFilters');
  resetButton.addEventListener('click', () => {
    const filterInputs = modal.querySelectorAll('input[type="checkbox"], select');
    filterInputs.forEach(input => {
      if (input.type === 'checkbox') {
        input.checked = false;
      } else if (input.tagName === 'SELECT') {
        input.selectedIndex = 0;
      }
    });
  });
  
  // Apply button handler
  const applyButton = document.getElementById('applyFilters');
  applyButton.addEventListener('click', () => {
    const filterValues = {};
    
    // Collect filter values
    filters.forEach(filter => {
      if (filter.type === 'checkbox') {
        filterValues[filter.id] = [];
        const checkboxes = modal.querySelectorAll(`input[name="${filter.id}"]:checked`);
        checkboxes.forEach(cb => filterValues[filter.id].push(cb.value));
      } else if (filter.type === 'select') {
        const select = document.getElementById(filter.id);
        filterValues[filter.id] = select.value;
      }
    });
    
    // Call onApply callback with filter values
    onApply(filterValues);
    
    // Hide modal
    modal.classList.remove('show');
  });
  
  // Close modal when clicking outside
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.remove('show');
    }
  });
}

/**
 * Create HTML for a filter group
 * @param {Object} filter - Filter definition
 * @returns {string} HTML string
 */
function createFilterGroup(filter) {
  let content = '';
  
  if (filter.type === 'checkbox') {
    content = `
      <div class="filter-group">
        <label>${filter.label}</label>
        <div class="filter-options">
          ${filter.options.map(option => `
            <div class="filter-option">
              <input type="checkbox" 
                     id="${filter.id}-${option.value}" 
                     name="${filter.id}" 
                     value="${option.value}"
                     ${option.selected ? 'checked' : ''}>
              <label for="${filter.id}-${option.value}">${option.label}</label>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  } else if (filter.type === 'select') {
    content = `
      <div class="filter-group">
        <label for="${filter.id}">${filter.label}</label>
        <select class="form-select" id="${filter.id}">
          ${filter.options.map(option => `
            <option value="${option.value}" ${option.selected ? 'selected' : ''}>
              ${option.label}
            </option>
          `).join('')}
        </select>
      </div>
    `;
  }
  
  return content;
}