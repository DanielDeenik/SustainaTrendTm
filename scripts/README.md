# SustainaTrend™ Service Management Scripts

This directory contains scripts for managing the SustainaTrend™ service on Windows systems.

## Prerequisites

- Windows operating system
- PowerShell 5.0 or later
- Administrator privileges (for install/uninstall operations)
- NSSM (Non-Sucking Service Manager) installed in the `scripts` directory

## Available Scripts

### `service_manager.ps1`

The main PowerShell script that handles all service management operations. This script should not be called directly; use the batch wrapper instead.

### `manage_service.bat`

A batch file wrapper that provides a simple command-line interface for managing the service.

## Usage

Open a command prompt and navigate to the project root directory. Then use the following commands:

```batch
scripts\manage_service.bat [action]
```

Where `[action]` is one of:

- `install` - Install the SustainaTrend™ service
- `uninstall` - Uninstall the SustainaTrend™ service
- `start` - Start the SustainaTrend™ service
- `stop` - Stop the SustainaTrend™ service
- `restart` - Restart the SustainaTrend™ service
- `status` - Check the status of the SustainaTrend™ service

## Examples

```batch
# Install the service
scripts\manage_service.bat install

# Start the service
scripts\manage_service.bat start

# Check service status
scripts\manage_service.bat status

# Stop the service
scripts\manage_service.bat stop

# Restart the service
scripts\manage_service.bat restart

# Uninstall the service
scripts\manage_service.bat uninstall
```

## Logging

All service management operations are logged to:
- Console output (with color-coded messages)
- `logs/service_manager.log` file

Service output is logged to:
- `logs/service_stdout.log` (standard output)
- `logs/service_stderr.log` (standard error)

## Error Handling

The scripts include comprehensive error handling:
- Validates administrator privileges for install/uninstall operations
- Checks for service existence before operations
- Provides detailed error messages
- Returns appropriate exit codes

## Notes

- The service is configured to automatically restart on failure
- Service logs are stored in the `logs` directory
- The service runs under the Local System account
- The service is configured to start automatically on system boot 