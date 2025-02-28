#!/usr/bin/env python3
"""
Port Manager - Structural solution for Replit port conflicts

This module provides a robust mechanism to ensure exclusive access to ports
in environments with resource contention (like Replit), handling detection,
termination, and verification of port usage.
"""
import os
import sys
import signal
import socket
import time
import subprocess
import logging
import psutil
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PortManager:
    """Manages port allocations to prevent conflicts"""

    def __init__(self, port=5000, max_retries=3, retry_delay=2, timeout=10):
        """
        Initialize the PortManager

        Args:
            port: The port to manage (default: 5000)
            max_retries: Maximum number of retries to free the port
            retry_delay: Delay between retries in seconds
            timeout: Timeout in seconds when waiting for an application to start
        """
        self.port = port
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.managed_process = None

    def is_port_in_use(self):
        """Check if the port is already in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', self.port)) == 0

    def get_pid_using_port(self):
        """Find the PID of any process using the specified port"""
        try:
            # Use psutil's network connections function to find processes using the port
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr and len(conn.laddr) >= 2 and conn.laddr[1] == self.port:
                    return conn.pid
        except (psutil.AccessDenied, AttributeError) as e:
            logger.warning(f"Access issue checking network connections: {str(e)}")

        # Fallback: use system command if psutil doesn't work
        try:
            output = subprocess.check_output(
                f"lsof -i :{self.port} -t", shell=True, text=True
            ).strip()
            if output:
                return int(output.split('\n')[0])
        except (subprocess.SubprocessError, ValueError):
            pass

        return None

    def terminate_process_by_pid(self, pid):
        """Terminate a process by its PID with proper handling"""
        if not pid:
            return False

        try:
            proc = psutil.Process(pid)
            logger.info(f"Found process {pid} ({proc.name()}) using port {self.port}")

            # Try graceful termination first
            logger.info(f"Attempting graceful termination of process {pid}")
            proc.terminate()

            # Wait for up to 3 seconds for graceful termination
            gone, still_alive = psutil.wait_procs([proc], timeout=3)

            if still_alive:
                # Force kill if still alive
                logger.warning(f"Process {pid} did not terminate gracefully, killing it")
                proc.kill()
                psutil.wait_procs([proc], timeout=2)

            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.warning(f"Error terminating process {pid}: {str(e)}")

            # Fallback: try using system commands if psutil fails
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                if self.is_port_in_use():
                    os.kill(pid, signal.SIGKILL)
                return True
            except OSError as ose:
                logger.warning(f"Failed to kill process using os.kill: {str(ose)}")

            return False

    def free_port(self):
        """Ensure the port is free, terminating any process using it"""
        if not self.is_port_in_use():
            logger.info(f"Port {self.port} is already free")
            return True

        logger.warning(f"Port {self.port} is in use, attempting to free it")

        for attempt in range(self.max_retries):
            pid = self.get_pid_using_port()

            if pid:
                success = self.terminate_process_by_pid(pid)
                if success:
                    logger.info(f"Process {pid} using port {self.port} terminated")
                else:
                    logger.warning(f"Failed to terminate process {pid}")
            else:
                logger.warning(f"Could not identify process using port {self.port}")

            # Wait for the port to be released
            time.sleep(self.retry_delay)

            if not self.is_port_in_use():
                logger.info(f"Port {self.port} is now free")
                return True

            if attempt < self.max_retries - 1:
                logger.warning(f"Port {self.port} still in use. Retry {attempt + 1}/{self.max_retries}...")

        logger.error(f"Failed to free port {self.port} after {self.max_retries} attempts")
        return False

    @contextmanager
    def ensure_free_port(self):
        """Context manager to ensure the port is free within the context"""
        success = self.free_port()
        if not success:
            logger.error(f"Could not free port {self.port}")
            yield False
        else:
            logger.info(f"Port {self.port} is free and available")
            yield True

    def run_app(self, app_command, working_dir=None):
        """Run an application with the managed port"""
        # Ensure port is free before starting the app
        if not self.free_port():
            logger.error(f"Cannot start application - port {self.port} is still in use")
            return None

        logger.info(f"Starting application on port {self.port} with command: {app_command}")

        # Prepare environment with PORT variable set
        env = os.environ.copy()
        env['PORT'] = str(self.port)

        # Start the application
        try:
            original_dir = None
            if working_dir:
                original_dir = os.getcwd()
                os.chdir(working_dir)

            self.managed_process = subprocess.Popen(
                app_command,
                env=env,
                shell=isinstance(app_command, str)
            )

            if original_dir:
                os.chdir(original_dir)

            # Wait for the app to start
            for _ in range(self.timeout):
                time.sleep(1)
                if self.is_port_in_use():
                    logger.info(f"Application is now running on port {self.port}")
                    return self.managed_process

            # If we got here, the app didn't start in time
            logger.error(f"Application failed to start within {self.timeout} seconds")
            if self.managed_process:
                self.managed_process.terminate()
                self.managed_process = None

            return None

        except Exception as e:
            logger.error(f"Error starting application: {str(e)}")
            if self.managed_process:
                self.managed_process.terminate()
                self.managed_process = None
            return None

    def run_flask_app(self, app_path):
        """Run a Flask application with the managed port"""
        return self.run_app([sys.executable, app_path])

    def stop_app(self):
        """Stop the managed application properly"""
        if not self.managed_process:
            logger.warning("No managed process to stop")
            return False

        logger.info(f"Stopping managed process {self.managed_process.pid}")
        try:
            self.managed_process.terminate()
            try:
                self.managed_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate gracefully, forcing kill")
                self.managed_process.kill()

            self.managed_process = None
            return True

        except Exception as e:
            logger.error(f"Error stopping managed process: {str(e)}")
            return False

def main():
    """Command-line interface for the port manager"""
    import argparse

    parser = argparse.ArgumentParser(description="Manage port allocations and run applications")
    parser.add_argument("--port", type=int, default=5000, help="Port to manage (default: 5000)")
    parser.add_argument("--check", action="store_true", help="Check if port is in use")
    parser.add_argument("--free", action="store_true", help="Free the port if in use")
    parser.add_argument("--run", help="Run a command with the managed port")
    parser.add_argument("--flask", help="Run a Flask application with the managed port")

    args = parser.parse_args()
    port_manager = PortManager(port=args.port)

    if args.check:
        if port_manager.is_port_in_use():
            pid = port_manager.get_pid_using_port()
            print(f"Port {args.port} is in use by process {pid}")
            return 1
        else:
            print(f"Port {args.port} is free")
            return 0

    if args.free:
        if port_manager.free_port():
            print(f"Successfully freed port {args.port}")
            return 0
        else:
            print(f"Failed to free port {args.port}")
            return 1

    if args.run:
        process = port_manager.run_app(args.run)
        if process:
            try:
                process.wait()
                return process.returncode
            except KeyboardInterrupt:
                print("Interrupted, stopping application...")
                port_manager.stop_app()
                return 1
        else:
            return 1

    if args.flask:
        process = port_manager.run_flask_app(args.flask)
        if process:
            try:
                process.wait()
                return process.returncode
            except KeyboardInterrupt:
                print("Interrupted, stopping Flask application...")
                port_manager.stop_app()
                return 1
        else:
            return 1

    parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())