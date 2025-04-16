# Start SustainaTrend service with elevated privileges
Write-Host "Starting SustainaTrend Windows Service..."

# Check for administrative privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Requesting administrative privileges..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Function to check service status
function Get-ServiceStatus {
    param($ServiceName)
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "Service Status: $($service.Status)"
        Write-Host "Start Type: $($service.StartType)"
        return $service
    }
    return $null
}

# Check if service exists and get its status
$service = Get-ServiceStatus -ServiceName "SustainaTrendService"
if (-not $service) {
    Write-Host "Error: Service not found"
    pause
    exit 1
}

# Try to start the service
Write-Host "Attempting to start service..."
try {
    Start-Service -Name "SustainaTrendService" -ErrorAction Stop
    Write-Host "Service started successfully"
} catch {
    Write-Host "Error starting service: $_"
    Write-Host "Checking service configuration..."
    
    # Check service configuration
    $sc = sc qc SustainaTrendService
    Write-Host "Service Configuration:"
    Write-Host $sc
    
    # Check service dependencies
    $deps = sc enumdepend SustainaTrendService
    Write-Host "Service Dependencies:"
    Write-Host $deps
    
    # Check event log for errors
    Write-Host "Checking Event Log for errors..."
    Get-EventLog -LogName System -Source "Service Control Manager" -Newest 10 | 
    Where-Object {$_.Message -like "*SustainaTrend*"} | 
    ForEach-Object {
        Write-Host "Event ID: $($_.EventID)"
        Write-Host "Time: $($_.TimeGenerated)"
        Write-Host "Message: $($_.Message)"
        Write-Host "---"
    }
}

# Wait and check final status
Start-Sleep -Seconds 5
Get-ServiceStatus -ServiceName "SustainaTrendService"

pause