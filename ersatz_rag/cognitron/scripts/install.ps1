# Cognitron Installation Script for Windows PowerShell
# Medical-Grade Personal Knowledge Assistant
# Version: 1.0.0

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('install', 'uninstall', 'update', 'help')]
    [string]$Action = 'install',
    
    [Parameter()]
    [string]$InstallDir = "$env:USERPROFILE\.cognitron",
    
    [Parameter()]
    [string]$CognitronVersion = "1.0.0",
    
    [Parameter()]
    [string]$PythonMinVersion = "3.11",
    
    [Parameter()]
    [switch]$Force,
    
    [Parameter()]
    [switch]$Quiet,
    
    [Parameter()]
    [switch]$Dev
)

# =============================================================================
# Configuration and Constants
# =============================================================================

$Script:ScriptVersion = "1.0.0"
$Script:PyPiPackage = "cognitron"
$Script:GitHubRepo = "https://github.com/cognitron-ai/cognitron"
$Script:VenvDir = Join-Path $InstallDir "venv"
$Script:LogFile = Join-Path $InstallDir "install.log"

# Colors for output
$Script:Colors = @{
    Red     = 'Red'
    Green   = 'Green'
    Yellow  = 'Yellow'
    Blue    = 'Blue'
    Cyan    = 'Cyan'
    White   = 'White'
    Gray    = 'Gray'
}

# =============================================================================
# Utility Functions
# =============================================================================

function Write-Log {
    param([string]$Message)
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp - $Message"
    
    try {
        if (-not (Test-Path (Split-Path $Script:LogFile))) {
            New-Item -ItemType Directory -Path (Split-Path $Script:LogFile) -Force | Out-Null
        }
        Add-Content -Path $Script:LogFile -Value $logMessage
    }
    catch {
        # Ignore logging errors
    }
}

function Write-Header {
    if (-not $Quiet) {
        Clear-Host
        Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
        Write-Host "║                                                                              ║" -ForegroundColor Cyan
        Write-Host "║   🧠 COGNITRON INSTALLER                                                     ║" -ForegroundColor Cyan
        Write-Host "║   Medical-Grade Personal Knowledge Assistant                                 ║" -ForegroundColor Cyan
        Write-Host "║                                                                              ║" -ForegroundColor Cyan
        Write-Host "║   Version: $CognitronVersion                                                           ║" -ForegroundColor Cyan
        Write-Host "║   Platform: Windows $(Get-WmiObject Win32_OperatingSystem | Select-Object -ExpandProperty Version)                                              ║" -ForegroundColor Cyan
        Write-Host "║                                                                              ║" -ForegroundColor Cyan
        Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
        Write-Host ""
    }
}

function Write-Step {
    param([string]$Message)
    
    if (-not $Quiet) {
        Write-Host "[STEP] $Message" -ForegroundColor Blue
    }
    Write-Log "STEP: $Message"
}

function Write-Success {
    param([string]$Message)
    
    if (-not $Quiet) {
        Write-Host "[SUCCESS] $Message" -ForegroundColor Green
    }
    Write-Log "SUCCESS: $Message"
}

function Write-Warning {
    param([string]$Message)
    
    if (-not $Quiet) {
        Write-Host "[WARNING] $Message" -ForegroundColor Yellow
    }
    Write-Log "WARNING: $Message"
}

function Write-ErrorMsg {
    param([string]$Message)
    
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    Write-Log "ERROR: $Message"
}

function Write-Info {
    param([string]$Message)
    
    if (-not $Quiet) {
        Write-Host "[INFO] $Message" -ForegroundColor White
    }
    Write-Log "INFO: $Message"
}

function Test-Command {
    param([string]$CommandName)
    
    return Get-Command $CommandName -ErrorAction SilentlyContinue
}

function Compare-Version {
    param(
        [string]$Version1,
        [string]$Version2
    )
    
    $v1 = [System.Version]::Parse($Version1)
    $v2 = [System.Version]::Parse($Version2)
    
    return $v1.CompareTo($v2)
}

function Read-YesNo {
    param(
        [string]$Prompt,
        [string]$Default = "Y"
    )
    
    if ($Quiet -and $Force) {
        return $true
    }
    
    $suffix = if ($Default -eq "Y") { " [Y/n]" } else { " [y/N]" }
    
    do {
        $response = Read-Host "$Prompt$suffix"
        if ([string]::IsNullOrEmpty($response)) {
            $response = $Default
        }
        
        switch ($response.ToUpper()) {
            "Y" { return $true }
            "YES" { return $true }
            "N" { return $false }
            "NO" { return $false }
            default { 
                Write-Host "Please answer yes or no." -ForegroundColor Red
            }
        }
    } while ($true)
}

function New-DirectoryIfNotExists {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Log "Created directory: $Path"
    }
}

# =============================================================================
# System Detection and Requirements
# =============================================================================

function Test-WindowsVersion {
    Write-Step "Checking Windows version"
    
    $os = Get-WmiObject Win32_OperatingSystem
    $osVersion = [System.Version]::Parse($os.Version)
    $minVersion = [System.Version]::Parse("10.0")  # Windows 10
    
    if ($osVersion.CompareTo($minVersion) -lt 0) {
        Write-ErrorMsg "Windows 10 or later is required. Current version: $($os.Caption)"
        exit 1
    }
    
    Write-Success "Windows version: $($os.Caption) (Build $($os.BuildNumber))"
    Write-Log "OS Details: $($os.Caption), Version: $($os.Version), Architecture: $($os.OSArchitecture)"
}

function Test-PowerShellVersion {
    Write-Step "Checking PowerShell version"
    
    $psVersion = $PSVersionTable.PSVersion
    $minVersion = [System.Version]::Parse("5.1")
    
    if ($psVersion.CompareTo($minVersion) -lt 0) {
        Write-ErrorMsg "PowerShell 5.1 or later is required. Current version: $psVersion"
        Write-Info "Please upgrade PowerShell: https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows"
        exit 1
    }
    
    Write-Success "PowerShell version: $psVersion"
}

function Find-Python {
    Write-Step "Checking Python installation"
    
    $pythonCommands = @("python", "python3", "py")
    $pythonCmd = $null
    $pythonVersion = $null
    
    foreach ($cmd in $pythonCommands) {
        if (Test-Command $cmd) {
            try {
                $versionOutput = & $cmd --version 2>&1
                if ($versionOutput -match "Python ([\d\.]+)") {
                    $version = $matches[1]
                    $minVersionObj = [System.Version]::Parse($PythonMinVersion)
                    $currentVersionObj = [System.Version]::Parse($version)
                    
                    if ($currentVersionObj.CompareTo($minVersionObj) -ge 0) {
                        $pythonCmd = $cmd
                        $pythonVersion = $version
                        break
                    }
                }
            }
            catch {
                continue
            }
        }
    }
    
    if (-not $pythonCmd) {
        Write-ErrorMsg "Python $PythonMinVersion or later not found"
        Write-Info "Please install Python from: https://www.python.org/downloads/"
        Write-Info "Or install via Microsoft Store: ms-windows-store://search/?query=python"
        Write-Info "Or use winget: winget install Python.Python.3.11"
        exit 1
    }
    
    $Script:PythonCmd = $pythonCmd
    $Script:PythonVersion = $pythonVersion
    Write-Success "Found Python $pythonVersion at $(Get-Command $pythonCmd | Select-Object -ExpandProperty Source)"
}

function Test-Dependencies {
    Write-Step "Checking system dependencies"
    
    $missingDeps = @()
    
    # Check for Git
    if (-not (Test-Command "git")) {
        $missingDeps += "Git"
    }
    
    # Check for curl or Invoke-WebRequest (built into PowerShell)
    # PowerShell has Invoke-WebRequest built-in, so we don't need curl
    
    # Check for Microsoft Visual C++ Build Tools (for some Python packages)
    $vcInstalled = $false
    try {
        $vs = Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*Microsoft Visual C++*" -or $_.Name -like "*Visual Studio*" }
        if ($vs) {
            $vcInstalled = $true
        }
    }
    catch {
        # Unable to check, assume it's available
        $vcInstalled = $true
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-Warning "Missing dependencies: $($missingDeps -join ', ')"
        
        if (Read-YesNo "Install missing dependencies?") {
            Install-SystemDependencies $missingDeps
        }
        else {
            Write-ErrorMsg "Dependencies are required for installation"
            exit 1
        }
    }
    else {
        Write-Success "All system dependencies are available"
    }
}

function Install-SystemDependencies {
    param([string[]]$Dependencies)
    
    Write-Step "Installing system dependencies: $($Dependencies -join ', ')"
    
    # Check for winget
    if (Test-Command "winget") {
        foreach ($dep in $Dependencies) {
            switch ($dep) {
                "Git" {
                    Write-Info "Installing Git via winget..."
                    & winget install Git.Git --silent
                }
                default {
                    Write-Warning "Don't know how to install: $dep"
                }
            }
        }
    }
    # Check for Chocolatey
    elseif (Test-Command "choco") {
        foreach ($dep in $Dependencies) {
            switch ($dep) {
                "Git" {
                    Write-Info "Installing Git via Chocolatey..."
                    & choco install git -y
                }
                default {
                    Write-Warning "Don't know how to install: $dep"
                }
            }
        }
    }
    else {
        Write-ErrorMsg "No package manager found. Please install dependencies manually:"
        foreach ($dep in $Dependencies) {
            switch ($dep) {
                "Git" {
                    Write-Info "  Git: https://git-scm.com/download/win"
                }
            }
        }
        exit 1
    }
    
    Write-Success "System dependencies installed"
}

# =============================================================================
# Installation Functions
# =============================================================================

function Initialize-InstallationDirectory {
    Write-Step "Setting up installation directory"
    
    New-DirectoryIfNotExists $InstallDir
    New-DirectoryIfNotExists (Join-Path $InstallDir "data")
    New-DirectoryIfNotExists (Join-Path $InstallDir "logs")
    New-DirectoryIfNotExists (Join-Path $InstallDir "config")
    New-DirectoryIfNotExists (Join-Path $InstallDir "cache")
    
    Write-Success "Installation directory created: $InstallDir"
}

function New-VirtualEnvironment {
    Write-Step "Creating Python virtual environment"
    
    if (Test-Path $Script:VenvDir) {
        Write-Warning "Virtual environment already exists"
        if (Read-YesNo "Remove existing virtual environment and create new one?") {
            Remove-Item -Path $Script:VenvDir -Recurse -Force
        }
        else {
            Write-Info "Using existing virtual environment"
            return
        }
    }
    
    # Create virtual environment
    & $Script:PythonCmd -m venv $Script:VenvDir
    
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to create virtual environment"
        exit 1
    }
    
    # Get paths to virtual environment executables
    $Script:VenvPython = Join-Path $Script:VenvDir "Scripts\python.exe"
    $Script:VenvPip = Join-Path $Script:VenvDir "Scripts\pip.exe"
    
    # Upgrade pip
    & $Script:VenvPip install --upgrade pip setuptools wheel
    
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to upgrade pip"
        exit 1
    }
    
    Write-Success "Virtual environment created and activated"
}

function Install-Cognitron {
    Write-Step "Installing Cognitron $CognitronVersion"
    
    # Install Cognitron with all dependencies
    if ($Dev -and $env:COGNITRON_DEV) {
        Write-Info "Installing development version from source"
        & $Script:VenvPip install -e "$env:COGNITRON_DEV[dev]"
    }
    else {
        Write-Info "Installing from PyPI"
        & $Script:VenvPip install "$Script:PyPiPackage==$CognitronVersion"
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to install Cognitron"
        exit 1
    }
    
    Write-Success "Cognitron installed successfully"
}

function New-Configuration {
    Write-Step "Creating default configuration"
    
    $configFile = Join-Path $InstallDir "config\config.yaml"
    
    if (Test-Path $configFile) {
        Write-Warning "Configuration file already exists"
        if (-not (Read-YesNo "Overwrite existing configuration?")) {
            return
        }
    }
    
    $configContent = @"
# Cognitron Medical-Grade Configuration
# Version: 1.0.0

# Medical-Grade Quality Thresholds
confidence:
  critical_threshold: 0.95      # Critical decisions (medical-grade)
  production_threshold: 0.85    # Production use
  display_threshold: 0.70       # Display minimum
  storage_threshold: 0.85       # Case memory storage

# Processing Configuration
processing:
  max_context_length: 4000      # Maximum context per query
  chunk_overlap: 200            # Text chunking overlap
  parallel_processing: true     # Enable parallel processing
  cache_enabled: true           # Enable response caching
  local_processing_only: true   # Force local processing

# Privacy and Security
privacy:
  encrypt_storage: true         # Encrypt stored data
  audit_logging: true           # Enable audit trails
  anonymize_logs: true          # Anonymize log entries
  data_retention_days: 90       # Data retention period

# Performance Tuning
performance:
  max_memory_usage: "2GB"       # Memory limit
  index_compression: true       # Compress search indices
  background_indexing: true     # Index in background
  cache_size: "500MB"          # Response cache size

# Monitoring and Health
monitoring:
  enable_metrics: true          # Prometheus metrics
  health_checks: true          # Health check endpoints
  log_level: "INFO"            # Logging level
  log_format: "structured"     # Log format

# LLM Provider Configuration (optional)
llm:
  primary_provider: "openai"    # Primary LLM provider
  fallback_providers: []       # Fallback providers
  
  providers:
    openai:
      model: "gpt-4"
      confidence_tracking: true
    
    google:
      model: "gemini-pro" 
      confidence_tracking: true
"@
    
    New-DirectoryIfNotExists (Split-Path $configFile)
    Set-Content -Path $configFile -Value $configContent
    
    Write-Success "Configuration file created: $configFile"
}

function Add-EnvironmentPath {
    Write-Step "Adding Cognitron to PATH"
    
    $scriptsDir = Join-Path $Script:VenvDir "Scripts"
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    if ($userPath -notlike "*$scriptsDir*") {
        $newPath = "$scriptsDir;$userPath"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        
        # Also update current session
        $env:PATH = "$scriptsDir;$env:PATH"
        
        Write-Success "Added Cognitron to user PATH"
    }
    else {
        Write-Info "Cognitron already in PATH"
    }
}

function New-StartMenuShortcut {
    Write-Step "Creating Start Menu shortcut"
    
    $startMenuDir = [System.IO.Path]::Combine($env:APPDATA, "Microsoft", "Windows", "Start Menu", "Programs")
    $shortcutPath = [System.IO.Path]::Combine($startMenuDir, "Cognitron.lnk")
    
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($shortcutPath)
        $Shortcut.TargetPath = Join-Path $Script:VenvDir "Scripts\cognitron.exe"
        $Shortcut.Description = "Medical-Grade Personal Knowledge Assistant"
        $Shortcut.WorkingDirectory = $InstallDir
        $Shortcut.Save()
        
        Write-Success "Start Menu shortcut created"
    }
    catch {
        Write-Warning "Failed to create Start Menu shortcut: $_"
    }
}

function Invoke-PostInstallSetup {
    Write-Step "Running post-installation setup"
    
    $cognitronExe = Join-Path $Script:VenvDir "Scripts\cognitron.exe"
    
    # Initialize Cognitron
    & $cognitronExe setup --data-dir (Join-Path $InstallDir "data") --config-dir (Join-Path $InstallDir "config")
    
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Cognitron setup failed"
    }
    
    # Run health check
    & $cognitronExe health-check --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Cognitron health check passed"
    }
    else {
        Write-Warning "Cognitron health check failed - check configuration"
    }
    
    Write-Success "Post-installation setup completed"
}

# =============================================================================
# Interactive Configuration
# =============================================================================

function Set-ApiKeys {
    Write-Step "Configuring API keys (optional)"
    
    if (-not (Read-YesNo "Would you like to configure API keys for enhanced confidence tracking?")) {
        return
    }
    
    $envFile = Join-Path $InstallDir ".env"
    
    $envContent = @"
# Cognitron API Keys
# Generated: $(Get-Date)

"@
    
    # OpenAI API Key
    if (Read-YesNo "Configure OpenAI API key?") {
        $openaiKey = Read-Host "Enter OpenAI API key" -MaskInput
        if (![string]::IsNullOrEmpty($openaiKey)) {
            $envContent += "OPENAI_API_KEY=$openaiKey`n"
            Write-Success "OpenAI API key configured"
        }
    }
    
    # Google API Key
    if (Read-YesNo "Configure Google Gemini API key?") {
        $googleKey = Read-Host "Enter Google API key" -MaskInput
        if (![string]::IsNullOrEmpty($googleKey)) {
            $envContent += "GOOGLE_API_KEY=$googleKey`n"
            Write-Success "Google API key configured"
        }
    }
    
    Set-Content -Path $envFile -Value $envContent
    
    # Set secure permissions (Windows equivalent)
    $acl = Get-Acl $envFile
    $acl.SetAccessRuleProtection($true, $false)  # Disable inheritance
    $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
    $acl.SetAccessRule($accessRule)
    Set-Acl $envFile $acl
}

function Set-KnowledgeIndexing {
    Write-Step "Configuring knowledge indexing"
    
    if (-not (Read-YesNo "Would you like to index your knowledge base now?")) {
        return
    }
    
    $cognitronExe = Join-Path $Script:VenvDir "Scripts\cognitron.exe"
    
    $defaultPaths = @(
        "$env:USERPROFILE\Documents",
        "$env:USERPROFILE\Desktop",
        "$env:USERPROFILE\code",
        "$env:USERPROFILE\projects"
    )
    
    $indexPaths = @()
    
    Write-Host "Select directories to index:" -ForegroundColor Cyan
    foreach ($path in $defaultPaths) {
        if (Test-Path $path) {
            if (Read-YesNo "Index $path?") {
                $indexPaths += $path
            }
        }
    }
    
    # Custom paths
    while (Read-YesNo "Add custom directory?") {
        $customPath = Read-Host "Enter directory path"
        if (Test-Path $customPath) {
            $indexPaths += $customPath
        }
        else {
            Write-Warning "Directory does not exist: $customPath"
        }
    }
    
    if ($indexPaths.Count -gt 0) {
        Write-Info "Indexing directories: $($indexPaths -join ', ')"
        & $cognitronExe index $indexPaths --verbose
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Knowledge indexing completed"
        }
        else {
            Write-Warning "Knowledge indexing failed"
        }
    }
}

# =============================================================================
# Uninstall Function
# =============================================================================

function Uninstall-Cognitron {
    Write-Step "Uninstalling Cognitron"
    
    if (-not (Test-Path $InstallDir)) {
        Write-ErrorMsg "Cognitron installation not found at $InstallDir"
        exit 1
    }
    
    Write-Host "WARNING: This will remove all Cognitron data and configuration" -ForegroundColor Red
    if (-not (Read-YesNo "Are you sure you want to uninstall Cognitron?" "N")) {
        Write-Info "Uninstall cancelled"
        exit 0
    }
    
    # Remove from PATH
    $scriptsDir = Join-Path $Script:VenvDir "Scripts"
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($userPath -like "*$scriptsDir*") {
        $newPath = $userPath.Replace("$scriptsDir;", "").Replace(";$scriptsDir", "")
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    }
    
    # Remove Start Menu shortcut
    $shortcutPath = [System.IO.Path]::Combine($env:APPDATA, "Microsoft", "Windows", "Start Menu", "Programs", "Cognitron.lnk")
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
    }
    
    # Remove installation directory
    Remove-Item -Path $InstallDir -Recurse -Force
    
    Write-Success "Cognitron uninstalled successfully"
    Write-Info "Please restart your PowerShell session to complete the uninstall process"
}

# =============================================================================
# Update Function
# =============================================================================

function Update-Cognitron {
    Write-Step "Updating Cognitron"
    
    if (-not (Test-Path $Script:VenvDir)) {
        Write-ErrorMsg "Cognitron installation not found. Please run installation first."
        exit 1
    }
    
    $cognitronExe = Join-Path $Script:VenvDir "Scripts\cognitron.exe"
    $venvPip = Join-Path $Script:VenvDir "Scripts\pip.exe"
    
    # Check current version
    try {
        $currentVersion = & $cognitronExe --version 2>$null | Select-String "[\d\.]+$" | ForEach-Object { $_.Matches.Value }
        Write-Info "Current version: $currentVersion"
    }
    catch {
        $currentVersion = "unknown"
        Write-Info "Current version: $currentVersion"
    }
    
    # Update package
    & $venvPip install --upgrade $Script:PyPiPackage
    
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to update Cognitron"
        exit 1
    }
    
    # Check new version
    try {
        $newVersion = & $cognitronExe --version 2>$null | Select-String "[\d\.]+$" | ForEach-Object { $_.Matches.Value }
        Write-Success "Updated to version: $newVersion"
    }
    catch {
        Write-Success "Update completed"
    }
    
    # Run migration if needed
    try {
        & $cognitronExe migrate --check-needed 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Step "Running migration"
            & $cognitronExe migrate --backup
            Write-Success "Migration completed"
        }
    }
    catch {
        # Migration not needed or not available
    }
}

# =============================================================================
# Main Installation Flow
# =============================================================================

function Start-MainInstall {
    Write-Header
    
    # Setup logging
    New-DirectoryIfNotExists (Split-Path $Script:LogFile)
    Write-Log "Starting Cognitron installation - Version $Script:ScriptVersion"
    
    try {
        # System checks
        Test-WindowsVersion
        Test-PowerShellVersion
        Find-Python
        Test-Dependencies
        
        # Installation
        Initialize-InstallationDirectory
        New-VirtualEnvironment
        Install-Cognitron
        New-Configuration
        Add-EnvironmentPath
        New-StartMenuShortcut
        Invoke-PostInstallSetup
        
        # Interactive configuration
        if (-not $Quiet) {
            Set-ApiKeys
            Set-KnowledgeIndexing
        }
        
        # Success message
        Write-Host ""
        Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║  🎉 COGNITRON INSTALLATION COMPLETED SUCCESSFULLY!                          ║" -ForegroundColor Green
        Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Installation Details:" -ForegroundColor White
        Write-Host "  📁 Install Directory: $InstallDir" -ForegroundColor Gray
        Write-Host "  🐍 Python Version: $Script:PythonVersion" -ForegroundColor Gray
        Write-Host "  🧠 Cognitron Version: $CognitronVersion" -ForegroundColor Gray
        Write-Host "  📋 Log File: $Script:LogFile" -ForegroundColor Gray
        
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor White
        Write-Host "  1. Restart PowerShell or run: " -ForegroundColor Gray -NoNewline
        Write-Host "refreshenv" -ForegroundColor Cyan
        Write-Host "  2. Verify installation: " -ForegroundColor Gray -NoNewline
        Write-Host "cognitron --version" -ForegroundColor Cyan
        Write-Host "  3. Check system status: " -ForegroundColor Gray -NoNewline
        Write-Host "cognitron status" -ForegroundColor Cyan
        Write-Host "  4. Start using Cognitron: " -ForegroundColor Gray -NoNewline
        Write-Host 'cognitron ask "How does this work?"' -ForegroundColor Cyan
        
        Write-Host ""
        Write-Host "Documentation:" -ForegroundColor White
        Write-Host "  📖 User Guide: https://docs.cognitron.ai" -ForegroundColor Gray
        Write-Host "  💬 Community: https://discord.gg/cognitron" -ForegroundColor Gray
        Write-Host "  🐛 Issues: https://github.com/cognitron-ai/cognitron/issues" -ForegroundColor Gray
        
        Write-Host ""
        Write-Host "Experience medical-grade AI reliability with Cognitron!" -ForegroundColor Cyan
        Write-Host ""
    }
    catch {
        Write-ErrorMsg "Installation failed: $_"
        Write-Info "Check log file: $Script:LogFile"
        Write-Info "You can retry installation or report issues at: $Script:GitHubRepo/issues"
        exit 1
    }
}

# =============================================================================
# Command Line Interface
# =============================================================================

function Show-Help {
    Write-Host "Cognitron Installation Script v$Script:ScriptVersion"
    Write-Host ""
    Write-Host "Usage: .\install.ps1 [Action] [Options]"
    Write-Host ""
    Write-Host "Actions:"
    Write-Host "  install     Install Cognitron (default)"
    Write-Host "  uninstall   Remove Cognitron completely"
    Write-Host "  update      Update existing Cognitron installation"
    Write-Host "  help        Show this help message"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -InstallDir <path>      Installation directory (default: ~/.cognitron)"
    Write-Host "  -CognitronVersion <ver> Version to install (default: $CognitronVersion)"
    Write-Host "  -Force                  Force installation without prompts"
    Write-Host "  -Quiet                  Suppress output"
    Write-Host "  -Dev                    Install development version"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\install.ps1                                    # Install Cognitron"
    Write-Host "  .\install.ps1 install                           # Install Cognitron"
    Write-Host "  .\install.ps1 update                            # Update Cognitron"
    Write-Host "  .\install.ps1 uninstall                         # Uninstall Cognitron"
    Write-Host "  .\install.ps1 -InstallDir C:\Tools\Cognitron    # Install to custom directory"
    Write-Host "  .\install.ps1 -Force -Quiet                     # Silent installation"
}

# =============================================================================
# Main Script Logic
# =============================================================================

# Set error action preference
$ErrorActionPreference = "Stop"

# Handle script arguments
switch ($Action.ToLower()) {
    "install" {
        Start-MainInstall
    }
    "uninstall" {
        Uninstall-Cognitron
    }
    "update" {
        Update-Cognitron
    }
    "help" {
        Show-Help
    }
    default {
        Write-ErrorMsg "Unknown action: $Action"
        Show-Help
        exit 1
    }
}