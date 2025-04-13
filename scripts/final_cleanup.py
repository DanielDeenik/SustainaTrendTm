import os
import shutil
import glob
import time

def move_file(source, destination):
    """Move a file to its new location."""
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # If destination file exists, remove it first
        if os.path.exists(destination):
            os.remove(destination)
            
        shutil.move(source, destination)
        print(f"Successfully moved {source} to {destination}")
    except Exception as e:
        print(f"Error moving {source} to {destination}: {str(e)}")

def safe_remove_directory(directory):
    try:
        if os.path.exists(directory):
            # Try to remove the directory
            shutil.rmtree(directory)
            print(f"Successfully removed directory: {directory}")
    except PermissionError:
        print(f"Warning: Could not remove {directory} - it may be in use by another process")
    except Exception as e:
        print(f"Error removing {directory}: {str(e)}")

def final_cleanup():
    """Finish cleaning up the codebase by moving remaining files to their appropriate locations."""
    # Move JSON files to src/backend/data/
    json_files = {
        "search_results.json": "src/backend/data/search_results.json",
        "story.json": "src/backend/data/story.json",
        "storytelling_response.json": "src/backend/data/storytelling_response.json",
        "response.json": "src/backend/data/response.json"
    }
    
    for source, dest in json_files.items():
        if os.path.exists(source):
            move_file(source, dest)
    
    # Move JavaScript files to src/frontend/static/js/
    js_files = glob.glob("*.js")
    for js_file in js_files:
        if js_file != "final_cleanup.py":  # Don't move the cleanup script itself
            dest = f"src/frontend/static/js/{js_file}"
            move_file(js_file, dest)
    
    # Move Python files to src/backend/scripts/
    py_files = glob.glob("*.py")
    for py_file in py_files:
        if py_file != "final_cleanup.py":  # Don't move the cleanup script itself
            dest = f"src/backend/scripts/{py_file}"
            move_file(py_file, dest)
    
    # Create necessary directories
    os.makedirs("src/backend/data", exist_ok=True)
    os.makedirs("src/backend/scripts", exist_ok=True)
    
    # Copy contents from old directories to new structure
    if os.path.exists("frontend") and not os.path.exists("src/frontend"):
        print("Copying files from frontend to src/frontend...")
        shutil.copytree("frontend", "src/frontend", dirs_exist_ok=True)
    
    if os.path.exists("backend") and not os.path.exists("src/backend"):
        print("Copying files from backend to src/backend...")
        shutil.copytree("backend", "src/backend", dirs_exist_ok=True)
    
    # Try to remove old directories and files
    print("\nAttempting to clean up old directories and files...")
    safe_remove_directory("frontend")
    safe_remove_directory("backend")
    safe_remove_directory("server")
    
    # Remove .replit file if it exists
    if os.path.exists(".replit"):
        try:
            os.remove(".replit")
            print("Removed .replit file")
        except Exception as e:
            print(f"Error removing .replit file: {str(e)}")
    
    print("\nCleanup completed. Some files or directories may still exist if they are in use.")
    print("Please close any applications that might be using these files and run the script again if needed.")

if __name__ == "__main__":
    final_cleanup() 