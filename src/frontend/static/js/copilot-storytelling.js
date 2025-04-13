/**
 * Sustainability Co-Pilot - Storytelling Integration
 * 
 * This module connects the Sustainability Co-Pilot with the storytelling functionality,
 * enabling users to create sustainability stories from Co-Pilot suggestions and prompts.
 */

// Define the storytelling connection functions in global scope for browser compatibility
window.SustainabilityCopilotStorytelling = {
    /**
     * Activate storytelling with specified category and prompt
     * This function initiates storytelling based on Co-Pilot interaction
     * 
     * @param {string} category - Sustainability category (emissions, water, waste, energy, social, governance)
     * @param {string} prompt - User prompt or question from Co-Pilot
     * @param {Object} options - Additional options (metrics, audience, etc.)
     */
    activateStorytelling: function(category = 'emissions', prompt = '', options = {}) {
        console.log('Activating storytelling with category:', category, 'prompt:', prompt, 'options:', options);
        
        // Default values
        const defaults = {
            audience: 'general',
            metrics: [],
            includeRecommendations: true,
            includeVisualizations: true
        };
        
        // Merge options with defaults
        const settings = Object.assign({}, defaults, options);
        
        // Build the URL for storytelling page with parameters
        let url = '/enhanced-strategy/stories/create?';
        
        // Add category parameter
        url += `category=${encodeURIComponent(category)}`;
        
        // Add audience parameter
        url += `&audience=${encodeURIComponent(settings.audience)}`;
        
        // Add prompt as additional context if provided
        if (prompt && prompt.trim() !== '') {
            url += `&prompt=${encodeURIComponent(prompt)}`;
        }
        
        // Add selected metrics if provided
        if (settings.metrics && settings.metrics.length > 0) {
            url += `&metrics=${encodeURIComponent(JSON.stringify(settings.metrics))}`;
        }
        
        // Add sections to include
        if (settings.includeRecommendations) {
            url += '&include_recommendations=true';
        }
        
        if (settings.includeVisualizations) {
            url += '&include_visualizations=true';
        }
        
        // Navigate to the storytelling page
        window.location.href = url;
    },
    
    /**
     * Process a Co-Pilot prompt for storytelling
     * Analyzes the prompt to determine the appropriate storytelling parameters
     * 
     * @param {string} prompt - The user's prompt from the Co-Pilot
     * @returns {Object} Storytelling parameters (category, audience, etc.)
     */
    processCopilotPrompt: function(prompt) {
        if (!prompt) return null;
        
        prompt = prompt.toLowerCase();
        
        // Extract category from prompt
        let category = 'general';
        
        // Check for category keywords in prompt
        if (prompt.includes('carbon') || prompt.includes('emissions') || prompt.includes('ghg') || 
            prompt.includes('greenhouse') || prompt.includes('climate')) {
            category = 'emissions';
        } else if (prompt.includes('water') || prompt.includes('ocean') || prompt.includes('marine')) {
            category = 'water';
        } else if (prompt.includes('waste') || prompt.includes('circular') || prompt.includes('recycling')) {
            category = 'waste';
        } else if (prompt.includes('energy') || prompt.includes('renewable') || prompt.includes('efficiency')) {
            category = 'energy';
        } else if (prompt.includes('social') || prompt.includes('diversity') || prompt.includes('equity') || 
                  prompt.includes('inclusion') || prompt.includes('community')) {
            category = 'social';
        } else if (prompt.includes('governance') || prompt.includes('compliance') || 
                  prompt.includes('board') || prompt.includes('ethics')) {
            category = 'governance';
        }
        
        // Extract audience from prompt
        let audience = 'general';
        if (prompt.includes('investor') || prompt.includes('shareholders')) {
            audience = 'investors';
        } else if (prompt.includes('customer') || prompt.includes('consumer')) {
            audience = 'customers';
        } else if (prompt.includes('employee') || prompt.includes('staff')) {
            audience = 'employees';
        } else if (prompt.includes('regulator') || prompt.includes('government')) {
            audience = 'regulators';
        }
        
        // Determine if metrics are requested
        const includeMetrics = prompt.includes('metrics') || prompt.includes('kpi') || 
                            prompt.includes('data') || prompt.includes('numbers');
                            
        // Determine if visualizations are requested
        const includeVisualizations = prompt.includes('visual') || prompt.includes('chart') || 
                                   prompt.includes('graph') || prompt.includes('dashboard');
        
        return {
            category,
            audience,
            prompt,
            includeMetrics,
            includeVisualizations
        };
    },
    
    /**
     * Create a story directly from the Co-Pilot interface
     * 
     * @param {string} prompt - The user's prompt from the Co-Pilot
     */
    createStoryFromCopilot: function(prompt) {
        // Process the prompt to determine storytelling parameters
        const params = this.processCopilotPrompt(prompt);
        
        // Activate storytelling with the processed parameters
        this.activateStorytelling(
            params.category, 
            prompt, 
            {
                audience: params.audience,
                includeRecommendations: true,
                includeVisualizations: params.includeVisualizations
            }
        );
    },
    
    /**
     * Handle story creation button clicks from the Co-Pilot interface
     * 
     * @param {Event} event - The click event
     */
    handleCreateStoryClick: function(event) {
        // Prevent default button behavior
        event.preventDefault();
        
        // Get the prompt from the copilot input field
        const promptInput = document.getElementById('copilot-query');
        if (!promptInput) return;
        
        const prompt = promptInput.value.trim();
        if (!prompt) {
            alert('Please enter a prompt to create a story');
            return;
        }
        
        // Create story from the prompt
        this.createStoryFromCopilot(prompt);
    }
};

// Initialize the integration when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a page with the Co-Pilot
    const copilotPanel = document.getElementById('copilot-panel');
    if (!copilotPanel) return;
    
    // Add a "Create Story" button to the Co-Pilot panel
    const copilotInput = document.querySelector('.copilot-input');
    if (copilotInput) {
        const createStoryButton = document.createElement('button');
        createStoryButton.id = 'copilot-create-story';
        createStoryButton.className = 'copilot-action-button';
        createStoryButton.title = 'Create sustainability story from this prompt';
        createStoryButton.innerHTML = '<i class="bi bi-file-earmark-text"></i>';
        
        // Add event listener
        createStoryButton.addEventListener('click', function(e) {
            window.SustainabilityCopilotStorytelling.handleCreateStoryClick(e);
        });
        
        // Insert before the submit button
        const submitButton = document.getElementById('copilot-submit');
        if (submitButton) {
            copilotInput.insertBefore(createStoryButton, submitButton);
        } else {
            copilotInput.appendChild(createStoryButton);
        }
    }
    
    // Add suggested prompts for storytelling if they don't exist
    const suggestedPromptsContainer = document.getElementById('copilot-suggested-prompts');
    if (suggestedPromptsContainer) {
        let hasStoryPrompt = false;
        
        // Check if there's already a storytelling-related prompt
        const existingPrompts = suggestedPromptsContainer.querySelectorAll('.copilot-suggested-prompt');
        existingPrompts.forEach(prompt => {
            if (prompt.textContent.toLowerCase().includes('story')) {
                hasStoryPrompt = true;
            }
        });
        
        // Add a storytelling prompt if none exists
        if (!hasStoryPrompt) {
            // Add two story prompts
            const storyPrompt1 = document.createElement('div');
            storyPrompt1.className = 'copilot-suggested-prompt';
            storyPrompt1.textContent = 'Create a sustainability story from our emissions data';
            storyPrompt1.addEventListener('click', function() {
                const input = document.getElementById('copilot-query');
                if (input) {
                    input.value = this.textContent;
                    // Trigger the create story function
                    window.SustainabilityCopilotStorytelling.handleCreateStoryClick(new Event('click'));
                }
            });
            
            const storyPrompt2 = document.createElement('div');
            storyPrompt2.className = 'copilot-suggested-prompt';
            storyPrompt2.textContent = 'Suggest metrics for my carbon reduction story...';
            storyPrompt2.addEventListener('click', function() {
                const input = document.getElementById('copilot-query');
                if (input) {
                    input.value = this.textContent;
                    // Trigger the create story function
                    window.SustainabilityCopilotStorytelling.handleCreateStoryClick(new Event('click'));
                }
            });
            
            suggestedPromptsContainer.appendChild(storyPrompt1);
            suggestedPromptsContainer.appendChild(storyPrompt2);
        }
    }
    
    console.log('Sustainability Co-Pilot Storytelling integration initialized');
});