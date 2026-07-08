#!/bin/bash
set -e

# ============================================================
# PayPulse VPS Setup Script
# Run as root on a fresh Ubuntu/Debian VPS
# Usage: bash deploy.sh
# ============================================================

DOMAIN_API="api.paypulse.cv"
DOMAIN_DASH="dashboard.paypulse.cv"

echo "============================================"
echo "  PayPulse VPS Deployment"
echo "============================================"

# --- 1. System packages ---
echo "[1/7] Installing system packages..."
apt-get update
apt-get install -y curl git ufw

# --- 2. Docker ---
echo "[2/7] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

# --- 3. Docker Compose ---
echo "[3/7] Installing Docker Compose plugin..."
if ! docker compose version &> /dev/null; then
    apt-get install -y docker-compose-plugin
fi

# --- 4. Firewall ---
echo "[4/7] Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Stop system nginx if running (docker nginx takes over port 80/443)
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "  Stopping system nginx..."
    systemctl stop nginx
    systemctl disable nginx
fi

# --- 5. Clone repo ---
echo "[5/7] Cloning repository..."
if [ ! -d "/opt/paypulse" ]; then
    git clone https://github.com/anomalyco/paypulse.git /opt/paypulse
else
    cd /opt/paypulse && git pull
fi
cd /opt/paypulse

# --- 6. Env file ---
echo "[6/7] Setting up environment..."
if [ ! -f "config/.env.production" ]; then
    echo "ERROR: config/.env.production not found!"
    echo "Create it from the template and fill in your secrets."
    exit 1
fi

# Generate JWT secret if placeholder
if grep -q "CHANGE_ME_TO_RANDOM_64_CHARS" config/.env.production; then
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))" 2>/dev/null || openssl rand -base64 48)
    sed -i "s/CHANGE_ME_TO_RANDOM_64_CHARS/$JWT_SECRET/" config/.env.production
    echo "  Generated JWT_SECRET_KEY"
fi

# --- 7. Start services (HTTP only first) ---
echo "[7/7] Starting services..."

# Copy HTTP-only nginx config as the active config
cp nginx/default.conf nginx/active.conf

# Build and start
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "Services started. Waiting for nginx to be ready..."
sleep 5

# Verify HTTP is working
echo "Testing HTTP connectivity..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ]; then
    echo "  HTTP OK (status: $HTTP_CODE)"
else
    echo "  WARNING: HTTP returned status $HTTP_CODE — check 'docker compose -f docker-compose.prod.yml logs nginx'"
fi

# --- 8. SSL certificates ---
echo ""
echo "============================================"
echo "  SSL Certificate Setup"
echo "============================================"
echo ""
echo "  VPS IP: $(curl -s ifconfig.me)"
echo ""
echo "  Make sure DNS is set up:"
echo "    $DOMAIN_API      -> $(curl -s ifconfig.me)"
echo "    $DOMAIN_DASH     -> $(curl -s ifconfig.me)"
echo ""

read -p "Have DNS records propagated? (y/n): " DNS_READY
if [ "$DNS_READY" = "y" ]; then
    echo "Requesting SSL certificates..."

    # Run certbot with webroot method
    docker compose -f docker-compose.prod.yml run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/lib/letsencrypt \
        -d "$DOMAIN_API" \
        -d "$DOMAIN_DASH" \
        --email "admin@paypulse.cv" \
        --agree-tos \
        --no-eff-email \
        --force-renewal

    # Check if certs were created
    if docker compose -f docker-compose.prod.yml run --rm certbot ls /etc/letsencrypt/live/ 2>/dev/null | grep -q "$DOMAIN_API"; then
        echo "SSL certificates issued successfully!"

        # Switch to SSL config
        cp nginx/ssl.conf nginx/active.conf

        # Reload nginx
        docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
        echo "Nginx reloaded with SSL!"
    else
        echo ""
        echo "ERROR: Certbot did not create certificates."
        echo "Check the logs: docker compose -f docker-compose.prod.yml logs certbot"
        echo ""
        echo "After fixing, run certbot manually:"
        echo "  docker compose -f docker-compose.prod.yml run --rm certbot certonly \\"
        echo "    --webroot --webroot-path=/var/lib/letsencrypt \\"
        echo "    -d $DOMAIN_API -d $DOMAIN_DASH \\"
        echo "    --email admin@paypulse.cv --agree-tos --no-eff-email"
        echo ""
        echo "Then switch to SSL:"
        echo "  cp nginx/ssl.conf nginx/active.conf"
        echo "  docker compose -f docker-compose.prod.yml exec nginx nginx -s reload"
    fi
else
    echo ""
    echo "After DNS propagates, run:"
    echo ""
    echo "  cd /opt/paypulse"
    echo "  docker compose -f docker-compose.prod.yml run --rm certbot certonly \\"
    echo "    --webroot --webroot-path=/var/lib/letsencrypt \\"
    echo "    -d $DOMAIN_API -d $DOMAIN_DASH \\"
    echo "    --email admin@paypulse.cv --agree-tos --no-eff-email"
    echo ""
    echo "  cp nginx/ssl.conf nginx/active.conf"
    echo "  docker compose -f docker-compose.prod.yml exec nginx nginx -s reload"
fi

# --- Done ---
echo ""
echo "============================================"
echo "  Deployment Complete!"
echo "============================================"
echo ""
echo "  API:       https://$DOMAIN_API"
echo "  Dashboard: https://$DOMAIN_DASH"
echo "  Health:    https://$DOMAIN_API/health"
echo ""
echo "  Logs:"
echo "    docker compose -f docker-compose.prod.yml logs -f api"
echo "    docker compose -f docker-compose.prod.yml logs -f dashboard"
echo ""
echo "  Restart:"
echo "    docker compose -f docker-compose.prod.yml restart"
echo ""
echo "  Update:"
echo "    cd /opt/paypulse && git pull"
echo "    docker compose -f docker-compose.prod.yml up -d --build"
echo ""
