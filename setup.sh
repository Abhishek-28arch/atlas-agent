#!/bin/bash
# ─────────────────────────────────────────────
# JARVIS Setup Script
# ─────────────────────────────────────────────

set -e

echo ""
echo "⚡ Setting up JARVIS..."
echo ""

# ─── Check Python ────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PYTHON_VERSION detected"

# ─── Check/Install Ollama ────────────────────
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✓ Ollama already installed"
fi

# ─── Pull AI Model ───────────────────────────
echo "📦 Pulling Qwen 3.5:4B model (this may take a while)..."
ollama pull qwen3.5:2b

echo "📦 Pulling embedding model..."
ollama pull nomic-embed-text

# ─── Python Virtual Environment ──────────────
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "✓ Virtual environment activated"

# ─── Install Dependencies ────────────────────
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt --quiet

# ─── Create Data Directories ────────────────
mkdir -p data/knowledge
mkdir -p data/logs

# ─── Create .env if not exists ───────────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env from template — edit it with your secrets"
fi

echo ""
echo "─────────────────────────────────────────"
echo "✅ JARVIS is ready!"
echo ""
echo "   Activate environment:  source .venv/bin/activate"
echo "   Start JARVIS:          python main.py"
echo "─────────────────────────────────────────"
echo ""
