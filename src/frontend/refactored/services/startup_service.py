"""
Startup service for managing application startup configuration.
Provides OS-specific startup management and status reporting.
"""

import os
import sys
import platform
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional

class StartupService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StartupService, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self._initialized = True
        self._config = self._load_config()
        self._status = self._check_configuration()

    def _load_config(self) -> Dict[str, Any]:
        """Load startup configuration based on OS."""
        config = {
            'os_type': platform.system().lower(),
            'startup_dir': self._get_startup_dir(),
            'app_path': str(Path(__file__).parent.parent.parent.absolute()),
            'is_configured': False
        }
        return config

    def _get_startup_dir(self) -> str:
        """Get OS-specific startup directory."""
        system = platform.system().lower()
        if system == 'windows':
            return os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        elif system == 'darwin':  # macOS
            return os.path.expanduser('~/Library/LaunchAgents')
        else:  # Linux
            return os.path.expanduser('~/.config/autostart')

    def _check_configuration(self) -> Dict[str, Any]:
        """Check current startup configuration status."""
        try:
            startup_file = self._get_startup_file_path()
            is_configured = os.path.exists(startup_file)
            
            return {
                'status': 'healthy' if is_configured else 'warning',
                'details': {
                    'os_type': self._config['os_type'],
                    'startup_dir': self._config['startup_dir'],
                    'app_path': self._config['app_path'],
                    'is_configured': is_configured
                }
            }
        except Exception as e:
            self.logger.error(f"Error checking startup configuration: {str(e)}")
            return {
                'status': 'error',
                'details': {
                    'os_type': self._config['os_type'],
                    'startup_dir': self._config['startup_dir'],
                    'app_path': self._config['app_path'],
                    'is_configured': False,
                    'error': str(e)
                }
            }

    def _get_startup_file_path(self) -> str:
        """Get OS-specific startup file path."""
        system = platform.system().lower()
        if system == 'windows':
            return os.path.join(self._config['startup_dir'], 'SustainaTrend.bat')
        elif system == 'darwin':  # macOS
            return os.path.join(self._config['startup_dir'], 'com.sustainatrend.plist')
        else:  # Linux
            return os.path.join(self._config['startup_dir'], 'sustainatrend.desktop')

    def configure_autostart(self) -> bool:
        """Configure application to start on system startup."""
        try:
            system = platform.system().lower()
            startup_file = self._get_startup_file_path()
            
            if system == 'windows':
                with open(startup_file, 'w') as f:
                    f.write(f'@echo off\n"{sys.executable}" "{os.path.join(self._config["app_path"], "run.py")}"')
            elif system == 'darwin':  # macOS
                plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sustainatrend</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{os.path.join(self._config["app_path"], "run.py")}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>'''
                with open(startup_file, 'w') as f:
                    f.write(plist_content)
            else:  # Linux
                desktop_entry = f'''[Desktop Entry]
Type=Application
Name=SustainaTrend
Exec={sys.executable} {os.path.join(self._config["app_path"], "run.py")}
Terminal=false
X-GNOME-Autostart-enabled=true'''
                with open(startup_file, 'w') as f:
                    f.write(desktop_entry)
                os.chmod(startup_file, 0o755)

            self._config['is_configured'] = True
            self._status = self._check_configuration()
            return True

        except Exception as e:
            self.logger.error(f"Error configuring autostart: {str(e)}")
            return False

    def remove_autostart(self) -> bool:
        """Remove application from system startup."""
        try:
            startup_file = self._get_startup_file_path()
            if os.path.exists(startup_file):
                os.remove(startup_file)
            
            self._config['is_configured'] = False
            self._status = self._check_configuration()
            return True

        except Exception as e:
            self.logger.error(f"Error removing autostart: {str(e)}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current startup service status."""
        return self._status

# Create singleton instance
startup_service = StartupService() 