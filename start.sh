#!/bin/bash

# MCP-A2A-LangChain Multi-Agent System Startup Script

echo "🚀 Starting MCP-A2A-LangChain Multi-Agent System"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before running the system"
    echo "   Required: OPENAI_API_KEY (for coordinator agent)"
    echo "   Optional: ANTHROPIC_API_KEY, GOOGLE_API_KEY, SERPER_API_KEY"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /workspace/scraped_data
mkdir -p /workspace/logs

# Start the system
echo "🌟 Starting the Multi-Agent System..."
python main.py

echo "👋 System shutdown complete."