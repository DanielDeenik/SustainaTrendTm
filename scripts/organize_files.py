import os
import shutil
from pathlib import Path

def create_directory(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)

def move_file(source, destination):
    """Move a file to its new location."""
    try:
        shutil.move(source, destination)
        print(f"Moved {source} to {destination}")
    except Exception as e:
        print(f"Error moving {source}: {e}")

def organize_files():
    # Create necessary directories
    directories = [
        "src/frontend/static",
        "src/frontend/templates",
        "src/frontend/utils",
        "src/backend/api",
        "src/backend/models",
        "src/backend/services",
        "src/backend/utils",
        "config",
        "tests",
        "docs",
        "assets/images",
        "assets/uploads",
        "scripts"
    ]
    
    for directory in directories:
        create_directory(directory)

    # Move frontend files
    frontend_files = {
        "*.html": "src/frontend/templates/",
        "*.js": "src/frontend/static/js/",
        "*.css": "src/frontend/static/css/",
        "story_edit_script.js": "src/frontend/static/js/",
        "updated_story_edit_script.js": "src/frontend/static/js/",
        "navigation_config.py": "src/frontend/utils/",
        "app.py": "src/frontend/",
        "sustainability_copilot.py": "src/frontend/services/",
        "sustainability_storytelling.py": "src/frontend/services/",
        "sustainability_trend.py": "src/frontend/services/",
        "strategy_ai_consultant.py": "src/frontend/services/",
        "strategy_simulation.py": "src/frontend/services/",
        "monetization_strategies.py": "src/frontend/services/",
        "marketing_strategies.py": "src/frontend/services/",
        "realestate_sustainability.py": "src/frontend/services/",
        "regulatory_ai_agent_refactored.py": "src/frontend/services/",
        "document_processor.py": "src/frontend/services/",
        "document_query_api.py": "src/frontend/services/",
        "enhanced_search.py": "src/frontend/services/",
        "esrs_framework.py": "src/frontend/services/",
        "ethical_ai.py": "src/frontend/services/",
        "benchmark_db.py": "src/frontend/services/",
        "ai_code_automation_example.py": "src/frontend/services/"
    }

    # Move backend files
    backend_files = {
        "main.py": "src/backend/",
        "database.py": "src/backend/models/",
        "models.py": "src/backend/models/",
        "storytelling_api.py": "src/backend/api/",
        "sustainability_api.py": "src/backend/api/",
        "create_stories_table.py": "src/backend/models/",
        "seed_database.py": "src/backend/models/",
        "logging.conf": "config/",
        "requirements-sustainability.txt": "config/"
    }

    # Move test files
    test_files = {
        "test_*.py": "tests/",
        "test_*.txt": "tests/data/"
    }

    # Move documentation files
    doc_files = {
        "*.md": "docs/",
        "ARCHITECTURE.md": "docs/",
        "AI-DRIVEN-ARCHITECTURE.md": "docs/",
        "ROUTE-DOCUMENTATION.md": "docs/",
        "STANDALONE-DASHBOARD.md": "docs/",
        "WIREFRAME-UI.md": "docs/"
    }

    # Move configuration files
    config_files = {
        ".env": "config/",
        ".env.example": "config/",
        "pyproject.toml": "config/",
        "package.json": "config/",
        "package-lock.json": "config/"
    }

    # Move asset files
    asset_files = {
        "*.png": "assets/images/",
        "*.jpg": "assets/images/",
        "*.jpeg": "assets/images/",
        "*.gif": "assets/images/",
        "*.svg": "assets/images/"
    }

    # Execute moves
    all_moves = {
        **frontend_files,
        **backend_files,
        **test_files,
        **doc_files,
        **config_files,
        **asset_files
    }

    for pattern, destination in all_moves.items():
        if "*" in pattern:
            # Handle glob patterns
            import glob
            for file in glob.glob(pattern):
                if os.path.isfile(file):
                    move_file(file, os.path.join(destination, os.path.basename(file)))
        else:
            # Handle specific files
            if os.path.exists(pattern):
                move_file(pattern, os.path.join(destination, pattern))

if __name__ == "__main__":
    organize_files() 