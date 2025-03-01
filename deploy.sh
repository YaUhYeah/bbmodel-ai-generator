#!/bin/bash

# AI-Powered bbmodel Generator Deployment Script
# This script automates the deployment of the application to a Digital Ocean VPS

# Exit on error
set -e

# Configuration
APP_NAME="bbmodel-ai-generator"
REPO_URL="https://github.com/yourusername/bbmodel-ai-generator.git"
DEPLOY_DIR="/opt/$APP_NAME"
DOMAIN="bbmodel-ai-generator.com"
EMAIL="admin@bbmodel-ai-generator.com"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# Update system packages
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required packages
print_status "Installing required packages..."
apt-get install -y \
    git \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw

# Enable and start Docker
print_status "Enabling and starting Docker..."
systemctl enable docker
systemctl start docker

# Configure firewall
print_status "Configuring firewall..."
ufw allow ssh
ufw allow http
ufw allow https
ufw allow 53006/tcp
ufw allow 59555/tcp
ufw --force enable

# Create deployment directory
print_status "Creating deployment directory..."
mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR

# Clone or update repository
if [ -d ".git" ]; then
    print_status "Updating existing repository..."
    git pull
else
    print_status "Cloning repository..."
    git clone $REPO_URL .
fi

# Create environment file
print_status "Creating environment file..."
cat > .env << EOL
# Database settings
DATABASE_URL=postgresql://postgres:postgres@db:5432/bbmodel
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=bbmodel

# Security settings
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# API settings
BACKEND_CORS_ORIGINS=["http://$DOMAIN", "https://$DOMAIN", "http://localhost", "http://localhost:59555"]

# Storage settings
MODELS_DIR=/app/static/models
TEXTURES_DIR=/app/static/textures

# Frontend settings
REACT_APP_API_URL=https://$DOMAIN/api
EOL

# Configure Nginx
print_status "Configuring Nginx..."
cat > /etc/nginx/sites-available/$APP_NAME << EOL
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://localhost:59555;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:53006;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /static {
        proxy_pass http://localhost:53006/static;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /docs {
        proxy_pass http://localhost:53006/docs;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /openapi.json {
        proxy_pass http://localhost:53006/openapi.json;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOL

# Enable the site
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx

# Set up SSL with Certbot
print_status "Setting up SSL with Certbot..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m $EMAIL

# Build and start the application with Docker Compose
print_status "Building and starting the application..."
docker-compose build
docker-compose up -d

# Initialize the database
print_status "Initializing the database..."
sleep 10  # Wait for the database to be ready
docker-compose exec backend python -c "from app.db.base import Base, engine; from app.db.models import *; Base.metadata.create_all(bind=engine)"
docker-compose exec backend python -c "from sqlalchemy.orm import Session; from app.db.base import engine; from app.db.init_db import init_db; session = Session(engine); init_db(session)"

print_status "Deployment completed successfully!"
print_status "Your application is now running at https://$DOMAIN"
print_status "API documentation is available at https://$DOMAIN/docs"