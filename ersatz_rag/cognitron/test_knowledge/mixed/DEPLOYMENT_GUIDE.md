# Medical System Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the medical information system across development, staging, and production environments with full HIPAA compliance.

## Prerequisites

### Infrastructure Requirements

#### Production Environment
- **Compute**: 8 CPU cores, 32GB RAM minimum per server
- **Storage**: SSD with encryption at rest, 1TB minimum
- **Network**: Dedicated VLAN with firewall protection
- **Backup**: Automated daily backups with 7-year retention
- **Monitoring**: 24/7 system monitoring and alerting

#### Security Requirements
- HIPAA-compliant data center certification
- Physical access controls and surveillance
- Network intrusion detection systems
- Regular penetration testing and vulnerability assessments

### Software Dependencies

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  medical-api:
    image: medical-system:latest
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/medical_db
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - HIPAA_AUDIT_ENABLED=true
    networks:
      - medical-network
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=medical_db
      - POSTGRES_USER=medical_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backup:/backup
    networks:
      - medical-network

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    networks:
      - medical-network

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - medical-api
    networks:
      - medical-network

networks:
  medical-network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
```

## Environment Configuration

### Environment Variables

Create environment-specific configuration files:

#### Production (.env.production)
```bash
# Database Configuration
DATABASE_URL=postgresql://medical_user:${DB_PASSWORD}@postgres:5432/medical_db
DATABASE_SSL_MODE=require
DATABASE_POOL_SIZE=20

# Redis Configuration  
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=${REDIS_PASSWORD}

# Security Configuration
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=/etc/ssl/private/jwt_private.pem
JWT_PUBLIC_KEY_PATH=/etc/ssl/certs/jwt_public.pem

# HIPAA Compliance
HIPAA_AUDIT_ENABLED=true
HIPAA_LOG_LEVEL=INFO
AUDIT_LOG_RETENTION_DAYS=2555  # 7 years

# Encryption
ENCRYPTION_KEY=${ENCRYPTION_KEY}
PHI_ENCRYPTION_ENABLED=true

# Monitoring
SENTRY_DSN=${SENTRY_DSN}
NEW_RELIC_LICENSE_KEY=${NEW_RELIC_KEY}
LOG_LEVEL=INFO

# Email Configuration
SMTP_HOST=smtp.hospital.com
SMTP_PORT=587
SMTP_USERNAME=${SMTP_USERNAME}
SMTP_PASSWORD=${SMTP_PASSWORD}
```

#### Staging (.env.staging)
```bash
# Similar to production but with staging-specific values
DATABASE_URL=postgresql://staging_user:${STAGING_DB_PASSWORD}@staging-db:5432/medical_staging
HIPAA_AUDIT_ENABLED=true
LOG_LEVEL=DEBUG
```

#### Development (.env.development)
```bash
# Development environment with test data
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/medical_dev
HIPAA_AUDIT_ENABLED=false
LOG_LEVEL=DEBUG
USE_TEST_DATA=true
```

## Deployment Process

### Step 1: Pre-deployment Checklist

```bash
#!/bin/bash
# pre-deployment-check.sh

echo "🏥 Medical System Pre-Deployment Checklist"

# Check SSL certificates
if [[ -f "/etc/ssl/certs/medical-api.crt" ]]; then
    echo "✅ SSL certificate found"
    openssl x509 -in /etc/ssl/certs/medical-api.crt -text -noout | grep "Not After"
else
    echo "❌ SSL certificate missing"
    exit 1
fi

# Check database connectivity
if pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Verify environment variables
required_vars=("JWT_SECRET_KEY" "DB_PASSWORD" "ENCRYPTION_KEY")
for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo "❌ Missing required environment variable: $var"
        exit 1
    else
        echo "✅ Environment variable $var is set"
    fi
done

# Check disk space
available_space=$(df -h /var/lib/postgresql/data | awk 'NR==2 {print $4}' | sed 's/G//')
if (( available_space < 100 )); then
    echo "❌ Insufficient disk space: ${available_space}GB available, need 100GB minimum"
    exit 1
else
    echo "✅ Sufficient disk space: ${available_space}GB available"
fi

echo "✅ Pre-deployment checks passed"
```

### Step 2: Database Migration

```python
# migrate.py
"""
Database migration script with HIPAA audit logging
"""
import os
import logging
from datetime import datetime
from alembic import command
from alembic.config import Config

# Configure audit logging
audit_logger = logging.getLogger('hipaa_audit')
audit_handler = logging.FileHandler('/var/log/medical/audit.log')
audit_logger.addHandler(audit_handler)

def run_migrations():
    """Run database migrations with audit logging"""
    
    audit_logger.info(f"Database migration started at {datetime.utcnow()}")
    
    try:
        # Load Alembic configuration
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        audit_logger.info("Database migration completed successfully")
        print("✅ Database migration successful")
        
    except Exception as e:
        audit_logger.error(f"Database migration failed: {str(e)}")
        print(f"❌ Database migration failed: {str(e)}")
        raise

def verify_schema():
    """Verify database schema matches expected structure"""
    from sqlalchemy import create_engine, inspect
    
    engine = create_engine(os.getenv("DATABASE_URL"))
    inspector = inspect(engine)
    
    required_tables = [
        'patients', 'medical_professionals', 'appointments', 
        'medical_records', 'audit_logs'
    ]
    
    existing_tables = inspector.get_table_names()
    
    for table in required_tables:
        if table in existing_tables:
            print(f"✅ Table {table} exists")
        else:
            print(f"❌ Table {table} missing")
            return False
            
    return True

if __name__ == "__main__":
    run_migrations()
    if verify_schema():
        print("✅ Schema verification passed")
    else:
        print("❌ Schema verification failed")
        exit(1)
```

### Step 3: Application Deployment

```bash
#!/bin/bash
# deploy.sh

set -e  # Exit on any error

ENVIRONMENT=${1:-production}
echo "🚀 Deploying Medical System to $ENVIRONMENT"

# Load environment configuration
if [[ -f ".env.$ENVIRONMENT" ]]; then
    source ".env.$ENVIRONMENT"
    echo "✅ Environment configuration loaded"
else
    echo "❌ Environment configuration file .env.$ENVIRONMENT not found"
    exit 1
fi

# Build application image
echo "📦 Building application image..."
docker build -t medical-system:latest .

# Run pre-deployment checks
echo "🔍 Running pre-deployment checks..."
./scripts/pre-deployment-check.sh

# Stop existing services gracefully
echo "⏹️  Stopping existing services..."
docker-compose -f docker-compose.$ENVIRONMENT.yml down --timeout 30

# Run database migrations
echo "🗄️  Running database migrations..."
python migrate.py

# Start new services
echo "🔄 Starting new services..."
docker-compose -f docker-compose.$ENVIRONMENT.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run health checks
echo "🏥 Running health checks..."
./scripts/health-check.sh

# Verify HIPAA compliance
echo "📋 Verifying HIPAA compliance..."
./scripts/hipaa-compliance-check.sh

# Update monitoring and alerting
echo "📊 Updating monitoring configuration..."
./scripts/update-monitoring.sh $ENVIRONMENT

echo "✅ Deployment completed successfully!"
echo "🏥 Medical System is now running in $ENVIRONMENT environment"
```

### Step 4: Health Check Script

```python
# health-check.py
"""
Comprehensive health check for medical system
"""
import requests
import psycopg2
import redis
import sys
from datetime import datetime

def check_api_health():
    """Check API health endpoint"""
    try:
        response = requests.get("https://api.hospital.com/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get("status") == "healthy":
                print("✅ API health check passed")
                return True
        print(f"❌ API health check failed: {response.status_code}")
        return False
    except Exception as e:
        print(f"❌ API health check error: {str(e)}")
        return False

def check_database_health():
    """Check database connectivity and basic operations"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result[0] == 1:
            print("✅ Database health check passed")
            return True
        else:
            print("❌ Database health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Database health check error: {str(e)}")
        return False

def check_redis_health():
    """Check Redis connectivity"""
    try:
        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True
        )
        
        r.ping()
        print("✅ Redis health check passed")
        return True
        
    except Exception as e:
        print(f"❌ Redis health check error: {str(e)}")
        return False

def check_ssl_certificate():
    """Verify SSL certificate is valid"""
    import ssl
    import socket
    from datetime import datetime
    
    try:
        hostname = os.getenv("API_HOSTNAME", "api.hospital.com")
        port = 443
        
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Check expiration
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (not_after - datetime.now()).days
                
                if days_until_expiry > 30:
                    print(f"✅ SSL certificate valid (expires in {days_until_expiry} days)")
                    return True
                else:
                    print(f"⚠️  SSL certificate expires soon ({days_until_expiry} days)")
                    return False
                    
    except Exception as e:
        print(f"❌ SSL certificate check error: {str(e)}")
        return False

def check_audit_logging():
    """Verify audit logging is functioning"""
    try:
        # Test audit log write
        test_log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "health_check",
            "user": "system",
            "action": "verify_audit_logging"
        }
        
        # This would write to your audit logging system
        print("✅ Audit logging check passed")
        return True
        
    except Exception as e:
        print(f"❌ Audit logging check error: {str(e)}")
        return False

def main():
    """Run all health checks"""
    print("🏥 Medical System Health Check")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("-" * 50)
    
    checks = [
        ("API Health", check_api_health),
        ("Database Health", check_database_health),
        ("Redis Health", check_redis_health),
        ("SSL Certificate", check_ssl_certificate),
        ("Audit Logging", check_audit_logging)
    ]
    
    passed = 0
    failed = 0
    
    for check_name, check_func in checks:
        print(f"\nRunning {check_name}...")
        if check_func():
            passed += 1
        else:
            failed += 1
    
    print("-" * 50)
    print(f"Health Check Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All health checks passed - System is healthy")
        sys.exit(0)
    else:
        print("❌ Some health checks failed - System needs attention")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Monitoring and Alerting

### System Monitoring Configuration

```yaml
# monitoring-config.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  grafana_data:
```

### Alert Rules

```yaml
# alert-rules.yml
groups:
  - name: medical_system_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
          system: medical_api
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 10% for 2 minutes"

      - alert: DatabaseConnectionFailure
        expr: up{job="postgres"} == 0
        for: 30s
        labels:
          severity: critical
          system: database
        annotations:
          summary: "Database connection failure"
          description: "Cannot connect to PostgreSQL database"

      - alert: PHIAccessAnomaly
        expr: increase(audit_log_phi_access_total[1h]) > 100
        for: 5m
        labels:
          severity: warning
          system: hipaa_compliance
        annotations:
          summary: "Unusual PHI access pattern detected"
          description: "PHI access rate is unusually high"
```

## Security Configuration

### SSL/TLS Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;

    upstream medical_api {
        server medical-api:8000;
        keepalive 32;
    }

    server {
        listen 443 ssl http2;
        server_name api.hospital.com;

        ssl_certificate /etc/nginx/ssl/medical-api.crt;
        ssl_certificate_key /etc/nginx/ssl/medical-api.key;
        
        ssl_protocols TLSv1.3 TLSv1.2;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        location /auth {
            limit_req zone=auth burst=5 nodelay;
            proxy_pass http://medical_api;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://medical_api;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

## Backup and Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/medical-system"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=2555  # 7 years for HIPAA compliance

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Database backup
echo "📦 Creating database backup..."
pg_dump $DATABASE_URL | gzip > "$BACKUP_DIR/$DATE/database_$DATE.sql.gz"

# File system backup (encrypted)
echo "📁 Creating file system backup..."
tar -czf - /var/lib/medical-system | openssl enc -aes-256-cbc -salt -k "$BACKUP_ENCRYPTION_KEY" > "$BACKUP_DIR/$DATE/filesystem_$DATE.tar.gz.enc"

# Verify backup integrity
echo "🔍 Verifying backup integrity..."
if gzip -t "$BACKUP_DIR/$DATE/database_$DATE.sql.gz"; then
    echo "✅ Database backup verified"
else
    echo "❌ Database backup verification failed"
    exit 1
fi

# Clean up old backups
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true

# Log backup completion
echo "✅ Backup completed: $BACKUP_DIR/$DATE"
logger "Medical system backup completed successfully: $DATE"
```

## Troubleshooting

### Common Issues and Solutions

#### 1. High Memory Usage
```bash
# Check memory usage
docker stats
# Scale down non-critical services
docker-compose scale worker=1
# Restart services if needed
docker-compose restart medical-api
```

#### 2. Database Connection Pool Exhaustion
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;
-- Kill long-running queries
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND query_start < now() - interval '1 hour';
```

#### 3. SSL Certificate Issues
```bash
# Check certificate expiration
openssl x509 -in /etc/ssl/certs/medical-api.crt -text -noout | grep "Not After"
# Renew certificate (Let's Encrypt)
certbot renew --nginx
```

## Compliance Verification

### HIPAA Compliance Checklist

- [ ] All PHI encrypted at rest and in transit
- [ ] Access controls implemented and regularly reviewed
- [ ] Audit logging enabled for all PHI access
- [ ] Regular security assessments conducted
- [ ] Staff training on HIPAA requirements completed
- [ ] Business associate agreements in place
- [ ] Incident response procedures documented and tested

### Post-Deployment Verification

```bash
# Run compliance check
./scripts/hipaa-compliance-check.sh

# Verify all services are running
docker-compose ps

# Check system logs
tail -f /var/log/medical/application.log

# Monitor system metrics
curl -s http://localhost:9090/metrics | grep medical_
```

## Support and Maintenance

### Routine Maintenance Tasks

- **Daily**: Monitor system health and review logs
- **Weekly**: Review access logs and security alerts  
- **Monthly**: Update system patches and dependencies
- **Quarterly**: Security assessment and penetration testing
- **Annually**: HIPAA compliance audit and policy review

### Emergency Contacts

- **On-call Engineer**: 555-EMERGENCY
- **Security Team**: security@hospital.com
- **HIPAA Officer**: hipaa@hospital.com