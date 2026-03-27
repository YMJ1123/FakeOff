#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# 麥騙 FakeOff — EC2 One-Click Setup Script
#
# Usage:
#   1. Launch an EC2 instance (t3.large, Ubuntu 22.04, 30GB gp3)
#   2. Open Security Group: 22 (SSH), 80 (HTTP), 5678 (n8n, optional)
#   3. SSH in and run:
#        curl -fsSL https://raw.githubusercontent.com/<YOUR_REPO>/main/ec2-setup.sh | bash
#      or copy this script to the instance and run:
#        chmod +x ec2-setup.sh && ./ec2-setup.sh
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/<YOUR_ORG>/AWS_hackathon.git}"
PROJECT_DIR="${PROJECT_DIR:-$HOME/AWS_hackathon}"

echo "══════════════════════════════════════════"
echo "  麥騙 FakeOff — EC2 Setup"
echo "══════════════════════════════════════════"

# ── 1. System updates ─────────────────────────────────────────
echo "[1/5] Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# ── 2. Install Docker ─────────────────────────────────────────
echo "[2/5] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    echo "  Docker installed. You may need to re-login for group changes."
else
    echo "  Docker already installed."
fi

# ── 3. Install Docker Compose plugin ──────────────────────────
echo "[3/5] Installing Docker Compose..."
if ! docker compose version &> /dev/null; then
    sudo apt-get install -y docker-compose-plugin
    echo "  Docker Compose installed."
else
    echo "  Docker Compose already installed."
fi

# ── 4. Clone project ─────────────────────────────────────────
echo "[4/5] Cloning project..."
if [ -d "$PROJECT_DIR" ]; then
    echo "  Project directory exists, pulling latest..."
    cd "$PROJECT_DIR"
    git pull
else
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# ── 5. Configure environment ─────────────────────────────────
echo "[5/5] Setting up environment..."
if [ ! -f .env.production ]; then
    echo ""
    echo "  ⚠  .env.production not found!"
    echo "  Please create it from the template:"
    echo ""
    echo "    cp .env.production.example .env.production"
    echo "    nano .env.production"
    echo ""
    echo "  Then run:"
    echo "    docker compose up -d --build"
    echo ""
    exit 1
fi

# ── Deploy ────────────────────────────────────────────────────
echo ""
echo "Building and starting all services..."
sudo docker compose up -d --build

echo ""
echo "══════════════════════════════════════════"
echo "  Deployment complete!"
echo ""
echo "  Web App:  http://$(curl -s ifconfig.me)"
echo "  n8n:      http://$(curl -s ifconfig.me):5678"
echo ""
echo "  Useful commands:"
echo "    docker compose logs -f        # view all logs"
echo "    docker compose logs -f api    # view API logs only"
echo "    docker compose restart api    # restart API"
echo "    docker compose down           # stop all"
echo "    docker compose up -d --build  # rebuild & restart"
echo "══════════════════════════════════════════"
