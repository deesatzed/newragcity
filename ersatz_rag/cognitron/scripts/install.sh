#!/bin/bash

# Cognitron Installation Script for Linux/macOS
# Medical-Grade Personal Knowledge Assistant
# Version: 1.0.0

set -euo pipefail  # Exit on any error, undefined variable, or pipe failure

# =============================================================================
# Configuration and Constants
# =============================================================================

readonly SCRIPT_VERSION="1.0.0"
readonly COGNITRON_VERSION="${COGNITRON_VERSION:-1.0.0}"
readonly PYTHON_MIN_VERSION="3.11"
readonly INSTALL_DIR="${INSTALL_DIR:-$HOME/.cognitron}"
readonly VENV_DIR="${INSTALL_DIR}/venv"
readonly LOG_FILE="${INSTALL_DIR}/install.log"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# Installation URLs
readonly GITHUB_REPO="https://github.com/cognitron-ai/cognitron"
readonly PYPI_PACKAGE="cognitron"

# =============================================================================
# Utility Functions
# =============================================================================

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "${LOG_FILE}" 2>/dev/null || true
}

print_header() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                              ║"
    echo "║   🧠 COGNITRON INSTALLER                                                     ║"
    echo "║   Medical-Grade Personal Knowledge Assistant                                 ║"
    echo "║                                                                              ║"
    echo "║   Version: ${COGNITRON_VERSION}                                                                ║"
    echo "║   Platform: $(uname -s) $(uname -m)                                                  ║"
    echo "║                                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
    log "STEP: $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    log "ERROR: $1"
}

print_info() {
    echo -e "${WHITE}[INFO]${NC} $1"
    log "INFO: $1"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

version_greater_equal() {
    printf '%s\n%s\n' "$2" "$1" | sort -V | head -n1 | grep -q "^$2$"
}

ask_yes_no() {
    local prompt="$1"
    local default="${2:-y}"
    
    if [[ "$default" == "y" ]]; then
        prompt="${prompt} [Y/n]: "
    else
        prompt="${prompt} [y/N]: "
    fi
    
    while true; do
        read -p "$(echo -e "${YELLOW}${prompt}${NC}")" choice
        case "${choice,,}" in
            y|yes) return 0 ;;
            n|no) return 1 ;;
            "") [[ "$default" == "y" ]] && return 0 || return 1 ;;
            *) echo -e "${RED}Please answer yes or no.${NC}" ;;
        esac
    done
}

create_directory() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
        log "Created directory: $dir"
    fi
}

cleanup_on_exit() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        print_error "Installation failed. Check log file: ${LOG_FILE}"
        print_info "You can retry installation or report issues at: ${GITHUB_REPO}/issues"
    fi
    exit $exit_code
}

# =============================================================================
# System Detection and Requirements
# =============================================================================

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists lsb_release; then
            OS_DISTRO=$(lsb_release -si)
            OS_VERSION=$(lsb_release -sr)
        elif [[ -f /etc/os-release ]]; then
            . /etc/os-release
            OS_DISTRO="$ID"
            OS_VERSION="$VERSION_ID"
        else
            OS_DISTRO="Unknown Linux"
            OS_VERSION="Unknown"
        fi
        OS_TYPE="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_DISTRO="macOS"
        OS_VERSION=$(sw_vers -productVersion)
        OS_TYPE="macos"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    print_info "Detected OS: ${OS_DISTRO} ${OS_VERSION}"
}

check_architecture() {
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64|amd64)
            ARCH_NORMALIZED="amd64"
            ;;
        arm64|aarch64)
            ARCH_NORMALIZED="arm64"
            ;;
        *)
            print_warning "Architecture ${ARCH} may not be fully supported"
            ARCH_NORMALIZED="$ARCH"
            ;;
    esac
    
    print_info "Architecture: ${ARCH} (normalized: ${ARCH_NORMALIZED})"
}

check_python() {
    print_step "Checking Python installation"
    
    local python_cmd=""
    local python_version=""
    
    # Try different Python commands
    for cmd in python3.12 python3.11 python3 python; do
        if command_exists "$cmd"; then
            python_version=$($cmd -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
            if version_greater_equal "$python_version" "$PYTHON_MIN_VERSION"; then
                python_cmd="$cmd"
                break
            fi
        fi
    done
    
    if [[ -z "$python_cmd" ]]; then
        print_error "Python ${PYTHON_MIN_VERSION}+ not found"
        print_info "Please install Python ${PYTHON_MIN_VERSION} or later:"
        
        if [[ "$OS_TYPE" == "macos" ]]; then
            print_info "  brew install python@3.11"
            print_info "  or download from: https://www.python.org/downloads/"
        elif [[ "$OS_TYPE" == "linux" ]]; then
            case "$OS_DISTRO" in
                Ubuntu|Debian)
                    print_info "  sudo apt update && sudo apt install python3.11 python3.11-venv python3.11-pip"
                    ;;
                CentOS|RHEL|Fedora)
                    print_info "  sudo dnf install python3.11 python3.11-venv python3.11-pip"
                    ;;
                *)
                    print_info "  Use your distribution's package manager to install Python ${PYTHON_MIN_VERSION}+"
                    ;;
            esac
        fi
        exit 1
    fi
    
    PYTHON_CMD="$python_cmd"
    PYTHON_VERSION="$python_version"
    print_success "Found Python ${PYTHON_VERSION} at $(command -v "$python_cmd")"
}

check_dependencies() {
    print_step "Checking system dependencies"
    
    local missing_deps=()
    
    # Required tools
    local required_tools=("curl" "git")
    
    if [[ "$OS_TYPE" == "linux" ]]; then
        required_tools+=("gcc" "make")
        
        # Check for development headers
        if ! pkg-config --exists libffi; then
            missing_deps+=("libffi-dev")
        fi
        
        if ! pkg-config --exists openssl; then
            missing_deps+=("libssl-dev")
        fi
    elif [[ "$OS_TYPE" == "macos" ]]; then
        # Check for Xcode Command Line Tools
        if ! xcode-select -p &>/dev/null; then
            print_warning "Xcode Command Line Tools not found"
            if ask_yes_no "Install Xcode Command Line Tools?"; then
                xcode-select --install
                print_info "Please complete the Xcode Command Line Tools installation and re-run this script"
                exit 0
            fi
        fi
    fi
    
    # Check for missing tools
    for tool in "${required_tools[@]}"; do
        if ! command_exists "$tool"; then
            missing_deps+=("$tool")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_warning "Missing dependencies: ${missing_deps[*]}"
        
        if ask_yes_no "Install missing dependencies?"; then
            install_system_dependencies "${missing_deps[@]}"
        else
            print_error "Dependencies are required for installation"
            exit 1
        fi
    else
        print_success "All system dependencies are available"
    fi
}

install_system_dependencies() {
    local deps=("$@")
    print_step "Installing system dependencies: ${deps[*]}"
    
    case "$OS_DISTRO" in
        Ubuntu|Debian)
            sudo apt update
            sudo apt install -y "${deps[@]}" python3.11-dev python3.11-venv python3.11-pip
            ;;
        CentOS|RHEL)
            sudo yum install -y "${deps[@]}" python3.11-devel
            ;;
        Fedora)
            sudo dnf install -y "${deps[@]}" python3.11-devel
            ;;
        macOS)
            if command_exists brew; then
                brew install "${deps[@]}"
            else
                print_error "Homebrew is required to install dependencies on macOS"
                print_info "Install Homebrew from: https://brew.sh/"
                exit 1
            fi
            ;;
        *)
            print_error "Cannot automatically install dependencies for ${OS_DISTRO}"
            print_info "Please install manually: ${deps[*]}"
            exit 1
            ;;
    esac
    
    print_success "System dependencies installed"
}

# =============================================================================
# Installation Functions
# =============================================================================

setup_installation_directory() {
    print_step "Setting up installation directory"
    
    create_directory "$INSTALL_DIR"
    create_directory "$INSTALL_DIR/data"
    create_directory "$INSTALL_DIR/logs"
    create_directory "$INSTALL_DIR/config"
    create_directory "$INSTALL_DIR/cache"
    
    # Set secure permissions
    chmod 755 "$INSTALL_DIR"
    chmod 750 "$INSTALL_DIR/data" "$INSTALL_DIR/logs" "$INSTALL_DIR/config"
    chmod 755 "$INSTALL_DIR/cache"
    
    print_success "Installation directory created: ${INSTALL_DIR}"
}

create_virtual_environment() {
    print_step "Creating Python virtual environment"
    
    if [[ -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment already exists"
        if ask_yes_no "Remove existing virtual environment and create new one?"; then
            rm -rf "$VENV_DIR"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    
    # Activate virtual environment
    # shellcheck source=/dev/null
    source "${VENV_DIR}/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    print_success "Virtual environment created and activated"
}

install_cognitron() {
    print_step "Installing Cognitron ${COGNITRON_VERSION}"
    
    # shellcheck source=/dev/null
    source "${VENV_DIR}/bin/activate"
    
    # Install Cognitron with all dependencies
    if [[ -n "${COGNITRON_DEV:-}" ]]; then
        print_info "Installing development version from source"
        pip install -e "${COGNITRON_DEV}[dev]"
    else
        print_info "Installing from PyPI"
        pip install "${PYPI_PACKAGE}==${COGNITRON_VERSION}"
    fi
    
    print_success "Cognitron installed successfully"
}

create_configuration() {
    print_step "Creating default configuration"
    
    local config_file="${INSTALL_DIR}/config/config.yaml"
    
    if [[ -f "$config_file" ]]; then
        print_warning "Configuration file already exists"
        if ! ask_yes_no "Overwrite existing configuration?"; then
            return 0
        fi
    fi
    
    cat > "$config_file" << 'EOF'
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
EOF
    
    print_success "Configuration file created: ${config_file}"
}

create_shell_integration() {
    print_step "Setting up shell integration"
    
    local shell_name=$(basename "$SHELL")
    local profile_file=""
    
    case "$shell_name" in
        bash)
            if [[ -f "$HOME/.bash_profile" ]]; then
                profile_file="$HOME/.bash_profile"
            else
                profile_file="$HOME/.bashrc"
            fi
            ;;
        zsh)
            profile_file="$HOME/.zshrc"
            ;;
        fish)
            profile_file="$HOME/.config/fish/config.fish"
            ;;
        *)
            print_warning "Unsupported shell: ${shell_name}"
            return 0
            ;;
    esac
    
    if [[ -n "$profile_file" ]]; then
        local cognitron_init="
# Cognitron Medical-Grade Personal Knowledge Assistant
export COGNITRON_HOME=\"${INSTALL_DIR}\"
export PATH=\"${VENV_DIR}/bin:\$PATH\"

# Cognitron aliases
alias cognitron=\"${VENV_DIR}/bin/cognitron\"
alias cgn=\"${VENV_DIR}/bin/cognitron\"
"
        
        if ! grep -q "COGNITRON_HOME" "$profile_file" 2>/dev/null; then
            echo "$cognitron_init" >> "$profile_file"
            print_success "Shell integration added to ${profile_file}"
        else
            print_info "Shell integration already configured"
        fi
    fi
}

create_desktop_entry() {
    print_step "Creating desktop entry (Linux only)"
    
    if [[ "$OS_TYPE" != "linux" ]]; then
        return 0
    fi
    
    local desktop_file="$HOME/.local/share/applications/cognitron.desktop"
    
    create_directory "$(dirname "$desktop_file")"
    
    cat > "$desktop_file" << EOF
[Desktop Entry]
Version=1.0
Name=Cognitron
Comment=Medical-Grade Personal Knowledge Assistant
Exec=${VENV_DIR}/bin/cognitron gui
Icon=${INSTALL_DIR}/icon.png
Terminal=false
Type=Application
Categories=Office;Education;Science;
StartupNotify=true
MimeType=text/plain;text/markdown;application/pdf;
Keywords=ai;knowledge;assistant;medical;confidence;
EOF
    
    chmod +x "$desktop_file"
    
    print_success "Desktop entry created: ${desktop_file}"
}

run_post_install_setup() {
    print_step "Running post-installation setup"
    
    # shellcheck source=/dev/null
    source "${VENV_DIR}/bin/activate"
    
    # Initialize Cognitron
    cognitron setup --data-dir "${INSTALL_DIR}/data" --config-dir "${INSTALL_DIR}/config"
    
    # Run health check
    if cognitron health-check --quiet; then
        print_success "Cognitron health check passed"
    else
        print_warning "Cognitron health check failed - check configuration"
    fi
    
    print_success "Post-installation setup completed"
}

# =============================================================================
# Interactive Configuration
# =============================================================================

configure_api_keys() {
    print_step "Configuring API keys (optional)"
    
    if ! ask_yes_no "Would you like to configure API keys for enhanced confidence tracking?"; then
        return 0
    fi
    
    local env_file="${INSTALL_DIR}/.env"
    
    echo "# Cognitron API Keys" > "$env_file"
    echo "# Generated: $(date)" >> "$env_file"
    echo "" >> "$env_file"
    
    # OpenAI API Key
    if ask_yes_no "Configure OpenAI API key?"; then
        read -p "Enter OpenAI API key: " -s openai_key
        echo ""
        if [[ -n "$openai_key" ]]; then
            echo "OPENAI_API_KEY=${openai_key}" >> "$env_file"
            print_success "OpenAI API key configured"
        fi
    fi
    
    # Google API Key
    if ask_yes_no "Configure Google Gemini API key?"; then
        read -p "Enter Google API key: " -s google_key
        echo ""
        if [[ -n "$google_key" ]]; then
            echo "GOOGLE_API_KEY=${google_key}" >> "$env_file"
            print_success "Google API key configured"
        fi
    fi
    
    # Secure the env file
    chmod 600 "$env_file"
}

configure_knowledge_indexing() {
    print_step "Configuring knowledge indexing"
    
    if ask_yes_no "Would you like to index your knowledge base now?"; then
        # shellcheck source=/dev/null
        source "${VENV_DIR}/bin/activate"
        
        local default_paths=(
            "$HOME/Documents"
            "$HOME/code"
            "$HOME/projects"
            "$HOME/notes"
        )
        
        local index_paths=()
        
        echo -e "${CYAN}Select directories to index:${NC}"
        for path in "${default_paths[@]}"; do
            if [[ -d "$path" ]]; then
                if ask_yes_no "Index ${path}?"; then
                    index_paths+=("$path")
                fi
            fi
        done
        
        # Custom paths
        while ask_yes_no "Add custom directory?"; do
            read -p "Enter directory path: " custom_path
            if [[ -d "$custom_path" ]]; then
                index_paths+=("$custom_path")
            else
                print_warning "Directory does not exist: ${custom_path}"
            fi
        done
        
        if [[ ${#index_paths[@]} -gt 0 ]]; then
            print_info "Indexing directories: ${index_paths[*]}"
            cognitron index "${index_paths[@]}" --verbose
            print_success "Knowledge indexing completed"
        fi
    fi
}

# =============================================================================
# Uninstall Function
# =============================================================================

uninstall_cognitron() {
    print_step "Uninstalling Cognitron"
    
    if [[ ! -d "$INSTALL_DIR" ]]; then
        print_error "Cognitron installation not found at ${INSTALL_DIR}"
        exit 1
    fi
    
    echo -e "${RED}WARNING: This will remove all Cognitron data and configuration${NC}"
    if ! ask_yes_no "Are you sure you want to uninstall Cognitron?" "n"; then
        print_info "Uninstall cancelled"
        exit 0
    fi
    
    # Remove installation directory
    rm -rf "$INSTALL_DIR"
    
    # Remove desktop entry
    local desktop_file="$HOME/.local/share/applications/cognitron.desktop"
    if [[ -f "$desktop_file" ]]; then
        rm "$desktop_file"
    fi
    
    # Remove shell integration
    local shell_name=$(basename "$SHELL")
    local profile_file=""
    
    case "$shell_name" in
        bash)
            if [[ -f "$HOME/.bash_profile" ]]; then
                profile_file="$HOME/.bash_profile"
            else
                profile_file="$HOME/.bashrc"
            fi
            ;;
        zsh)
            profile_file="$HOME/.zshrc"
            ;;
    esac
    
    if [[ -n "$profile_file" && -f "$profile_file" ]]; then
        sed -i.bak '/# Cognitron Medical-Grade Personal Knowledge Assistant/,/alias cgn=/d' "$profile_file"
    fi
    
    print_success "Cognitron uninstalled successfully"
    print_info "Please restart your terminal to complete the uninstall process"
}

# =============================================================================
# Update Function
# =============================================================================

update_cognitron() {
    print_step "Updating Cognitron"
    
    if [[ ! -d "$VENV_DIR" ]]; then
        print_error "Cognitron installation not found. Please run installation first."
        exit 1
    fi
    
    # shellcheck source=/dev/null
    source "${VENV_DIR}/bin/activate"
    
    # Check current version
    local current_version
    current_version=$(cognitron --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' || echo "unknown")
    print_info "Current version: ${current_version}"
    
    # Update package
    pip install --upgrade "${PYPI_PACKAGE}"
    
    # Check new version
    local new_version
    new_version=$(cognitron --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' || echo "unknown")
    print_success "Updated to version: ${new_version}"
    
    # Run migration if needed
    if command_exists cognitron && cognitron migrate --check-needed; then
        print_step "Running migration"
        cognitron migrate --backup
        print_success "Migration completed"
    fi
}

# =============================================================================
# Main Installation Flow
# =============================================================================

main_install() {
    print_header
    
    # Setup logging
    create_directory "$(dirname "$LOG_FILE")"
    log "Starting Cognitron installation - Version ${SCRIPT_VERSION}"
    
    # System checks
    detect_os
    check_architecture
    check_python
    check_dependencies
    
    # Installation
    setup_installation_directory
    create_virtual_environment
    install_cognitron
    create_configuration
    create_shell_integration
    create_desktop_entry
    run_post_install_setup
    
    # Interactive configuration
    configure_api_keys
    configure_knowledge_indexing
    
    # Success message
    echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗"
    echo -e "║  🎉 COGNITRON INSTALLATION COMPLETED SUCCESSFULLY!                          ║"
    echo -e "╚══════════════════════════════════════════════════════════════════════════════╝${NC}\n"
    
    echo -e "${WHITE}Installation Details:${NC}"
    echo -e "  📁 Install Directory: ${INSTALL_DIR}"
    echo -e "  🐍 Python Version: ${PYTHON_VERSION}"
    echo -e "  🧠 Cognitron Version: ${COGNITRON_VERSION}"
    echo -e "  📋 Log File: ${LOG_FILE}"
    
    echo -e "\n${WHITE}Next Steps:${NC}"
    echo -e "  1. Restart your terminal or run: ${CYAN}source ~/.bashrc${NC}"
    echo -e "  2. Verify installation: ${CYAN}cognitron --version${NC}"
    echo -e "  3. Check system status: ${CYAN}cognitron status${NC}"
    echo -e "  4. Start using Cognitron: ${CYAN}cognitron ask \"How does this work?\"${NC}"
    
    echo -e "\n${WHITE}Documentation:${NC}"
    echo -e "  📖 User Guide: https://docs.cognitron.ai"
    echo -e "  💬 Community: https://discord.gg/cognitron"
    echo -e "  🐛 Issues: https://github.com/cognitron-ai/cognitron/issues"
    
    echo -e "\n${CYAN}Experience medical-grade AI reliability with Cognitron!${NC}\n"
}

# =============================================================================
# Command Line Interface
# =============================================================================

show_help() {
    echo "Cognitron Installation Script v${SCRIPT_VERSION}"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  install     Install Cognitron (default)"
    echo "  uninstall   Remove Cognitron completely"
    echo "  update      Update existing Cognitron installation"
    echo "  --help      Show this help message"
    echo "  --version   Show script version"
    echo ""
    echo "Environment Variables:"
    echo "  COGNITRON_VERSION    Version to install (default: ${COGNITRON_VERSION})"
    echo "  INSTALL_DIR          Installation directory (default: ~/.cognitron)"
    echo "  COGNITRON_DEV        Install from local source directory"
    echo ""
    echo "Examples:"
    echo "  $0                           # Install Cognitron"
    echo "  $0 install                   # Install Cognitron"
    echo "  $0 update                    # Update Cognitron"
    echo "  $0 uninstall                 # Uninstall Cognitron"
    echo "  INSTALL_DIR=/opt/cognitron $0 # Install to custom directory"
}

# Set up signal handlers
trap cleanup_on_exit EXIT
trap 'exit 130' INT  # Ctrl+C
trap 'exit 143' TERM # Termination

# Parse command line arguments
case "${1:-install}" in
    install)
        main_install
        ;;
    uninstall)
        uninstall_cognitron
        ;;
    update)
        update_cognitron
        ;;
    --help|-h)
        show_help
        ;;
    --version|-v)
        echo "Cognitron Installation Script v${SCRIPT_VERSION}"
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac