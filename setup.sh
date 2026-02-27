#!/usr/bin/env bash
# ============================================================
# setup.sh — Gmail JobTracker one-time setup
# Usage: chmod +x setup.sh && ./setup.sh
# ============================================================

set -e

echo "============================================================"
echo "  Gmail JobTracker — Setup"
echo "============================================================"
echo ""

# --------------------------------------------------
# 1. Check Python
# --------------------------------------------------
echo "[1/5] Checking Python..."
if command -v python3 &> /dev/null; then
    PY=$(python3 --version 2>&1)
    echo "       Found: $PY"
else
    echo "       ERROR: python3 not found. Please install Python 3.9+."
    exit 1
fi

# --------------------------------------------------
# 2. Create venv
# --------------------------------------------------
echo "[2/5] Setting up Python virtual environment..."
if [ -d "venv" ]; then
    echo "       venv/ already exists. Skipping creation."
else
    python3 -m venv venv
    echo "       Created venv/"
fi

# Activate venv
source venv/bin/activate
echo "       Activated venv ($(python --version))"

# --------------------------------------------------
# 3. Install Python dependencies
# --------------------------------------------------
echo "[3/5] Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "       Done."

# --------------------------------------------------
# 4. Install frontend dependencies
# --------------------------------------------------
echo "[4/5] Installing frontend dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    npm install --silent
    cd ..
    echo "       Done."
else
    echo "       WARNING: frontend/ directory not found. Skipping."
fi

# --------------------------------------------------
# 5. Pre-flight checks
# --------------------------------------------------
echo "[5/5] Pre-flight checks..."

# Check credentials.json
if [ -f "credentials.json" ]; then
    echo "       ✔ credentials.json found"
else
    echo "       ⚠ credentials.json NOT found"
    echo "         Download it from Google Cloud Console → APIs & Services → Credentials"
    echo "         and place it in the project root."
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    echo "       ✔ ollama command found"

    # Check classification model
    if ollama list 2>/dev/null | grep -q "qwen2.5-coder:7b"; then
        echo "       ✔ qwen2.5-coder:7b model available (classification)"
    else
        echo "       ⚠ qwen2.5-coder:7b not found. Run: ollama pull qwen2.5-coder:7b"
    fi

    # Check chat model
    if ollama list 2>/dev/null | grep -q "qwen3:8b"; then
        echo "       ✔ qwen3:8b model available (AI chat)"
    else
        echo "       ⚠ qwen3:8b not found. Run: ollama pull qwen3:8b"
    fi
else
    echo "       ⚠ ollama not found. Install from https://ollama.com"
fi

echo ""
echo "============================================================"
echo "  Setup complete!"
echo "  Next: ./start.sh"
echo "============================================================"