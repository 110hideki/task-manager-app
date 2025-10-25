#!/bin/bash

# Test script to verify both MongoDB connection methods work correctly
# This script tests:
# 1. Individual variables method (new primary approach)
# 2. MONGODB_URI method (backward compatibility)

echo "🧪 Testing MongoDB Connection Methods"
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test health endpoint
test_health() {
    local port=$1
    local method=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}Testing $method (port $port)...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $method: Health check passed${NC}"
            
            # Test the ready endpoint (includes MongoDB connectivity)
            if curl -s -f "http://localhost:$port/ready" > /dev/null 2>&1; then
                echo -e "${GREEN}✅ $method: Ready check passed (MongoDB connected)${NC}"
                return 0
            else
                echo -e "${RED}❌ $method: Ready check failed (MongoDB not connected)${NC}"
                return 1
            fi
        fi
        
        echo "   Attempt $attempt/$max_attempts - waiting for service..."
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ $method: Service not available after $max_attempts attempts${NC}"
    return 1
}

# Function to check logs for connection method
check_connection_method() {
    local container=$1
    local expected_method=$2
    
    echo -e "${YELLOW}Checking connection method used by $container...${NC}"
    
    # Wait a moment for logs to appear
    sleep 2
    
    # Check logs for connection method
    if docker logs "$container" 2>&1 | grep -q "$expected_method"; then
        echo -e "${GREEN}✅ $container: Using $expected_method as expected${NC}"
        return 0
    else
        echo -e "${RED}❌ $container: Not using $expected_method${NC}"
        echo "Actual logs:"
        docker logs "$container" 2>&1 | grep -i "mongodb\|connection\|using"
        return 1
    fi
}

# Start the test
echo "Starting MongoDB connection method tests..."
echo

# Build the application if needed
echo "Building application..."
docker-compose -f docker-compose.mongodb-uri.yml build

# Start services
echo "Starting services..."
docker-compose -f docker-compose.mongodb-uri.yml up -d

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to start..."
sleep 10

echo
echo "🔍 Testing Connection Methods"
echo "-----------------------------"

# Test Method 1: Individual Variables (port 5002)
echo "1. Testing Individual Variables Method..."
test_health 5002 "Individual Variables"
individual_vars_result=$?

# Test Method 2: MONGODB_URI (port 5003)  
echo
echo "2. Testing MONGODB_URI Method..."
test_health 5003 "MONGODB_URI"
uri_result=$?

echo
echo "🔍 Verifying Connection Methods Used"
echo "-----------------------------------"

# Check that each container uses the expected connection method
check_connection_method "task-manager-app-individual" "individual variables"
individual_method_result=$?

check_connection_method "task-manager-app-uri" "MONGODB_URI"
uri_method_result=$?

# Summary
echo
echo "📊 Test Results Summary"
echo "======================="

if [ $individual_vars_result -eq 0 ]; then
    echo -e "${GREEN}✅ Individual Variables Method: PASSED${NC}"
else
    echo -e "${RED}❌ Individual Variables Method: FAILED${NC}"
fi

if [ $uri_result -eq 0 ]; then
    echo -e "${GREEN}✅ MONGODB_URI Method: PASSED${NC}"
else
    echo -e "${RED}❌ MONGODB_URI Method: FAILED${NC}"
fi

if [ $individual_method_result -eq 0 ]; then
    echo -e "${GREEN}✅ Individual Variables Detection: PASSED${NC}"
else
    echo -e "${RED}❌ Individual Variables Detection: FAILED${NC}"
fi

if [ $uri_method_result -eq 0 ]; then
    echo -e "${GREEN}✅ MONGODB_URI Detection: PASSED${NC}"
else
    echo -e "${RED}❌ MONGODB_URI Detection: FAILED${NC}"
fi

echo
echo "🌐 Access URLs:"
echo "Individual Variables: http://localhost:5002"
echo "MONGODB_URI:         http://localhost:5003"

echo
echo "🧹 Cleanup:"
echo "To stop services: docker-compose -f docker-compose.mongodb-uri.yml down"

# Calculate overall result
if [ $individual_vars_result -eq 0 ] && [ $uri_result -eq 0 ] && [ $individual_method_result -eq 0 ] && [ $uri_method_result -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests PASSED! Both connection methods work correctly.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests FAILED. Please check the output above.${NC}"
    exit 1
fi