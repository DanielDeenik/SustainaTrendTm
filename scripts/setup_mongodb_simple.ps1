# PowerShell script to set up MongoDB directories and configuration

# Create MongoDB data directory
$dataPath = "C:\data\db"
if (-not (Test-Path $dataPath)) {
    New-Item -ItemType Directory -Path $dataPath -Force
    Write-Host "Created MongoDB data directory at $dataPath"
}

# Create MongoDB log directory
$logPath = "C:\data\log"
if (-not (Test-Path $logPath)) {
    New-Item -ItemType Directory -Path $logPath -Force
    Write-Host "Created MongoDB log directory at $logPath"
}

# Create MongoDB configuration file
$configPath = "C:\Program Files\MongoDB\Server\7.0\bin\mongod.cfg"
$configContent = @"
systemLog:
  destination: file
  path: C:\data\log\mongod.log
  logAppend: true
storage:
  dbPath: C:\data\db
net:
  bindIp: 127.0.0.1
  port: 27017
"@

try {
    Set-Content -Path $configPath -Value $configContent -Force
    Write-Host "Created MongoDB configuration file at $configPath"
} catch {
    Write-Host "Error creating configuration file: $_"
}

Write-Host "`nMongoDB setup completed!"
Write-Host "Please ensure MongoDB is installed from https://www.mongodb.com/try/download/community"
Write-Host "After installation, run the following commands as administrator:"
Write-Host "1. mongod --config `"$configPath`" --install"
Write-Host "2. Start-Service MongoDB" 