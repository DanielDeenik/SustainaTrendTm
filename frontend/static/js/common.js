/**
 * SustainaTrend™ Common UI JavaScript
 * Provides shared functionality across all dashboard pages
 */

// Toggle sidebar collapse
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const mobileToggle = document.querySelector('.mobile-toggle');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
            // Update icon
            const icon = sidebarToggle.querySelector('i');
            if (sidebar.classList.contains('collapsed')) {
                icon.classList.remove('bi-chevron-left');
                icon.classList.add('bi-chevron-right');
            } else {
                icon.classList.remove('bi-chevron-right');
                icon.classList.add('bi-chevron-left');
            }
        });
    }
    
    // Mobile toggle functionality
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-expanded');
        });
    }
    
    // Theme toggle functionality
    const themeToggleBtn = document.querySelector('.theme-toggle-button');
    const htmlElement = document.documentElement;
    
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            if (htmlElement.classList.contains('light-mode')) {
                htmlElement.classList.remove('light-mode');
                htmlElement.classList.add('dark-mode');
                themeToggleBtn.innerHTML = '<i class="bi bi-sun"></i>';
                localStorage.setItem('theme', 'dark');
            } else {
                htmlElement.classList.remove('dark-mode');
                htmlElement.classList.add('light-mode');
                themeToggleBtn.innerHTML = '<i class="bi bi-moon"></i>';
                localStorage.setItem('theme', 'light');
            }
            
            // Trigger theme update in charts if function exists
            if (typeof updateChartTheme === 'function') {
                updateChartTheme(htmlElement.classList.contains('dark-mode'));
            }
        });
    }
    
    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        if (savedTheme === 'light') {
            htmlElement.classList.remove('dark-mode');
            htmlElement.classList.add('light-mode');
            if (themeToggleBtn) themeToggleBtn.innerHTML = '<i class="bi bi-moon"></i>';
        } else {
            htmlElement.classList.remove('light-mode');
            htmlElement.classList.add('dark-mode');
            if (themeToggleBtn) themeToggleBtn.innerHTML = '<i class="bi bi-sun"></i>';
        }
    }
});

/**
 * Filter modal functionality
 */
function initFilterModal() {
    const filterBtn = document.getElementById('filter-btn');
    const filterModal = document.getElementById('filter-modal');
    const closeModal = document.getElementById('close-modal');
    const applyFilters = document.getElementById('apply-filters');
    const resetFilters = document.getElementById('reset-filters');
    
    if (!filterBtn || !filterModal) return;
    
    filterBtn.addEventListener('click', function() {
        filterModal.style.display = 'flex';
    });
    
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            filterModal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === filterModal) {
            filterModal.style.display = 'none';
        }
    });
    
    // Apply filters
    if (applyFilters) {
        applyFilters.addEventListener('click', function() {
            // Get filter values
            const timeframe = document.querySelector('input[name="timeframe"]:checked')?.value || 'all';
            
            const categories = [];
            document.querySelectorAll('input[name="category"]:checked').forEach(function(checkbox) {
                categories.push(checkbox.value);
            });
            
            // Get slider value if exists
            let sliderValue = null;
            const viralitySlider = document.getElementById('virality-slider');
            const impactSlider = document.getElementById('impact-slider');
            const scoreSlider = document.getElementById('score-slider');
            
            if (viralitySlider) sliderValue = viralitySlider.value;
            else if (impactSlider) sliderValue = impactSlider.value;
            else if (scoreSlider) sliderValue = scoreSlider.value;
            
            // Collect and apply filters
            const filters = {
                timeframe: timeframe,
                categories: categories,
                minScore: sliderValue
            };
            
            // Call page-specific filter function if available
            if (typeof applyDataFilters === 'function') {
                applyDataFilters(filters);
            }
            
            filterModal.style.display = 'none';
            
            // Show notification
            showNotification('Filters applied successfully', 'bi-funnel-fill', 'info');
        });
    }
    
    // Reset filters
    if (resetFilters) {
        resetFilters.addEventListener('click', function() {
            // Reset radio buttons
            const allTimeRadio = document.querySelector('input[name="timeframe"][value="all"]');
            if (allTimeRadio) allTimeRadio.checked = true;
            
            // Reset checkboxes
            document.querySelectorAll('input[name="category"]').forEach(function(checkbox) {
                checkbox.checked = true;
            });
            
            // Reset sliders
            const viralitySlider = document.getElementById('virality-slider');
            const impactSlider = document.getElementById('impact-slider');
            const scoreSlider = document.getElementById('score-slider');
            
            if (viralitySlider) {
                viralitySlider.value = 30;
                document.getElementById('virality-value').textContent = '30';
            }
            
            if (impactSlider) {
                impactSlider.value = 30;
                document.getElementById('impact-value').textContent = '30';
            }
            
            if (scoreSlider) {
                scoreSlider.value = 30;
                document.getElementById('score-value').textContent = '30';
            }
            
            showNotification('Filters reset to default', 'bi-arrow-counterclockwise', 'info');
        });
    }
    
    // Update slider value display
    const sliders = [
        { slider: 'virality-slider', value: 'virality-value' },
        { slider: 'impact-slider', value: 'impact-value' },
        { slider: 'score-slider', value: 'score-value' }
    ];
    
    sliders.forEach(function(item) {
        const slider = document.getElementById(item.slider);
        const valueDisplay = document.getElementById(item.value);
        
        if (slider && valueDisplay) {
            slider.addEventListener('input', function() {
                valueDisplay.textContent = slider.value;
            });
        }
    });
}

/**
 * Export dropdown functionality
 */
function initExportDropdown() {
    const exportBtn = document.getElementById('export-btn');
    const exportDropdown = document.getElementById('export-dropdown');
    
    if (!exportBtn || !exportDropdown) return;
    
    exportBtn.addEventListener('click', function(event) {
        event.stopPropagation();
        exportDropdown.style.display = exportDropdown.style.display === 'block' ? 'none' : 'block';
    });
    
    // Handle export format selection
    const exportLinks = exportDropdown.querySelectorAll('a');
    exportLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const format = this.getAttribute('data-format');
            
            // Call page-specific export function if available
            if (typeof exportData === 'function') {
                exportData(format);
            } else {
                showNotification('Export functionality not implemented', 'bi-exclamation-triangle-fill', 'warning');
            }
            
            exportDropdown.style.display = 'none';
        });
    });
    
    // Close dropdown when clicking elsewhere
    document.addEventListener('click', function() {
        exportDropdown.style.display = 'none';
    });
}

/**
 * Toast notification system
 * @param {string} message - Message to display
 * @param {string} iconClass - Bootstrap icon class
 * @param {string} type - Type of notification: 'info', 'success', 'warning', 'error'
 */
function showNotification(message, iconClass, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="bi ${iconClass}"></i>
        </div>
        <div class="toast-content">${message}</div>
        <button class="toast-close">&times;</button>
    `;
    
    container.appendChild(toast);
    
    // Add close button functionality
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', function() {
        container.removeChild(toast);
    });
    
    // Auto-close after 5 seconds
    setTimeout(function() {
        if (container.contains(toast)) {
            container.removeChild(toast);
        }
    }, 5000);
}

/**
 * Initialize common UI components
 */
function initCommonUI() {
    initFilterModal();
    initExportDropdown();
}

// Initialize common UI when document is ready
document.addEventListener('DOMContentLoaded', initCommonUI);