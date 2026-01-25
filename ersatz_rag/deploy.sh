#!/bin/bash
# ERSATZ RAG Deployment Script
# Comprehensive deployment automation for all services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Volumes/WS4TB/ERSATZ_RAG"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi

    # Check if .env file exists
    if [ ! -f "$PROJECT_ROOT/regulus/.env" ]; then
        log_error "Environment file not found: $PROJECT_ROOT/regulus/.env"
        log_info "Please create the .env file with required API keys."
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Build all services
build_services() {
    log_info "Building all services..."
    cd "$PROJECT_ROOT"

    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" build
    else
        docker compose -f "$COMPOSE_FILE" build
    fi

    log_success "Services built successfully"
}

# Start all services
start_services() {
    log_info "Starting all services..."
    cd "$PROJECT_ROOT"

    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" up -d
    else
        docker compose -f "$COMPOSE_FILE" up -d
    fi

    log_success "Services started successfully"
}

# Stop all services
stop_services() {
    log_info "Stopping all services..."
    cd "$PROJECT_ROOT"

    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" down
    else
        docker compose -f "$COMPOSE_FILE" down
    fi

    log_success "Services stopped successfully"
}

# Check service health
check_health() {
    log_info "Checking service health..."

    services=(
        "http://localhost:6333/health:Qdrant"
        "http://localhost:8000/health:PageIndex"
        "http://localhost:8001/health:LEANN"
        "http://localhost:8002/health:deepConf"
        "http://localhost:8003/health:Thalamus"
    )

    for service in "${services[@]}"; do
        url=$(echo $service | cut -d: -f1)
        name=$(echo $service | cut -d: -f2)

        if curl -f -s "$url" > /dev/null 2>&1; then
            log_success "$name service is healthy"
        else
            log_warning "$name service is not responding"
        fi
    done
}

# View logs
view_logs() {
    service_name=$1
    cd "$PROJECT_ROOT"

    if [ -z "$service_name" ]; then
        log_info "Viewing logs for all services..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "$COMPOSE_FILE" logs -f
        else
            docker compose -f "$COMPOSE_FILE" logs -f
        fi
    else
        log_info "Viewing logs for $service_name..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "$COMPOSE_FILE" logs -f "$service_name"
        else
            docker compose -f "$COMPOSE_FILE" logs -f "$service_name"
        fi
    fi
}

# Run tests
run_tests() {
    log_info "Running test suite..."
    cd "$PROJECT_ROOT/tests"

    if [ ! -f "requirements.txt" ]; then
        log_error "Test requirements not found"
        exit 1
    fi

    # Install test dependencies
    pip install -r requirements.txt

    # Run tests
    python -m pytest -v --tb=short

    log_success "Test suite completed"
}

# Clean up
cleanup() {
    log_info "Cleaning up deployment..."
    cd "$PROJECT_ROOT"

    # Stop services
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" down -v
    else
        docker compose -f "$COMPOSE_FILE" down -v
    fi

    # Remove images
    log_info "Removing Docker images..."
    docker images | grep ersatz_rag | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || true

    log_success "Cleanup completed"
}

# Main script logic
case "${1:-help}" in
    "build")
        check_prerequisites
        build_services
        ;;
    "start")
        check_prerequisites
        start_services
        sleep 10
        check_health
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 5
        check_prerequisites
        start_services
        sleep 10
        check_health
        ;;
    "status")
        check_health
        ;;
    "logs")
        view_logs "$2"
        ;;
    "test")
        run_tests
        ;;
    "cleanup")
        cleanup
        ;;
    "deploy")
        check_prerequisites
        build_services
        start_services
        sleep 15
        check_health
        log_success "Deployment completed successfully!"
        log_info "Services are available at:"
        log_info "  - PageIndex: http://localhost:8000"
        log_info "  - LEANN: http://localhost:8001"
        log_info "  - deepConf: http://localhost:8002"
        log_info "  - Thalamus: http://localhost:8003"
        ;;
    "help"|*)
        echo "ERSATZ RAG Deployment Script"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  build     Build all Docker images"
        echo "  start     Start all services"
        echo "  stop      Stop all services"
        echo "  restart   Restart all services"
        echo "  status    Check service health"
        echo "  logs      View service logs (optional: specify service name)"
        echo "  test      Run the test suite"
        echo "  cleanup   Stop services and remove containers/images"
        echo "  deploy    Full deployment (build + start + health check)"
        echo "  help      Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 deploy          # Full deployment"
        echo "  $0 logs pageindex  # View PageIndex logs"
        echo "  $0 test            # Run tests"
        ;;
esac
