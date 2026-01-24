#!/bin/bash
# Test setup.py flow with simulated user inputs

echo "Testing RoT setup.py flow..."
echo ""

# Simulate user inputs:
# 1. Framework choice: 2 (Ollama for easier testing)
# 2. Model choice: 4 (Skip model setup)
# 3. Data folder: Y (use default)
# 4. Continue after validation: Y

echo "2
4
Y
Y" | python setup.py --debug
