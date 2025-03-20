# Strategy Hub Consolidation Documentation

## Overview
This directory used to contain multiple strategy-related templates including:
- strategy_hub.html
- ai_first_strategy_hub.html 
- strategy_modeler.html
- strategy_simulation.html

As part of the SustainaTrend™ platform consolidation, these have been replaced by the unified Enhanced Strategy Hub located at:
- Templates: `/frontend/templates/strategy/enhanced_strategy_hub.html`
- Route: `/enhanced-strategy-hub`

## Backward Compatibility

All previous strategy routes under `/strategy/*` now redirect to the Enhanced Strategy Hub for backward compatibility. This ensures that existing bookmarks and links continue to work.

## Key Features Now Available in Enhanced Strategy Hub

The Enhanced Strategy Hub combines all previous strategy functionality in a single, unified interface:

1. **Framework Selection & Analysis**: AI-driven framework selection from CSRD, SFDR, ESRS, etc.
2. **Document Processing**: Upload and analyze sustainability documents  
3. **Regulatory Compliance**: Automated assessment against major regulatory frameworks
4. **Monetization Strategy**: Business model recommendations for sustainability initiatives
5. **Trend Analysis**: Real-time analysis of sustainability trends and virality
6. **AI Strategy Advisor**: Agentic RAG-powered strategy recommendations

## Implementation Details

### Directory Structure
- `/frontend/templates/strategy/enhanced_strategy_hub.html` - Main template
- `/frontend/templates/strategy/components/` - Reusable UI components 
- `/frontend/routes/enhanced_strategy.py` - Route handlers
- `/frontend/routes/strategy.py` - Redirection handlers for backward compatibility

### Redirection Mechanism
The redirection is implemented in `frontend/routes/strategy.py` using Flask's `redirect()` and `url_for()` functions to point all legacy routes to the new Enhanced Strategy Hub.

## When to Use
Always use the Enhanced Strategy Hub at `/enhanced-strategy-hub` for any strategy-related functionality. The legacy routes are maintained only for backward compatibility.