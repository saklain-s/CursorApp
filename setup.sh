#!/bin/bash

# UnAI Setup Script
echo "🚀 Setting up UnAI - AI Content Detection App"
echo "============================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv unai_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source unai_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install system dependencies based on OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux - Installing system dependencies..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-dev libmagic1 ffmpeg libsndfile1
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-devel file-devel ffmpeg libsndfile
    else
        echo "⚠️ Please install libmagic, ffmpeg, and libsndfile manually"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS - Installing system dependencies..."
    if command -v brew &> /dev/null; then
        brew install libmagic ffmpeg libsndfile
    else
        echo "⚠️ Please install Homebrew and run: brew install libmagic ffmpeg libsndfile"
    fi
else
    echo "🪟 Please install ffmpeg and libmagic for your system"
fi

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p logs

# Set permissions
chmod +x app.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment: source unai_env/bin/activate"
echo "2. Run the app: python app.py"
echo "3. Open http://localhost:5000 in your browser"
echo ""
echo "For production deployment, consider using gunicorn:"
echo "gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "Happy AI detecting! 🤖🔍"