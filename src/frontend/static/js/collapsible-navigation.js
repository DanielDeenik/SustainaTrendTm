/**
 * Collapsible Navigation System for SustainaTrend Platform
 * Finchat-inspired interactive navigation panel with responsive behavior
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeCollapsibleNavigation();
    initializeDataCards();
});

/**
 * Initialize the collapsible navigation system
 */
function initializeCollapsibleNavigation() {
    // Get navigation elements
    const navToggle = document.querySelector('.st-nav-toggle');
    const navSidebar = document.querySelector('.st-nav-sidebar');
    const menuItems = document.querySelectorAll('.st-nav-item');
    
    // Set active menu item based on current path
    setActiveMenuItem();
    
    // Toggle navigation collapse state
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navSidebar.classList.toggle('collapsed');
            
            // Save state to localStorage
            const isCollapsed = navSidebar.classList.contains('collapsed');
            localStorage.setItem('st-nav-collapsed', isCollapsed);
            
            // Update tooltip positions if needed
            updateTooltipPositions();
        });
    }
    
    // Load saved collapse state
    const savedCollapsedState = localStorage.getItem('st-nav-collapsed');
    if (savedCollapsedState === 'true') {
        navSidebar.classList.add('collapsed');
    }
    
    // Handle mobile navigation
    handleMobileNavigation();
    
    // Add tooltip interaction
    menuItems.forEach(menuItem => {
        const itemText = menuItem.querySelector('.st-nav-item-text').textContent;
        const tooltip = document.createElement('div');
        tooltip.className = 'st-nav-tooltip';
        tooltip.textContent = itemText;
        menuItem.appendChild(tooltip);
        
        // Position tooltip on hover
        menuItem.addEventListener('mouseenter', function() {
            positionTooltip(menuItem, tooltip);
        });
    });
}

/**
 * Set the active menu item based on current path
 */
function setActiveMenuItem() {
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.st-nav-item');
    
    menuItems.forEach(item => {
        const itemPath = item.getAttribute('href');
        if (itemPath === currentPath || 
            (currentPath.includes(itemPath) && itemPath !== '/')) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

/**
 * Handle mobile-specific navigation behavior
 */
function handleMobileNavigation() {
    const navSidebar = document.querySelector('.st-nav-sidebar');
    const navToggle = document.querySelector('.st-nav-toggle');
    const menuItems = document.querySelectorAll('.st-nav-item');
    
    // Check if we're on mobile
    function isMobile() {
        return window.innerWidth <= 768;
    }
    
    // Update navigation for mobile
    function updateMobileNav() {
        if (isMobile()) {
            navSidebar.classList.add('hidden');
            
            // Hide sidebar when clicking a menu item
            menuItems.forEach(item => {
                item.addEventListener('click', function() {
                    navSidebar.classList.add('hidden');
                });
            });
        } else {
            navSidebar.classList.remove('hidden');
        }
    }
    
    // Toggle sidebar visibility on mobile
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            if (isMobile()) {
                navSidebar.classList.toggle('hidden');
            }
        });
    }
    
    // Initialize and update on resize
    updateMobileNav();
    window.addEventListener('resize', updateMobileNav);
}

/**
 * Position tooltip relative to menu item
 */
function positionTooltip(menuItem, tooltip) {
    const rect = menuItem.getBoundingClientRect();
    tooltip.style.top = `${rect.top}px`;
}

/**
 * Update all tooltip positions
 */
function updateTooltipPositions() {
    const menuItems = document.querySelectorAll('.st-nav-item');
    
    menuItems.forEach(menuItem => {
        const tooltip = menuItem.querySelector('.st-nav-tooltip');
        if (tooltip) {
            positionTooltip(menuItem, tooltip);
        }
    });
}

/**
 * Initialize collapsible data cards
 */
function initializeDataCards() {
    const dataToggle = document.querySelectorAll('.st-data-toggle');
    
    dataToggle.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const card = this.closest('.st-data-card');
            const content = card.querySelector('.st-data-content');
            
            // Toggle collapsed state
            toggle.classList.toggle('collapsed');
            content.classList.toggle('collapsed');
            
            // Update any visualizations inside if needed
            window.dispatchEvent(new Event('resize'));
        });
    });
}

/**
 * Initialize Co-Pilot integration
 */
function initializeCopiloPanel() {
    const copilotToggle = document.querySelector('.st-copilot-toggle');
    const copilotPanel = document.querySelector('.st-copilot-panel');
    
    if (copilotToggle && copilotPanel) {
        copilotToggle.addEventListener('click', function() {
            copilotPanel.classList.toggle('active');
        });
        
        // Close when clicking outside
        document.addEventListener('click', function(event) {
            if (!copilotPanel.contains(event.target) && 
                !copilotToggle.contains(event.target) &&
                copilotPanel.classList.contains('active')) {
                copilotPanel.classList.remove('active');
            }
        });
    }
}