/**
 * Sustainability Co-Pilot JavaScript
 * Handles the client-side functionality for the Gemini-powered Sustainability Co-Pilot
 */

// Main Co-Pilot class
class SustainabilityCopilot {
    constructor() {
        // Configuration
        this.apiEndpoint = '/api/sustainability-copilot/query';
        this.suggestedPromptsEndpoint = '/api/sustainability-copilot/suggested-prompts';
        
        // State
        this.isOpen = false;
        this.isLoading = false;
        this.conversationId = null;
        this.context = 'general';
        this.page = window.location.pathname.replace('/', '');
        
        // Elements
        this.copilotPanel = null;
        this.copilotToggleButton = null;
        this.initElements();
        
        // Bind event handlers
        this.toggleCopilot = this.toggleCopilot.bind(this);
        this.submitQuery = this.submitQuery.bind(this);
        this.handleSuggestedPromptClick = this.handleSuggestedPromptClick.bind(this);
        
        // Initialize
        this.initialize();
    }
    
    // Create and initialize the Co-Pilot UI elements
    initElements() {
        // Create the Co-Pilot panel if it doesn't exist
        if (!document.getElementById('copilot-panel')) {
            const panel = document.createElement('div');
            panel.id = 'copilot-panel';
            panel.className = 'copilot-panel';
            panel.innerHTML = `
                <div class="copilot-header">
                    <div class="copilot-title">
                        <i class="bi bi-robot"></i>
                        <span>Sustainability Co-Pilot</span>
                    </div>
                    <button class="copilot-close-button" id="copilot-close">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <div class="copilot-content">
                    <div class="copilot-messages" id="copilot-messages">
                        <div class="copilot-welcome">
                            <h3>Welcome to the Sustainability Co-Pilot</h3>
                            <p>I'm here to help with all your sustainability intelligence needs. Ask me anything about sustainability metrics, trends, or reporting.</p>
                        </div>
                    </div>
                    <div class="copilot-suggested-prompts" id="copilot-suggested-prompts">
                        <div class="copilot-suggested-prompt">What are the current sustainability trends?</div>
                        <div class="copilot-suggested-prompt">How can we improve our carbon metrics?</div>
                        <div class="copilot-suggested-prompt">Explain ESG reporting requirements</div>
                    </div>
                </div>
                <div class="copilot-input">
                    <textarea id="copilot-query" placeholder="Ask me anything about sustainability..."></textarea>
                    <button id="copilot-submit">
                        <i class="bi bi-send"></i>
                    </button>
                </div>
            `;
            document.body.appendChild(panel);
            this.copilotPanel = panel;
            
            // Add event listeners
            document.getElementById('copilot-close').addEventListener('click', this.toggleCopilot);
            document.getElementById('copilot-submit').addEventListener('click', this.submitQuery);
            
            // Add event listener for Enter key in the textarea
            document.getElementById('copilot-query').addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.submitQuery();
                }
            });
            
            // Add event listeners for suggested prompts
            const suggestedPrompts = document.querySelectorAll('.copilot-suggested-prompt');
            suggestedPrompts.forEach(prompt => {
                prompt.addEventListener('click', this.handleSuggestedPromptClick);
            });
        } else {
            this.copilotPanel = document.getElementById('copilot-panel');
        }
    }
    
    // Initialize the Co-Pilot
    initialize() {
        // Load suggested prompts based on current page
        this.loadSuggestedPrompts();
        
        // Generate a new conversation ID if none exists
        if (!this.conversationId) {
            this.conversationId = 'conv-' + Date.now() + '-' + Math.floor(Math.random() * 9000 + 1000);
        }
    }
    
    // Toggle the Co-Pilot panel
    toggleCopilot() {
        if (this.isOpen) {
            this.copilotPanel.classList.remove('open');
        } else {
            this.copilotPanel.classList.add('open');
            // Refocus on input field
            setTimeout(() => {
                document.getElementById('copilot-query').focus();
            }, 300);
        }
        this.isOpen = !this.isOpen;
    }
    
    // Load suggested prompts from the server
    async loadSuggestedPrompts() {
        try {
            const promptsContainer = document.getElementById('copilot-suggested-prompts');
            
            // Show loading state
            promptsContainer.innerHTML = '<div class="copilot-loading">Loading suggestions...</div>';
            
            // Get prompts from API
            const response = await fetch(this.suggestedPromptsEndpoint + 
                `?context=${encodeURIComponent(this.context)}&page=${encodeURIComponent(this.page)}`);
                
            if (!response.ok) {
                throw new Error('Failed to load suggested prompts');
            }
            
            const data = await response.json();
            
            if (data.prompts && data.prompts.length > 0) {
                // Clear container
                promptsContainer.innerHTML = '';
                
                // Add new prompts
                data.prompts.forEach(prompt => {
                    const promptElement = document.createElement('div');
                    promptElement.className = 'copilot-suggested-prompt';
                    promptElement.textContent = prompt;
                    promptElement.addEventListener('click', this.handleSuggestedPromptClick);
                    promptsContainer.appendChild(promptElement);
                });
            } else {
                // Use fallback prompts
                promptsContainer.innerHTML = `
                    <div class="copilot-suggested-prompt">What are the current sustainability trends?</div>
                    <div class="copilot-suggested-prompt">How can we improve our carbon metrics?</div>
                    <div class="copilot-suggested-prompt">Explain ESG reporting requirements</div>
                `;
                
                // Re-add event listeners
                const suggestedPrompts = document.querySelectorAll('.copilot-suggested-prompt');
                suggestedPrompts.forEach(prompt => {
                    prompt.addEventListener('click', this.handleSuggestedPromptClick);
                });
            }
        } catch (error) {
            console.error('Error loading suggested prompts:', error);
            // Use fallback prompts on error
            const promptsContainer = document.getElementById('copilot-suggested-prompts');
            promptsContainer.innerHTML = `
                <div class="copilot-suggested-prompt">What are the current sustainability trends?</div>
                <div class="copilot-suggested-prompt">How can we improve our carbon metrics?</div>
                <div class="copilot-suggested-prompt">Explain ESG reporting requirements</div>
            `;
            
            // Re-add event listeners
            const suggestedPrompts = document.querySelectorAll('.copilot-suggested-prompt');
            suggestedPrompts.forEach(prompt => {
                prompt.addEventListener('click', this.handleSuggestedPromptClick);
            });
        }
    }
    
    // Handle click on a suggested prompt
    handleSuggestedPromptClick(event) {
        const prompt = event.target.textContent;
        document.getElementById('copilot-query').value = prompt;
        this.submitQuery();
    }
    
    // Submit a query to the Co-Pilot
    async submitQuery() {
        const queryInput = document.getElementById('copilot-query');
        const query = queryInput.value.trim();
        
        if (!query) return;
        
        try {
            // Show loading state
            this.isLoading = true;
            queryInput.disabled = true;
            document.getElementById('copilot-submit').disabled = true;
            
            // Add user message to the chat
            this.addMessage('user', query);
            
            // Clear input
            queryInput.value = '';
            
            // Send query to API
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query,
                    context: this.context,
                    page: this.page,
                    conversation_id: this.conversationId
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to get response from Co-Pilot');
            }
            
            const data = await response.json();
            
            // Add AI response to the chat
            this.addMessage('assistant', data.response, data.actions, data.facts);
            
            // Update conversation ID if provided
            if (data.conversation_id) {
                this.conversationId = data.conversation_id;
            }
        } catch (error) {
            console.error('Error submitting query:', error);
            // Show error message
            this.addMessage('assistant', 'Sorry, I encountered an error processing your request. Please try again.');
        } finally {
            // Reset loading state
            this.isLoading = false;
            queryInput.disabled = false;
            document.getElementById('copilot-submit').disabled = false;
            queryInput.focus();
        }
    }
    
    // Add a message to the chat
    addMessage(role, content, actions = [], facts = []) {
        const messagesContainer = document.getElementById('copilot-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `copilot-message copilot-${role}-message`;
        
        // Build message content
        let messageHtml = `<div class="copilot-message-content">${this.formatMessageContent(content)}</div>`;
        
        // Add facts if provided
        if (facts && facts.length > 0) {
            messageHtml += '<div class="copilot-facts">';
            messageHtml += '<h4>Key Facts</h4>';
            messageHtml += '<ul>';
            facts.forEach(fact => {
                messageHtml += `<li>${fact}</li>`;
            });
            messageHtml += '</ul>';
            messageHtml += '</div>';
        }
        
        // Add actions if provided
        if (actions && actions.length > 0) {
            messageHtml += '<div class="copilot-actions">';
            actions.forEach(action => {
                let actionUrl = '';
                let actionTarget = '';
                
                // Determine if action is internal or external
                if (action.action && action.action.startsWith('http')) {
                    actionUrl = action.action;
                    actionTarget = 'target="_blank"';
                } else if (action.action) {
                    actionUrl = action.action;
                }
                
                if (actionUrl) {
                    messageHtml += `<a href="${actionUrl}" ${actionTarget} class="copilot-action">${action.label}</a>`;
                } else {
                    messageHtml += `<div class="copilot-action">${action.label}</div>`;
                }
            });
            messageHtml += '</div>';
        }
        
        messageElement.innerHTML = messageHtml;
        
        // Remove welcome message if it exists
        const welcomeMessage = messagesContainer.querySelector('.copilot-welcome');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        // Add message to container
        messagesContainer.appendChild(messageElement);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Format message content with Markdown-like syntax
    formatMessageContent(content) {
        // Replace URLs with links
        let formattedContent = content.replace(
            /(https?:\/\/[^\s]+)/g, 
            '<a href="$1" target="_blank">$1</a>'
        );
        
        // Replace **bold** with <strong>
        formattedContent = formattedContent.replace(
            /\*\*(.*?)\*\*/g, 
            '<strong>$1</strong>'
        );
        
        // Replace *italic* with <em>
        formattedContent = formattedContent.replace(
            /\*(.*?)\*/g, 
            '<em>$1</em>'
        );
        
        // Replace new lines with <br>
        formattedContent = formattedContent.replace(/\n/g, '<br>');
        
        return formattedContent;
    }
}

// Initialize the Co-Pilot when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create a global instance
    window.copilotInstance = new SustainabilityCopilot();
    
    // Add event listeners to any copilot activation buttons
    const activationButtons = document.querySelectorAll('[id^="activate-copilot"]');
    activationButtons.forEach(button => {
        button.addEventListener('click', () => window.copilotInstance.toggleCopilot());
    });
});