import subprocess
import time
import os

def take_screenshot(url, output_path):
    """Take a screenshot of a webpage using Chrome"""
    try:
        # We need to create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Use curl to check if the server is running
        subprocess.run(["curl", "-s", url], check=True, stdout=subprocess.PIPE)
        
        # Simple command to take a screenshot using Chrome headless mode
        cmd = [
            "google-chrome", 
            "--headless", 
            "--disable-gpu",
            "--window-size=1920,1080",
            "--screenshot=" + output_path,
            url
        ]
        
        subprocess.run(cmd, check=True)
        print(f"Screenshot saved to {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error taking screenshot: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Wait a bit to make sure the server is fully running
    time.sleep(2)
    
    # Take screenshots of various pages
    pages = [
        ("/dashboard/", "dashboard"),
        ("/copilot/", "copilot"),
        ("/vc-lens/", "vc_lens"),
        ("/strategy-hub/", "strategy_hub"),
    ]
    
    for path, name in pages:
        output_path = f"./screenshots/{name}.png"
        take_screenshot("http://localhost:5000" + path, output_path)
        # Wait a bit between screenshots
        time.sleep(1)