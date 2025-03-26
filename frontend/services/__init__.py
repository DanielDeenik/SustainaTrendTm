"""
Services Module for SustainaTrend™ Intelligence Platform

This package contains core service modules that provide shared functionality
across different parts of the application.
"""

# Import services for easy access
try:
    from .ai_connector import (
        connect_to_ai_services,
        is_openai_available,
        is_google_ai_available,
        is_pinecone_available,
        generate_embedding,
        semantic_search,
        get_completion,
        get_best_ai_model
    )

    from .regulatory_ai_service import (
        get_supported_frameworks,
        analyze_document_compliance,
        generate_compliance_visualization_data,
        handle_document_upload,
        get_upload_folder
    )
except ImportError as e:
    # This is fine - individual modules will handle their own imports
    pass