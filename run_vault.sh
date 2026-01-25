#!/bin/bash

# The Vault - Execution Script
echo "🔒 Starting The Vault..."

# 1. Ensure Dependencies (User should run this once)
# uv sync

# 2. Build the Configuration
echo "⚙️  Building Pipeline Configuration..."
ultrarag build TheVault/pipeline/vault_main.yaml

# 3. Run the Pipeline
echo "🚀 Running The Vault..."
# We pass a sample query via environment variable or CLI arg if supported, 
# but UltraRAG usually takes input from the pipeline definition or interactive mode.
# For this demo, we'll run the defined pipeline which expects inputs.
# Note: In a real app, you'd use 'ultrarag show ui' or pass inputs via a separate parameter file.

ultrarag run TheVault/pipeline/vault_main.yaml
