/**
 * SustainaTrend™ Atomic Design System Core JavaScript
 * Contains shared functionality for consistent behavior across components
 */

(function() {
  // Initialize when DOM is fully loaded
  document.addEventListener('DOMContentLoaded', function() {
    initThemeToggle();
    initSidebar();
    initMobileMenu();
    initNavigationControls();
    initNotifications();
    initTooltips();
    initTabNavigation();
    initDropdowns();
    initAtomicNavigation();
  });

  /**
   * Initialize theme toggle functionality
   */
  function initThemeToggle() {
    const themeToggle = document.querySelector('.st-theme-toggle');
    const htmlElement = document.documentElement;
    
    if (!themeToggle) return;
    
    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      htmlElement.setAttribute('data-theme', savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      htmlElement.setAttribute('data-theme', 'dark');
    }
    
    // Toggle theme
    themeToggle.addEventListener('click', function() {
      const currentTheme = htmlElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      htmlElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
    });
  }

  /**
   * Initialize sidebar functionality
   */
  function initSidebar() {
    const sidebarToggle = document.querySelector('.st-sidebar-toggle');
    const appContainer = document.querySelector('.st-app-container');
    
    if (!sidebarToggle || !appContainer) return;
    
    // Check for saved sidebar state
    const sidebarCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    if (sidebarCollapsed) {
      appContainer.classList.add('st-sidebar-collapsed');
    }
    
    // Toggle sidebar
    sidebarToggle.addEventListener('click', function() {
      appContainer.classList.toggle('st-sidebar-collapsed');
      localStorage.setItem('sidebar-collapsed', appContainer.classList.contains('st-sidebar-collapsed'));
    });
  }

  /**
   * Initialize mobile menu functionality
   */
  function initMobileMenu() {
    // Create mobile menu button if it doesn't exist
    if (!document.querySelector('.st-mobile-menu-toggle')) {
      const mobileMenuButton = document.createElement('button');
      mobileMenuButton.className = 'st-mobile-menu-toggle';
      mobileMenuButton.setAttribute('aria-label', 'Toggle navigation menu');
      mobileMenuButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="18" x2="20" y2="18"/></svg>';
      
      const topbar = document.querySelector('.st-topbar');
      if (topbar) {
        topbar.insertBefore(mobileMenuButton, topbar.firstChild);
      }
    }
    
    const mobileMenuButton = document.querySelector('.st-mobile-menu-toggle');
    const sidebar = document.querySelector('.st-sidebar');
    
    if (!mobileMenuButton || !sidebar) return;
    
    mobileMenuButton.addEventListener('click', function() {
      sidebar.classList.toggle('open');
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
      if (window.innerWidth <= 768 && 
          sidebar.classList.contains('open') && 
          !sidebar.contains(event.target) && 
          !mobileMenuButton.contains(event.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  /**
   * Initialize navigation controls
   */
  function initNavigationControls() {
    const backButton = document.querySelector('.st-navigation-controls button:first-child');
    const forwardButton = document.querySelector('.st-navigation-controls button:last-child');
    
    if (!backButton || !forwardButton) return;
    
    backButton.addEventListener('click', function() {
      window.history.back();
    });
    
    forwardButton.addEventListener('click', function() {
      window.history.forward();
    });
  }

  /**
   * Initialize notifications
   */
  function initNotifications() {
    const notificationButton = document.querySelector('.st-action-button[aria-label="Notifications"]');
    
    if (!notificationButton) return;
    
    notificationButton.addEventListener('click', function() {
      // In a real implementation, this would toggle a notifications panel
      alert('Notifications panel would appear here');
    });
  }

  /**
   * Initialize tooltips
   */
  function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
      element.addEventListener('mouseenter', function() {
        const tooltipText = this.getAttribute('data-tooltip');
        
        const tooltip = document.createElement('div');
        tooltip.className = 'st-tooltip';
        tooltip.textContent = tooltipText;
        
        document.body.appendChild(tooltip);
        
        const rect = this.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        tooltip.classList.add('visible');
        
        this.addEventListener('mouseleave', function() {
          tooltip.remove();
        }, { once: true });
      });
    });
  }

  /**
   * Initialize tab navigation
   */
  function initTabNavigation() {
    const tabs = document.querySelectorAll('.st-tab');
    
    tabs.forEach(tab => {
      tab.addEventListener('click', function(event) {
        // If this is an anchor tab (href="#some-id"), prevent default and handle manually
        if (this.getAttribute('href').startsWith('#')) {
          event.preventDefault();
          
          // Remove active class from all tabs
          tabs.forEach(t => t.classList.remove('active'));
          
          // Add active class to clicked tab
          this.classList.add('active');
          
          // Show the corresponding tab content
          const tabContentId = this.getAttribute('href').substring(1);
          const tabContents = document.querySelectorAll('.st-tab-content');
          
          tabContents.forEach(content => {
            content.style.display = content.id === tabContentId ? 'block' : 'none';
          });
        }
      });
    });
  }

  /**
   * Initialize dropdowns
   */
  function initDropdowns() {
    const dropdownToggles = document.querySelectorAll('.st-dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
      toggle.addEventListener('click', function() {
        const dropdown = this.nextElementSibling;
        
        if (dropdown && dropdown.classList.contains('st-dropdown-menu')) {
          dropdown.classList.toggle('show');
          
          // Close when clicking outside
          const closeDropdown = function(event) {
            if (!toggle.contains(event.target) && !dropdown.contains(event.target)) {
              dropdown.classList.remove('show');
              document.removeEventListener('click', closeDropdown);
            }
          };
          
          document.addEventListener('click', closeDropdown);
        }
      });
    });
  }

  /**
   * Initialize search functionality
   * @param {string} searchInputId - ID of the search input element
   * @param {Function} searchCallback - Callback function to handle search
   */
  window.initSearch = function(searchInputId, searchCallback) {
    const searchInput = document.getElementById(searchInputId);
    
    if (!searchInput) return;
    
    // Handle search input
    searchInput.addEventListener('keyup', function(event) {
      if (event.key === 'Enter') {
        const query = this.value.trim();
        
        if (query && typeof searchCallback === 'function') {
          searchCallback(query);
        } else {
          // Default behavior if no callback provided
          window.location.href = '/search?q=' + encodeURIComponent(query);
        }
      }
    });
    
    // Handle voice search
    const voiceButton = searchInput.parentElement.querySelector('.st-voice-search-button');
    
    if (voiceButton) {
      voiceButton.addEventListener('click', function() {
        if ('webkitSpeechRecognition' in window) {
          const recognition = new webkitSpeechRecognition();
          recognition.continuous = false;
          recognition.interimResults = false;
          
          recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            searchInput.value = transcript;
            
            if (typeof searchCallback === 'function') {
              searchCallback(transcript);
            } else {
              // Default behavior if no callback provided
              window.location.href = '/search?q=' + encodeURIComponent(transcript);
            }
          };
          
          recognition.start();
        } else {
          alert('Voice search is not supported in this browser');
        }
      });
    }
  };

  /**
   * Format number with abbreviation for large values (K, M, B)
   * @param {number} num - Number to format
   * @returns {string} Formatted number with appropriate suffix
   */
  window.formatNumberWithAbbreviation = function(num) {
    if (num >= 1000000000) {
      return (num / 1000000000).toFixed(1) + 'B';
    }
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  /**
   * Format date as relative time (e.g., "2 days ago")
   * @param {Date|string} date - Date to format
   * @returns {string} Relative time string
   */
  window.formatRelativeTime = function(date) {
    const now = new Date();
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const diffMs = now - dateObj;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    const diffMonth = Math.floor(diffDay / 30);
    const diffYear = Math.floor(diffMonth / 12);
    
    if (diffYear > 0) {
      return diffYear === 1 ? '1 year ago' : diffYear + ' years ago';
    }
    if (diffMonth > 0) {
      return diffMonth === 1 ? '1 month ago' : diffMonth + ' months ago';
    }
    if (diffDay > 0) {
      return diffDay === 1 ? '1 day ago' : diffDay + ' days ago';
    }
    if (diffHour > 0) {
      return diffHour === 1 ? '1 hour ago' : diffHour + ' hours ago';
    }
    if (diffMin > 0) {
      return diffMin === 1 ? '1 minute ago' : diffMin + ' minutes ago';
    }
    return 'Just now';
  };
  
  /**
   * Initialize navigation between atomic design system pages
   * This ensures consistent navigation across all atomic design pages
   */
  function initAtomicNavigation() {
    // Navigation links in the sidebar
    const atomicHomeLink = document.querySelector('.st-sidebar-nav-link[href="/atomic-home"]');
    const atomicTrendsLink = document.querySelector('.st-sidebar-nav-link[href="/trend-analysis-atomic"]');
    const atomicStoriesLink = document.querySelector('.st-sidebar-nav-link[href="/sustainability-stories-atomic"]');
    
    // Create page registry with routes and names
    const atomicPageRegistry = [
      { route: '/atomic-home', name: 'Home', icon: 'home' },
      { route: '/trend-analysis-atomic', name: 'Trend Analysis', icon: 'bar-chart-2' },
      { route: '/sustainability-stories-atomic', name: 'Sustainability Stories', icon: 'book-open' }
    ];
    
    // Populate quick navigation if it exists
    const quickNav = document.querySelector('.st-quick-nav');
    if (quickNav) {
      // Clear existing items
      while (quickNav.firstChild) {
        quickNav.removeChild(quickNav.firstChild);
      }
      
      // Add atomic pages to quick navigation
      atomicPageRegistry.forEach(page => {
        const navItem = document.createElement('a');
        navItem.href = page.route;
        navItem.className = 'st-quick-nav-item';
        navItem.setAttribute('data-tooltip', page.name);
        
        // Add icon
        navItem.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-${page.icon}"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`;
        
        // Highlight current page
        if (window.location.pathname === page.route) {
          navItem.classList.add('active');
        }
        
        quickNav.appendChild(navItem);
      });
    }
    
    // Add "View Atomic Design" button to non-atomic pages if not on an atomic page
    if (!window.location.pathname.includes('-atomic')) {
      const topbar = document.querySelector('.st-topbar-actions');
      if (topbar && !document.querySelector('.st-atomic-view-button')) {
        const atomicButton = document.createElement('button');
        atomicButton.className = 'st-button st-button--outline st-atomic-view-button';
        atomicButton.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <circle cx="12" cy="12" r="4"/>
            <line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/>
            <line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/>
            <line x1="14.83" y1="9.17" x2="19.07" y2="4.93"/>
            <line x1="4.93" y1="19.07" x2="9.17" y2="14.83"/>
          </svg>
          View Atomic Design
        `;
        
        atomicButton.addEventListener('click', function() {
          window.location.href = '/atomic-home';
        });
        
        topbar.appendChild(atomicButton);
      }
    }
    
    // Create a DOM navigation panel for jumping between atomic pages
    if (window.location.pathname.includes('-atomic')) {
      const mainContent = document.querySelector('.st-main-content');
      if (mainContent && !document.querySelector('.st-atomic-nav-panel')) {
        const navPanel = document.createElement('div');
        navPanel.className = 'st-atomic-nav-panel';
        navPanel.innerHTML = `
          <div class="st-atomic-nav-title">Atomic Design Pages</div>
          <div class="st-atomic-nav-items"></div>
        `;
        
        const navItems = navPanel.querySelector('.st-atomic-nav-items');
        
        // Add page links
        atomicPageRegistry.forEach(page => {
          const navItem = document.createElement('a');
          navItem.href = page.route;
          navItem.className = 'st-atomic-nav-item';
          
          // Check if this is the current page
          if (window.location.pathname === page.route) {
            navItem.classList.add('active');
          }
          
          navItem.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-${page.icon}"></svg>
            <span>${page.name}</span>
          `;
          
          navItems.appendChild(navItem);
        });
        
        // Add the panel after the breadcrumbs
        const breadcrumbs = mainContent.querySelector('.st-breadcrumbs');
        if (breadcrumbs) {
          breadcrumbs.parentNode.insertBefore(navPanel, breadcrumbs.nextSibling);
        } else {
          mainContent.insertBefore(navPanel, mainContent.firstChild);
        }
      }
    }
  }
})();