import os
import shutil
from pathlib import Path

def unify_trendsense():
    """
    Unify TrendSense and VC Sense features with consistent styling.
    """
    # Define paths
    src_dir = Path("src")
    frontend_dir = src_dir / "frontend"
    backend_dir = src_dir / "backend"
    
    # Create unified CSS directory
    css_dir = frontend_dir / "static" / "css" / "unified"
    os.makedirs(css_dir, exist_ok=True)
    
    # Create a unified theme CSS file
    unified_theme = css_dir / "unified-theme.css"
    
    # Combine and organize CSS files
    css_files = {
        "base": [
            "normalize.css",
            "common.css",
            "theme.css",
            "unified-theme.css"
        ],
        "components": [
            "card-components.css",
            "chart-components.css",
            "metric-components.css",
            "navigation-components.css",
            "story-components.css"
        ],
        "features": [
            "trend-analysis.css",
            "sustainability-copilot.css",
            "strategy-hub.css",
            "dashboard.css",
            "document-hub-redesign.css"
        ]
    }
    
    # Create feature-specific directories
    for feature in css_files.keys():
        os.makedirs(css_dir / feature, exist_ok=True)
    
    # Move and organize CSS files
    for category, files in css_files.items():
        for file in files:
            source = frontend_dir / "static" / "css" / file
            if source.exists():
                dest = css_dir / category / file
                try:
                    # Read with UTF-8 encoding
                    with open(source, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Write with UTF-8 encoding
                    with open(dest, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"Moved {file} to unified/{category}/")
                except UnicodeDecodeError:
                    # If UTF-8 fails, try with latin-1
                    with open(source, 'r', encoding='latin-1') as f:
                        content = f.read()
                    with open(dest, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Moved {file} to unified/{category}/ (converted encoding)")
    
    # Create a main CSS file that imports all components
    with open(css_dir / "main.css", "w", encoding='utf-8') as f:
        f.write("/* Unified TrendSense Theme */\n\n")
        
        # Import base styles
        f.write("/* Base Styles */\n")
        for file in css_files["base"]:
            f.write(f'@import "base/{file}";\n')
        
        # Import components
        f.write("\n/* Components */\n")
        for file in css_files["components"]:
            f.write(f'@import "components/{file}";\n')
        
        # Import features
        f.write("\n/* Features */\n")
        for file in css_files["features"]:
            f.write(f'@import "features/{file}";\n')
    
    # Update template references
    templates_dir = frontend_dir / "templates"
    for template in templates_dir.glob("**/*.html"):
        try:
            with open(template, "r", encoding='utf-8') as f:
                content = f.read()
            
            # Update CSS references
            content = content.replace(
                'href="/static/css/',
                'href="/static/css/unified/'
            )
            
            with open(template, "w", encoding='utf-8') as f:
                f.write(content)
        except UnicodeDecodeError:
            with open(template, "r", encoding='latin-1') as f:
                content = f.read()
            content = content.replace(
                'href="/static/css/',
                'href="/static/css/unified/'
            )
            with open(template, "w", encoding='utf-8') as f:
                f.write(content)
    
    # Create a unified routes file
    routes_dir = backend_dir / "routes"
    os.makedirs(routes_dir, exist_ok=True)
    
    # Copy and merge route files
    vc_pe_routes = backend_dir / "services" / "trendsense" / "vc_pe" / "routes.py"
    if vc_pe_routes.exists():
        shutil.copy2(vc_pe_routes, routes_dir / "vc_pe_routes.py")
    
    print("\nSuccessfully unified TrendSense features!")
    print("\nNext steps:")
    print("1. Review the unified CSS structure in src/frontend/static/css/unified/")
    print("2. Update any template references to use the new unified CSS")
    print("3. Test the application to ensure all features work with the unified styling")

if __name__ == "__main__":
    unify_trendsense() 