import os
import shutil
from pathlib import Path

def integrate_trendsense():
    """
    Integrate the TrendSense codebase into the current project structure.
    """
    # Define paths
    trendsense_dir = Path("TrendSense")
    src_dir = Path("src")
    
    # Create necessary directories
    os.makedirs("src/backend/services/trendsense", exist_ok=True)
    os.makedirs("src/backend/api", exist_ok=True)
    os.makedirs("src/backend/config", exist_ok=True)
    os.makedirs("src/frontend/templates", exist_ok=True)
    os.makedirs("src/frontend/static", exist_ok=True)
    
    # Move backend components
    if trendsense_dir.exists():
        try:
            # Move core application files
            if (trendsense_dir / "app.py").exists():
                shutil.copy2(trendsense_dir / "app.py", src_dir / "backend" / "app.py")
                print("Copied app.py")
            
            # Move VC/PE module
            if (trendsense_dir / "vc_pe").exists():
                shutil.copytree(
                    trendsense_dir / "vc_pe",
                    src_dir / "backend" / "services" / "trendsense" / "vc_pe",
                    dirs_exist_ok=True
                )
                print("Copied VC/PE module")
            
            # Move frontend templates and static files
            if (trendsense_dir / "frontend" / "templates").exists():
                shutil.copytree(
                    trendsense_dir / "frontend" / "templates",
                    src_dir / "frontend" / "templates",
                    dirs_exist_ok=True
                )
                print("Copied frontend templates")
            
            if (trendsense_dir / "frontend" / "static").exists():
                shutil.copytree(
                    trendsense_dir / "frontend" / "static",
                    src_dir / "frontend" / "static",
                    dirs_exist_ok=True
                )
                print("Copied frontend static files")
            
            # Move sample data
            if (trendsense_dir / "sample_data").exists():
                shutil.copytree(
                    trendsense_dir / "sample_data",
                    src_dir / "backend" / "data" / "sample_data",
                    dirs_exist_ok=True
                )
                print("Copied sample data")
            
            # Copy environment file
            if (trendsense_dir / ".env.example").exists():
                shutil.copy2(trendsense_dir / ".env.example", ".env.example")
                print("Copied .env.example")
            
            # Copy dependencies
            if (trendsense_dir / "pyproject.toml").exists():
                shutil.copy2(trendsense_dir / "pyproject.toml", "pyproject.toml")
                print("Copied pyproject.toml")
            
            print("\nSuccessfully integrated TrendSense codebase!")
            print("\nNext steps:")
            print("1. Review and update the .env file with your configuration")
            print("2. Install the required dependencies from pyproject.toml")
            print("3. Start the application using 'python src/backend/app.py'")
            
        except Exception as e:
            print(f"Error during integration: {str(e)}")
    else:
        print("Error: TrendSense directory not found!")

if __name__ == "__main__":
    integrate_trendsense() 