# PowerShell script to set up MongoDB on Windows

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

# Download MongoDB Community Server
$mongodbUrl = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-6.0.6-signed.msi"
$installerPath = "$env:TEMP\mongodb.msi"

Write-Host "Downloading MongoDB Community Server..."
Invoke-WebRequest -Uri $mongodbUrl -OutFile $installerPath

# Install MongoDB
Write-Host "Installing MongoDB..."
Start-Process msiexec.exe -ArgumentList "/i `"$installerPath`" /qn" -Wait

# Add MongoDB to system PATH
$mongodbPath = "C:\Program Files\MongoDB\Server\6.0\bin"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if (-not $currentPath.Contains($mongodbPath)) {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$mongodbPath", "Machine")
    Write-Host "Added MongoDB to system PATH"
}

# Create MongoDB configuration file
$configPath = "C:\Program Files\MongoDB\Server\6.0\bin\mongod.cfg"
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

Set-Content -Path $configPath -Value $configContent
Write-Host "Created MongoDB configuration file"

# Install MongoDB as a Windows Service
Write-Host "Installing MongoDB service..."
& "C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe" --config "$configPath" --install

# Start MongoDB service
Write-Host "Starting MongoDB service..."
Start-Service MongoDB

Write-Host "MongoDB setup completed successfully!"
Write-Host "You can now run the populate_mongodb.py script to populate the database with mock data." 