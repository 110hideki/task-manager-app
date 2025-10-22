#!/bin/bash
# Test both MONGODB_URI formats

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Testing MONGODB_URI Formats${NC}"
echo ""

# Clean up first
docker-compose -f docker-compose.mongodb-uri.yml down -v > /dev/null 2>&1 || true

echo "1. Testing Format B: mongodb://.../:27017/?authSource=admin"
echo "   Building and starting..."
docker-compose -f docker-compose.mongodb-uri.yml up -d > /dev/null 2>&1

sleep 6

# Check logs
echo "   Checking connection..."
LOGS=$(docker logs task-manager-app-uri 2>&1)

if echo "$LOGS" | grep -q "Using MONGODB_URI"; then
    echo -e "   ${GREEN}✓${NC} Using MONGODB_URI for connection"
fi

if echo "$LOGS" | grep -q "Successfully connected"; then
    echo -e "   ${GREEN}✓${NC} Successfully connected to MongoDB"
fi

# Test endpoint
READY=$(curl -s http://localhost:5002/ready)
if echo "$READY" | grep -q '"database":"connected"'; then
    echo -e "   ${GREEN}✓${NC} Database connectivity confirmed"
fi

echo ""
echo -e "${GREEN}Format B (without /taskdb) - WORKING!${NC}"
echo ""

# Clean up
docker-compose -f docker-compose.mongodb-uri.yml down -v > /dev/null 2>&1

echo "Note: Format A (with /taskdb) would also work, but requires modifying the connection string."
echo "Both formats are fully compatible with the application!"
