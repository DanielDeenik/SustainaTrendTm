/**
 * Sustainability Co-Pilot Prompt Templates
 * 
 * This file contains structured prompt templates for the Gemini-powered Co-Pilot
 * to generate context-aware responses across different sections of the platform.
 * 
 * Each template includes:
 * - Base context information
 * - Required parameters for that route
 * - Suggested prompt structures
 * - Response formatting guidance
 */

const CopilotPromptTemplates = {
    /**
     * Dashboard context prompt template
     * Focus: Portfolio-wide sustainability metrics and insights
     */
    dashboard: {
        systemPrompt: `You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability intelligence.
You're currently helping with the main dashboard which shows portfolio-wide sustainability metrics.
Format your responses to be concise and action-oriented, focusing on insights rather than descriptions.
Include specific metrics when available and suggest concrete next steps.`,
        
        contextTemplate: {
            route: "dashboard",
            metrics: [], // Will be populated with current metrics
            trends: [],  // Will be populated with trend data
            timeframe: "quarterly", // Default timeframe
            comparisonPeriod: "previous_quarter",
            riskAreas: [], // Areas flagged for attention
            performanceAreas: [] // Areas showing positive performance
        },
        
        suggestedPrompts: [
            "What are my biggest sustainability risks right now?",
            "Which metrics have improved the most this quarter?",
            "What actions would have the biggest impact on our carbon footprint?",
            "How do our sustainability metrics compare to industry benchmarks?",
            "Which areas need immediate attention based on recent trends?"
        ],
        
        responseStructure: {
            summary: "Brief overview of current sustainability position",
            keyInsights: [], // 3-5 bullet points of specific insights
            recommendedActions: [], // 2-3 concrete next steps
            relevantMetrics: [], // Any metrics specifically relevant to the query
            visualizations: [] // Any charts/graphs recommended
        }
    },

    /**
     * Real Estate context prompt template
     * Focus: Property-specific performance and sustainable building metrics
     */
    real_estate: {
        systemPrompt: `You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in real estate sustainability.
You're currently helping with the real estate portfolio view which shows property-specific environmental performance.
Focus on practical building improvements, energy efficiency, certification paths, and financial benefits of sustainable practices.
Provide specific, actionable recommendations relevant to property types in the portfolio.`,
        
        contextTemplate: {
            route: "real_estate",
            propertyCount: 0,
            epcDistribution: {}, // Energy Performance Certificate distribution
            propertyTypes: [], // Commercial, residential, mixed-use, etc.
            topPerformers: [], // Best performing properties
            metrics: [], // Property metrics (energy, water, waste, etc.)
            regions: [], // Geographic regions of properties
            certifications: [], // BREEAM, LEED, etc.
            regulatoryRisks: [] // Upcoming regulations affecting properties
        },
        
        suggestedPrompts: [
            "Which properties need EPC upgrades to meet 2028 regulations?",
            "What's the ROI on solar installation for our A-rated buildings?",
            "How can we improve water efficiency across our residential portfolio?",
            "Which sustainable features deliver the best rental premium?",
            "What are the carbon reduction opportunities for our office buildings?"
        ],
        
        responseStructure: {
            summary: "Brief overview of property portfolio sustainability status",
            propertyInsights: [], // Specific insights about property performance
            improvementOpportunities: [], // Concrete improvement suggestions
            regulatoryConsiderations: [], // Relevant regulations and compliance
            financialBenefits: [], // Financial benefits of suggested improvements
            certificationPathways: [] // Potential sustainability certifications
        }
    },

    /**
     * Trend Analysis context prompt template
     * Focus: Market trends, emerging themes, and predictive insights
     */
    trend_analysis: {
        systemPrompt: `You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability trend analysis.
You're currently helping with the trend analysis view which tracks emerging sustainability themes and market trends.
Focus on identifying patterns, predicting future developments, and connecting trends to strategic opportunities.
Highlight emerging risks, market sentiment shifts, and competitive intelligence.`,
        
        contextTemplate: {
            route: "trend_analysis",
            currentTrends: [], // Active sustainability trends
            emergingThemes: [], // Newly detected themes
            industryShifts: [], // Major shifts in industry approaches
            regulatoryHorizon: [], // Upcoming regulatory changes
            consumerSentiment: {}, // Consumer sentiment metrics
            competitorMoves: [], // Recent competitor sustainability initiatives
            marketOpportunities: [] // Market opportunities identified
        },
        
        suggestedPrompts: [
            "What sustainability trends are gaining momentum this quarter?",
            "How is consumer sentiment changing around carbon transparency?",
            "What regulatory changes should we prepare for in the next 18 months?",
            "Which emerging sustainability technologies should we monitor?",
            "What competitive advantage could we gain from current market trends?"
        ],
        
        responseStructure: {
            summary: "Brief overview of current sustainability trend landscape",
            keyTrends: [], // 3-5 most relevant trends to focus on
            emergingOpportunities: [], // Market opportunities based on trends
            competitiveLandscape: [], // Competitor positioning
            strategicRecommendations: [], // Strategic moves to consider
            trendProjections: [] // How trends might develop in coming periods
        }
    },

    /**
     * Document Analysis context prompt template
     * Focus: Sustainability report analysis, compliance verification, and insight extraction
     */
    document_analysis: {
        systemPrompt: `You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability document analysis.
You're currently helping with the document analysis view which examines sustainability reports and ESG disclosures.
Focus on extracting key metrics, evaluating compliance with reporting frameworks, and identifying gaps or opportunities.
Provide insights on report quality, completeness, and comparability to industry standards.`,
        
        contextTemplate: {
            route: "document_analysis",
            documentType: "", // Sustainability report, ESG disclosure, etc.
            documentDate: "", // Publication date
            organization: "", // Document owner/organization
            frameworks: [], // Frameworks referenced (GRI, SASB, TCFD, etc.)
            keyMetrics: {}, // Extracted sustainability metrics
            textLength: 0, // Document size
            analysisComplete: false, // Analysis status
            complianceScore: 0 // Overall compliance score
        },
        
        suggestedPrompts: [
            "What are the key sustainability metrics in this report?",
            "Does this report comply with TCFD recommendations?",
            "What disclosures are missing compared to GRI standards?",
            "How does this company's carbon reporting compare to industry peers?",
            "What sustainability goals has this organization committed to?"
        ],
        
        responseStructure: {
            summary: "Brief overview of the document's sustainability content",
            keyDisclosures: [], // Important disclosures identified
            complianceAnalysis: [], // Analysis of framework compliance
            metricHighlights: [], // Key metrics extracted
            dataGaps: [], // Missing information or disclosures
            qualityAssessment: [], // Assessment of report quality
            comparativeInsights: [] // How it compares to standards or peers
        }
    },

    /**
     * Sustainability Stories context prompt template
     * Focus: Converting sustainability data into compelling narratives
     */
    stories: {
        systemPrompt: `You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability storytelling.
You're currently helping with the sustainability stories view which transforms data into compelling narratives.
Focus on creating impactful, accurate, and engaging stories that effectively communicate sustainability progress.
Suggest narrative structures, key message points, and suitable data visualizations.`,
        
        contextTemplate: {
            route: "stories",
            storyTopics: [], // Available sustainability story topics
            availableMetrics: [], // Metrics that can be included
            audienceTypes: [], // Target audiences (investors, customers, etc.)
            communicationChannels: [], // Where stories will be shared
            brandValues: [], // Organization's sustainability values
            previousStories: [], // Recently created stories
            performanceHighlights: [] // Notable achievements to feature
        },
        
        suggestedPrompts: [
            "How can we tell our carbon reduction story to investors?",
            "What's the most impactful way to communicate our water conservation progress?",
            "Can you suggest a storytelling approach for our supply chain transparency?",
            "How should we frame our renewable energy transition for customers?",
            "What visualization would best communicate our progress toward net zero?"
        ],
        
        responseStructure: {
            summary: "Brief overview of the storytelling opportunity",
            narrativeStructure: [], // Suggested story structure
            keyMessages: [], // Core messages to emphasize
            dataPoints: [], // Specific data to include
            visualizationIdeas: [], // Recommended visualization approaches
            audienceConsiderations: [], // Tailoring for specific audiences
            impactEnhancement: [] // Ways to maximize story impact
        }
    },

    /**
     * Search context prompt template
     * Focus: Helping users find relevant sustainability information and resources
     */
    search: {
        systemPrompt: `You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability information retrieval.
You're currently helping with the search view which helps users find relevant sustainability information and resources.
Focus on understanding search intent, suggesting relevant filters, and providing context for search results.
Help users refine their searches and connect them to the most valuable resources.`,
        
        contextTemplate: {
            route: "search",
            searchQuery: "", // Current search terms
            searchFilters: {}, // Applied filters
            resultCount: 0, // Number of results found
            topCategories: [], // Categories in results
            recentSearches: [], // User's recent searches
            popularSearches: [], // Platform-wide popular searches
            relatedConcepts: [] // Concepts related to the search
        },
        
        suggestedPrompts: [
            "Can you help me find resources on science-based targets?",
            "What's the difference between Scope 1 and Scope 2 emissions?",
            "How do I find case studies on water reduction strategies?",
            "What are the best resources for understanding CSRD requirements?",
            "Can you explain what these search results about ESG ratings mean?"
        ],
        
        responseStructure: {
            summary: "Brief interpretation of search intent",
            keyDefinitions: [], // Definitions of searched terms if needed
            resourceSuggestions: [], // Specific resources to explore
            searchRefinements: [], // Ways to improve the search
            conceptExplanations: [], // Explanations of complex concepts
            relatedTopics: [] // Related areas to explore
        }
    },

    /**
     * ESRS context prompt template
     * Focus: European Sustainability Reporting Standards compliance and guidance
     */
    esrs: {
        systemPrompt: `You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in ESRS compliance.
You're currently helping with the ESRS framework view which guides organizations on compliance with European Sustainability Reporting Standards.
Focus on practical implementation guidance, disclosure requirements, and compliance strategies.
Provide specific, actionable insights tailored to the organization's context and reporting maturity.`,
        
        contextTemplate: {
            route: "esrs",
            applicableStandards: [], // Relevant ESRS standards
            organizationSize: "", // Company size category
            industryClassification: "", // Industry sector
            currentCompliance: {}, // Compliance status by standard
            reportingTimeline: "", // Implementation timeline
            materialityAssessment: {}, // Results of materiality assessment
            dataReadiness: {} // Data availability for required disclosures
        },
        
        suggestedPrompts: [
            "What ESRS disclosures are mandatory for our industry?",
            "How do we conduct a double materiality assessment?",
            "What's the implementation timeline for ESRS E1?",
            "What data gaps do we need to address for ESRS S1 compliance?",
            "How does ESRS relate to other frameworks like GRI and TCFD?"
        ],
        
        responseStructure: {
            summary: "Brief overview of ESRS relevance to the organization",
            keyRequirements: [], // Essential requirements to focus on
            implementationSteps: [], // Practical implementation guidance
            complianceTimeline: [], // Critical deadlines and phases
            dataRequirements: [], // Data needed for compliance
            resourceSuggestions: [], // Helpful resources
            strategyRecommendations: [] // Strategic approach to compliance
        }
    },

    /**
     * General context prompt template
     * Fallback for pages without specific contexts
     */
    general: {
        systemPrompt: `You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability intelligence.
You provide knowledgeable, practical guidance on sustainability topics across environmental, social, and governance domains.
Keep responses concise, factual, and practical with a focus on actionable insights.
When appropriate, suggest relevant areas of the platform to explore for more detailed information.`,
        
        contextTemplate: {
            route: "general",
            platform_areas: [
                "dashboard", "real_estate", "trend_analysis", 
                "document_analysis", "stories", "search", "esrs"
            ],
            user_role: "", // If known
            recent_activity: [] // Recent user activity if available
        },
        
        suggestedPrompts: [
            "What sustainability reporting frameworks should I know about?",
            "How can I get started with carbon footprint measurement?",
            "What are the key aspects of the EU Green Deal?",
            "How does climate risk affect financial reporting?",
            "What are science-based targets and why are they important?"
        ],
        
        responseStructure: {
            summary: "Brief overview of the requested information",
            keyPoints: [], // Core information addressing the query
            relevantContext: [], // Related sustainability context
            practicalApplication: [], // How to apply this information
            platformSuggestions: [], // Relevant areas of the platform to explore
            furtherResources: [] // Additional resources if appropriate
        }
    }
};

/**
 * Helper function to get the appropriate prompt template based on context
 * @param {string} context - The current application context
 * @returns {Object} The prompt template for the given context
 */
function getPromptTemplate(context) {
    return CopilotPromptTemplates[context] || CopilotPromptTemplates.general;
}

/**
 * Generates a customized system prompt with context-specific information
 * @param {string} context - The current application context
 * @param {Object} contextData - Dynamic context data from the current view
 * @returns {string} A customized system prompt
 */
function generateSystemPrompt(context, contextData = {}) {
    const template = getPromptTemplate(context);
    
    // Start with the base system prompt
    let systemPrompt = template.systemPrompt;
    
    // Add context-specific details if available
    if (contextData && Object.keys(contextData).length > 0) {
        systemPrompt += "\n\nCurrent context information:";
        
        // Add relevant context information based on available data
        Object.keys(contextData).forEach(key => {
            // Skip empty arrays or objects
            if (Array.isArray(contextData[key]) && contextData[key].length === 0) return;
            if (typeof contextData[key] === 'object' && Object.keys(contextData[key]).length === 0) return;
            
            // Add the context data in a readable format
            if (typeof contextData[key] === 'object') {
                systemPrompt += `\n- ${key}: ${JSON.stringify(contextData[key])}`;
            } else {
                systemPrompt += `\n- ${key}: ${contextData[key]}`;
            }
        });
    }
    
    return systemPrompt;
}

/**
 * Gets suggested prompts for the current context
 * @param {string} context - The current application context
 * @returns {Array} List of suggested prompts for this context
 */
function getSuggestedPrompts(context) {
    const template = getPromptTemplate(context);
    return template.suggestedPrompts || [];
}

// Export the functions and templates
window.CopilotPromptTemplates = CopilotPromptTemplates;
window.getPromptTemplate = getPromptTemplate;
window.generateSystemPrompt = generateSystemPrompt;
window.getSuggestedPrompts = getSuggestedPrompts;

// Also export as module exports for ES modules
export {
    CopilotPromptTemplates,
    getPromptTemplate,
    generateSystemPrompt,
    getSuggestedPrompts
};