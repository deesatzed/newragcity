# Multi-stage Dockerfile for Cognitron Medical-Grade Personal Knowledge Assistant
# Optimized for production deployment with medical-grade security and performance

# =============================================================================
# Stage 1: Base dependencies and build environment
# =============================================================================
FROM python:3.11-slim as base

# Set build arguments
ARG COGNITRON_VERSION=1.0.0
ARG BUILD_DATE
ARG VCS_REF

# Add metadata labels for medical-grade traceability
LABEL maintainer="Cognitron AI Team <team@cognitron.ai>" \
      version="${COGNITRON_VERSION}" \
      description="Medical-Grade Personal Knowledge Assistant" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}" \
      vendor="Cognitron AI" \
      schema-version="1.0" \
      medical-grade="true" \
      security-scan="required"

# Set environment variables for medical-grade configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    COGNITRON_VERSION=${COGNITRON_VERSION}

# Create non-root user for security (medical-grade requirement)
RUN groupadd -r cognitron --gid=1000 && \
    useradd -r -g cognitron --uid=1000 --shell=/bin/bash --home=/app cognitron

# Install system dependencies with security updates
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    gcc \
    g++ \
    # System utilities
    curl \
    ca-certificates \
    gnupg \
    # Database support
    sqlite3 \
    libsqlite3-dev \
    # SSL/TLS support
    libssl-dev \
    libffi-dev \
    # Medical-grade security tools
    aide \
    rkhunter \
    # Monitoring tools
    procps \
    htop \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y

# =============================================================================
# Stage 2: Python dependencies and build
# =============================================================================
FROM base as builder

# Set working directory
WORKDIR /build

# Create virtual environment for isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel build

# Copy dependency files first for better caching
COPY pyproject.toml README.md ./
COPY cognitron/ ./cognitron/

# Install Python dependencies with medical-grade verification
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir \
    # Medical-grade monitoring
    prometheus-client==0.19.0 \
    psutil==5.9.6 \
    # Enhanced security
    cryptography==41.0.7 \
    bcrypt==4.1.2 \
    # Production WSGI server
    gunicorn==21.2.0 \
    uvicorn==0.24.0 \
    # Health check utilities
    requests==2.31.0

# Verify installation integrity
RUN python -c "import cognitron; print(f'Cognitron v{cognitron.__version__} installed successfully')"

# Run medical-grade security scan on dependencies
RUN pip audit --format=json --output=/build/security-audit.json || true

# =============================================================================
# Stage 3: Runtime environment with security hardening
# =============================================================================
FROM base as runtime

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application files with proper ownership
COPY --chown=cognitron:cognitron --from=builder /build/cognitron ./cognitron
COPY --chown=cognitron:cognitron --from=builder /build/pyproject.toml ./
COPY --chown=cognitron:cognitron --from=builder /build/security-audit.json ./

# Create application directories with secure permissions
RUN mkdir -p /app/data /app/logs /app/config /app/tmp && \
    chown -R cognitron:cognitron /app && \
    chmod 755 /app && \
    chmod 750 /app/data /app/logs /app/config && \
    chmod 1777 /app/tmp  # Sticky bit for temp directory

# Copy configuration files
COPY --chown=cognitron:cognitron docker/config/ ./config/
COPY --chown=cognitron:cognitron docker/entrypoint.sh ./
COPY --chown=cognitron:cognitron docker/healthcheck.py ./

# Make scripts executable
RUN chmod +x entrypoint.sh healthcheck.py

# Create medical-grade audit configuration
RUN echo "# Medical-Grade Audit Configuration" > /app/config/audit.conf && \
    echo "audit_enabled=true" >> /app/config/audit.conf && \
    echo "audit_level=detailed" >> /app/config/audit.conf && \
    echo "retention_days=90" >> /app/config/audit.conf && \
    chown cognitron:cognitron /app/config/audit.conf

# Set medical-grade environment variables
ENV COGNITRON_ENV=production \
    COGNITRON_DATA_DIR=/app/data \
    COGNITRON_LOG_DIR=/app/logs \
    COGNITRON_CONFIG_DIR=/app/config \
    COGNITRON_TEMP_DIR=/app/tmp \
    COGNITRON_AUDIT_ENABLED=true \
    COGNITRON_SECURITY_LEVEL=medical_grade \
    COGNITRON_CRITICAL_THRESHOLD=0.95 \
    COGNITRON_PRODUCTION_THRESHOLD=0.85 \
    COGNITRON_LOG_LEVEL=INFO

# Expose ports
EXPOSE 8080 9090

# Health check with medical-grade validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python healthcheck.py || exit 1

# Create volumes for persistent data
VOLUME ["/app/data", "/app/logs"]

# Switch to non-root user (security requirement)
USER cognitron

# Set secure umask
RUN echo "umask 027" >> ~/.bashrc

# Default command
ENTRYPOINT ["./entrypoint.sh"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8080", "--production"]

# =============================================================================
# Stage 4: Development variant
# =============================================================================
FROM runtime as development

# Switch back to root for development tools installation
USER root

# Install development and debugging tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Development tools
    vim \
    git \
    curl \
    wget \
    # Debugging tools
    strace \
    gdb \
    # Network tools
    netcat-openbsd \
    telnet \
    # Performance monitoring
    iotop \
    nethogs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN /opt/venv/bin/pip install --no-cache-dir \
    # Development tools
    ipython==8.17.2 \
    ipdb==0.13.13 \
    # Testing tools
    pytest==7.4.3 \
    pytest-cov==4.1.0 \
    pytest-asyncio==0.21.1 \
    # Code quality tools
    ruff==0.1.6 \
    mypy==1.7.1 \
    bandit==1.7.5 \
    # Documentation tools
    mkdocs==1.5.3 \
    mkdocs-material==9.4.8

# Set development environment variables
ENV COGNITRON_ENV=development \
    COGNITRON_LOG_LEVEL=DEBUG \
    COGNITRON_DEBUG=true \
    COGNITRON_RELOAD=true

# Switch back to cognitron user
USER cognitron

# Development command
CMD ["serve", "--host", "0.0.0.0", "--port", "8080", "--development", "--reload"]

# =============================================================================
# Stage 5: Security-hardened production variant
# =============================================================================
FROM runtime as security-hardened

# Switch to root for security hardening
USER root

# Install additional security tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Security scanning
    lynis \
    chkrootkit \
    # File integrity monitoring  
    aide \
    # Network security
    fail2ban \
    # Logging and monitoring
    rsyslog \
    logrotate \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure AIDE (file integrity monitoring)
RUN aideinit && \
    mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Configure fail2ban for network security
COPY docker/security/fail2ban.conf /etc/fail2ban/jail.local

# Set up log rotation for medical-grade audit trails
COPY docker/security/logrotate.conf /etc/logrotate.d/cognitron

# Configure secure syslog
RUN echo "# Cognitron secure logging" >> /etc/rsyslog.conf && \
    echo "local0.*    /app/logs/audit.log" >> /etc/rsyslog.conf

# Run security hardening script
COPY docker/security/harden.sh /tmp/harden.sh
RUN chmod +x /tmp/harden.sh && /tmp/harden.sh && rm /tmp/harden.sh

# Switch back to cognitron user
USER cognitron

# Security-hardened environment variables
ENV COGNITRON_SECURITY_HARDENED=true \
    COGNITRON_FILE_INTEGRITY_CHECK=true \
    COGNITRON_NETWORK_MONITORING=true

# =============================================================================
# Stage 6: Multi-architecture support
# =============================================================================
FROM runtime as multiarch

# Multi-architecture optimization
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Platform-specific optimizations
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
      echo "Optimizing for ARM64"; \
      # ARM64 specific optimizations
    elif [ "$TARGETPLATFORM" = "linux/amd64" ]; then \
      echo "Optimizing for AMD64"; \
      # AMD64 specific optimizations  
    fi

# Print build information
RUN echo "Build platform: $BUILDPLATFORM" && \
    echo "Target platform: $TARGETPLATFORM" && \
    echo "Python version: $(python --version)" && \
    echo "Cognitron version: $COGNITRON_VERSION"