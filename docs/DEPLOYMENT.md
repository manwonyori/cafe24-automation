# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Cafe24 API credentials
- Domain name (for production)
- SSL certificates (for HTTPS)

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cafe24-automation-system.git
cd cafe24-automation-system
```

### 2. Configure Environment

```bash
cp config/.env.template config/.env
# Edit config/.env with your credentials
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

### 4. Verify Installation

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f app

# Run health check
docker-compose exec app python src/main.py --health-check
```

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure

```bash
# Clone repository
cd /opt
sudo git clone https://github.com/yourusername/cafe24-automation-system.git
cd cafe24-automation-system

# Create production environment file
sudo cp config/.env.template config/.env
sudo nano config/.env  # Add production credentials
```

### 3. SSL Configuration

```bash
# Create SSL directory
sudo mkdir -p nginx/ssl

# Copy certificates
sudo cp /path/to/your/cert.pem nginx/ssl/
sudo cp /path/to/your/key.pem nginx/ssl/
```

### 4. Start Services

```bash
# Pull images
sudo docker-compose pull

# Start in detached mode
sudo docker-compose up -d

# Check status
sudo docker-compose ps
```

### 5. Set Up Systemd Service

Create `/etc/systemd/system/cafe24-automation.service`:

```ini
[Unit]
Description=Cafe24 Automation System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/cafe24-automation-system
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable the service:

```bash
sudo systemctl enable cafe24-automation
sudo systemctl start cafe24-automation
```

## Monitoring

### 1. Application Logs

```bash
# View all logs
docker-compose logs

# Follow specific service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

### 2. Health Checks

```bash
# Manual health check
docker-compose exec app python src/main.py --health-check

# Check endpoint
curl http://localhost:5000/health
```

### 3. Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## Backup and Restore

### Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/cafe24"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/

# Backup cache
tar -czf $BACKUP_DIR/cache_$DATE.tar.gz cache/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Backup Docker volumes
docker run --rm -v cafe24-automation_redis-data:/data -v $BACKUP_DIR:/backup alpine tar -czf /backup/redis_$DATE.tar.gz -C /data .

echo "Backup completed: $BACKUP_DIR"
```

### Restore

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR="/backups/cafe24"
DATE=$1

if [ -z "$DATE" ]; then
    echo "Usage: ./restore.sh YYYYMMDD_HHMMSS"
    exit 1
fi

# Stop services
docker-compose down

# Restore configuration
tar -xzf $BACKUP_DIR/config_$DATE.tar.gz

# Restore cache
tar -xzf $BACKUP_DIR/cache_$DATE.tar.gz

# Restore logs
tar -xzf $BACKUP_DIR/logs_$DATE.tar.gz

# Restore Redis data
docker run --rm -v cafe24-automation_redis-data:/data -v $BACKUP_DIR:/backup alpine tar -xzf /backup/redis_$DATE.tar.gz -C /data

# Start services
docker-compose up -d

echo "Restore completed from: $DATE"
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs app

# Verify environment
docker-compose exec app env | grep CAFE24

# Test configuration
docker-compose exec app python -c "from src.cafe24_system import Cafe24System; s = Cafe24System()"
```

### API Connection Issues

```bash
# Test API connectivity
docker-compose exec app python -c "
from src.api_client import Cafe24APIClient
import os
config = {
    'mall_id': os.getenv('CAFE24_MALL_ID'),
    'client_id': os.getenv('CAFE24_CLIENT_ID'),
    'client_secret': os.getenv('CAFE24_CLIENT_SECRET')
}
client = Cafe24APIClient(config)
print(client.get_products(limit=1))
"
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Clear cache
docker-compose exec app python -c "
from src.cache_manager import CacheManager
cache = CacheManager({'enabled': True, 'cache_dir': 'cache'})
cache.clear()
"

# Restart services
docker-compose restart
```

## Security Checklist

- [ ] Change default passwords
- [ ] Use strong API credentials
- [ ] Enable firewall (allow only 80, 443, 22)
- [ ] Set up SSL certificates
- [ ] Regular security updates
- [ ] Implement log rotation
- [ ] Set up automated backups
- [ ] Monitor disk space
- [ ] Configure fail2ban
- [ ] Use GitHub Secrets for CI/CD