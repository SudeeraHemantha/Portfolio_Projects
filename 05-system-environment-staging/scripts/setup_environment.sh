#!/usr/bin/env bash
# ==============================================================================
# Project 05: Staging & Multi-Environment Deployment System
# Script: setup_environment.sh
# Purpose: Cross-OS Automated Environment Provisioning & Parity Validator
# ==============================================================================

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================================${NC}"
echo -e "${BLUE}🚀 Initializing Multi-Environment Staging Provisioning Engine...${NC}"
echo -e "${BLUE}====================================================================${NC}"

# 1. OS Auto-Detection
OS_TYPE="$(uname -s)"
case "${OS_TYPE}" in
    Linux*)     
        if grep -q -i microsoft /proc/version 2>/dev/null; then
            DETECTED_OS="WSL (Windows Subsystem for Linux)"
        else
            DETECTED_OS="Linux (Ubuntu/Debian)"
        fi
        ;;
    Darwin*)    DETECTED_OS="macOS (Darwin)";;
    MINGW*|MSYS*|CYGWIN*) DETECTED_OS="Windows (Git Bash / MSYS)";;
    *)          DETECTED_OS="Unknown (${OS_TYPE})";;
esac

echo -e "${GREEN}✓ Host OS Detected:${NC} ${DETECTED_OS}"

# 2. Check Docker Binary & Daemon
echo -e "${BLUE}🔍 Checking Docker Engine & Daemon availability...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: 'docker' CLI is not installed or not in PATH.${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Error: Docker daemon is not running. Please start Docker Desktop/Engine.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker daemon is active and responsive.${NC}"

# 3. Environment Variable File Generator
ENV_FILE=".env.staging"
if [ ! -f "${ENV_FILE}" ]; then
    echo -e "${YELLOW}⚠️  Staging environment file '${ENV_FILE}' not found. Generating default settings...${NC}"
    cat <<EOF > "${ENV_FILE}"
# Automated Staging Environment Configuration
ENV_NAME=staging
STAGING_API_PORT=8005
STAGING_REDIS_PORT=6385
STAGING_PROXY_PORT=8085
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✓ Created default '${ENV_FILE}' file.${NC}"
else
    echo -e "${GREEN}✓ Staging environment file '${ENV_FILE}' verified.${NC}"
fi

# 4. Spin up Staging Container Parity Stack
echo -e "${BLUE}🐳 Provisioning Staging Containers via Docker Compose...${NC}"
docker compose --env-file "${ENV_FILE}" up -d --build

echo -e "${GREEN}====================================================================${NC}"
echo -e "${GREEN}🎉 Staging Environment Successfully Provisioned!${NC}"
echo -e "${GREEN}====================================================================${NC}"
echo -e "Access API:   http://localhost:8005/health"
echo -e "Access Proxy: http://localhost:8085"
