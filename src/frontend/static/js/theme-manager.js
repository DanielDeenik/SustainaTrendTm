/**
 * SustainaTrend™ Theme Manager
 * Handles theme switching and persistence for the SustainaTrend™ platform
 */

class ThemeManager {
  constructor() {
    this.themeKey = 'sustainatrend-theme';
    this.defaultTheme = 'light';
    this.currentTheme = this.getSavedTheme();
    this.toggleButton = document.getElementById('darkModeToggle');
    
    this.init();
  }
  
  /**
   * Initialize the theme manager
   */
  init() {
    // Apply saved theme on load
    this.applyTheme(this.currentTheme);
    
    // Set up event listeners
    if (this.toggleButton) {
      this.toggleButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleTheme();
      });
      
      // Update toggle button icon
      this.updateToggleIcon();
    }
    
    // Listen for OS theme changes
    this.setupMediaQueryListener();
  }
  
  /**
   * Get the currently saved theme or use system preference
   */
  getSavedTheme() {
    const savedTheme = localStorage.getItem(this.themeKey);
    
    if (savedTheme) {
      return savedTheme;
    }
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return this.defaultTheme;
  }
  
  /**
   * Apply a theme to the document
   */
  applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    this.currentTheme = theme;
    localStorage.setItem(this.themeKey, theme);
    
    // Update toggle button if it exists
    if (this.toggleButton) {
      this.updateToggleIcon();
    }
    
    // Dispatch event for components that need to react to theme changes
    document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
  }
  
  /**
   * Toggle between light and dark theme
   */
  toggleTheme() {
    const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    this.applyTheme(newTheme);
  }
  
  /**
   * Update the toggle button icon based on current theme
   */
  updateToggleIcon() {
    const icon = this.toggleButton.querySelector('i');
    
    if (this.currentTheme === 'dark') {
      icon.classList.remove('bi-moon');
      icon.classList.add('bi-sun');
      this.toggleButton.setAttribute('title', 'Switch to light mode');
    } else {
      icon.classList.remove('bi-sun');
      icon.classList.add('bi-moon');
      this.toggleButton.setAttribute('title', 'Switch to dark mode');
    }
  }
  
  /**
   * Set up listener for OS theme changes
   */
  setupMediaQueryListener() {
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      mediaQuery.addEventListener('change', (e) => {
        // Only change if user hasn't explicitly set a preference
        if (!localStorage.getItem(this.themeKey)) {
          this.applyTheme(e.matches ? 'dark' : 'light');
        }
      });
    }
  }
}

// Initialize theme manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.themeManager = new ThemeManager();
});