#!/usr/bin/env bash
# ==============================================================================
# Project 05: Staging & Multi-Environment Deployment System
# Script: health_check.sh
# Purpose: Diagnostic Environment & Health Verification Suite
# ==============================================================================

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}====================================================================${NC}"
echo -e "${BLUE}🩺 Running Staging Environment Health Diagnostics...${NC}"
echo -e "${BLUE}====================================================================${NC}"

# 1. Inspect Docker Container Statuses
echo -e "${BLUE}📊 Checking active container statuses...${NC}"
docker compose ps

# 2. Test API Health Endpoint (Port 8005)
echo -e "${BLUE}🌐 Testing Staging API endpoint (http://localhost:8005/health)...${NC}"
if command -v curl &> /dev/null; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8005/health || echo "000")
    if [ "${HTTP_STATUS}" -eq 200 ]; then
        echo -e "${GREEN}✓ Staging API Health Check PASSED (HTTP 200 OK)${NC}"
    else
        echo -e "${RED}❌ Staging API Health Check FAILED (HTTP ${HTTP_STATUS})${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ 'curl' command not found, skipping HTTP endpoint test.${NC}"
fi

# 3. Check Redis Ping (Port 6385)
echo -e "${BLUE}🔑 Testing Staging Redis Cache (Port 6385)...${NC}"
if docker exec staging_redis_service redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis Cache Health Check PASSED (PONG)${NC}"
else
    echo -e "${RED}❌ Redis Cache Health Check FAILED${NC}"
fi

echo -e "${GREEN}====================================================================${NC}"
echo -e "${GREEN}🏁 Health Diagnostics Complete.${NC}"
echo -e "${GREEN}====================================================================${NC}"
