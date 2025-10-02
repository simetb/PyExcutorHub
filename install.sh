#!/bin/bash

# PyExecutorHub Installer
# The Ultimate Python Execution Platform

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ASCII Art Logo
show_logo() {
    clear
    echo -e "${CYAN}"
    echo "  _____       ______                     _             _    _       _     "
    echo " |  __ \\     |  ____|                   | |           | |  | |     | |    "
    echo " | |__) |   _| |__  __  _____  ___ _   _| |_ ___  _ __| |__| |_   _| |__  "
    echo " |  ___/ | | |  __| \\ \\/ / _ \\/ __| | | | __/ _ \\| '__|  __  | | | | '_ \\" 
    echo " | |   | |_| | |____ >  <  __/ (__| |_| | || (_) | |  | |  | | |_| | |_) |"
    echo " |_|    \\__, |______/_/\\_\\___|\\___|\\__,_|\\__\\___/|_|  |_|  |_|\\__,_|_.__/ "
    echo "         __/ |                                                            "
    echo "        |___/              "
    echo -e "${NC}"
    echo -e "${YELLOW}⚡ Deploy Python scripts in seconds, not hours. Execute with confidence.${NC}"
    echo ""
}

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    print_info "Checking system requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    else
        print_status "Docker is installed"
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    else
        print_status "Docker Compose is installed"
    fi
    
    # Check if Git is installed
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    else
        print_status "Git is installed"
    fi
    
    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed. Please install curl first."
        exit 1
    else
        print_status "curl is installed"
    fi
}

# Configure environment
configure_environment() {
    print_info "Configuring environment..."
    
    # Copy environment file if it doesn't exist
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            print_status "Environment file created from template"
        else
            print_error "env.example not found"
            exit 1
        fi
    else
        print_status "Environment file already exists"
    fi
    
    # Get current directory for HOST_PROJECT_DIR
    CURRENT_DIR=$(pwd)
    
    # Update .env file with current directory
    if grep -q "HOST_PROJECT_DIR" .env; then
        sed -i "s|HOST_PROJECT_DIR=.*|HOST_PROJECT_DIR=$CURRENT_DIR|g" .env
        print_status "Updated HOST_PROJECT_DIR in .env"
    fi
}

# Build and start services
start_services() {
    print_info "Building PyExecutorHub base image..."
    
    # Build base image first
    if docker compose build pyexecutorhub-base; then
        print_status "Base image built successfully"
    else
        print_error "Failed to build base image"
        exit 1
    fi
    
    print_info "Building and starting PyExecutorHub API service..."
    
    # Build and start API service
    if docker compose up -d --build pyexecutorhub-api; then
        print_status "API service started successfully"
    else
        print_error "Failed to start API service"
        exit 1
    fi
}

# Test the installation
test_installation() {
    print_info "Testing installation..."
    
    # Get API port from .env
    API_PORT=$(grep API_PORT .env | cut -d'=' -f2)
    if [ -z "$API_PORT" ]; then
        API_PORT=8001
    fi
    
    # Wait a moment for services to start
    sleep 5
    
    # Test health endpoint
    if curl -s http://localhost:$API_PORT/health > /dev/null; then
        print_status "API is responding"
        echo -e "${GREEN}Health check:${NC} http://localhost:$API_PORT/health"
    else
        print_warning "API health check failed. Services might still be starting..."
    fi
    
    # Test programs endpoint
    if curl -s http://localhost:$API_PORT/programs > /dev/null; then
        print_status "Programs endpoint is working"
        echo -e "${GREEN}Programs:${NC} http://localhost:$API_PORT/programs"
    else
        print_warning "Programs endpoint check failed"
    fi
}

# Show usage information
show_usage() {
    print_info "PyExecutorHub is now running!"
    echo ""
    echo -e "${CYAN}Quick Start:${NC}"
    echo "1. Get credentials from logs:"
    echo "   docker compose logs pyexecutorhub-api | grep -A 5 'CREDENCIALES DE USO'"
    echo ""
    echo "2. Login to get token:"
    echo "   curl -X POST http://localhost:$API_PORT/auth/login \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"username\": \"YOUR_USERNAME\", \"password\": \"YOUR_PASSWORD\"}'"
    echo ""
    echo "3. View available programs:"
    echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" http://localhost:$API_PORT/programs"
    echo ""
    echo "4. Execute a script:"
    echo "   curl -X POST http://localhost:$API_PORT/execute \\"
    echo "     -H \"Authorization: Bearer YOUR_TOKEN\" \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"program_id\": \"example_script\"}'"
    echo ""
    echo -e "${CYAN}Useful Commands:${NC}"
    echo "• View logs: docker compose logs -f pyexecutorhub-api"
    echo "• Stop services: docker compose down"
    echo "• Restart services: docker compose restart"
    echo "• Rebuild base image: docker compose build pyexecutorhub-base"
    echo "• View API docs: http://localhost:$API_PORT/docs"
    echo ""
    echo -e "${YELLOW}Documentation:${NC} README.md"
    echo -e "${YELLOW}Contributing:${NC} CONTRIBUTING.md"
    echo ""
    echo -e "${GREEN}⚡ PyExecutorHub - Deploy Python scripts in seconds, execute with confidence.${NC}"
}

# Main installation function
main() {
    show_logo
    print_info "Starting PyExecutorHub installation..."
    echo ""
    
    check_root
    check_requirements
    echo ""
    
    configure_environment
    echo ""
    
    start_services
    echo ""
    
    test_installation
    echo ""
    
    show_usage
}

# Run main function
main "$@" 