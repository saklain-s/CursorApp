# 🚀 Getting Started with UnAI

Welcome to UnAI - your comprehensive AI content detection solution! This guide will help you get the application running quickly.

## ✅ What You Have

Your UnAI app is now fully built and includes:

### 📁 Project Structure
```
UnAI/
├── 🐍 Backend (Python/Flask)
│   ├── app.py              # Main application server
│   ├── requirements.txt    # Python dependencies
│   └── uploads/           # File upload directory
├── 🎨 Frontend (HTML/CSS/JS)
│   ├── templates/
│   │   └── index.html     # Main web interface
│   └── static/
│       ├── css/style.css  # Modern styling
│       └── js/app.js      # Interactive functionality
├── 🛠️ Setup & Deployment
│   ├── setup.sh           # Automated setup script
│   ├── run.py             # Development server launcher
│   ├── Dockerfile         # Container deployment
│   └── docker-compose.yml # Multi-service deployment
└── 📚 Documentation
    ├── README.md          # Comprehensive documentation
    ├── GETTING_STARTED.md # This file
    └── test_app.py        # Testing suite
```

### 🎯 Key Features
- **Multi-Format Support**: Images, Videos, Audio files
- **Advanced Detection**: Statistical analysis, edge detection, frequency analysis
- **Modern UI**: Drag-and-drop interface with real-time previews
- **REST API**: Programmatic access for integration
- **Responsive Design**: Works on desktop and mobile
- **Docker Ready**: Easy containerized deployment

## 🏃‍♂️ Quick Start (3 Methods)

### Method 1: Using Setup Script (Recommended)
```bash
# Make executable and run
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source unai_env/bin/activate

# Run the app
python app.py
```

### Method 2: Using Run Script
```bash
# Direct execution
python3 run.py
```

### Method 3: Manual Setup
```bash
# Create virtual environment
python3 -m venv unai_env
source unai_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

## 🌐 Access Your App

Once running, open your browser to:
- **Web Interface**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health

## 🧪 Testing Your Installation

Run the test suite to verify everything works:
```bash
# Start the server first (in another terminal)
python app.py

# Then run tests
python test_app.py
```

## 📱 Using the Web Interface

1. **Upload Files**: 
   - Drag and drop files onto the upload area
   - Or click to browse and select files
   - Supports: PNG, JPG, MP4, MP3, WAV, and more

2. **View Results**:
   - ✅ **Human-Made**: Likely created by humans
   - 🤖 **AI-Generated**: Likely created by AI
   - ❓ **Uncertain**: Not enough confidence to determine

3. **Analyze Details**:
   - View technical analysis metrics
   - Understand detection methodology
   - See confidence percentage

## 🔌 Using the API

### Analyze a File
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@your_image.jpg"
```

### Response Format
```json
{
  "is_ai_generated": false,
  "confidence": 72.5,
  "file_type": "image",
  "filename": "your_image.jpg",
  "features": {
    "pixel_variance": 1234.56,
    "edge_density": 0.12,
    "frequency_variance": 15.8
  }
}
```

## 🐳 Docker Deployment

For production deployment:
```bash
# Build and run with Docker
docker-compose up --build

# Or just the app
docker build -t unai-app .
docker run -p 5000:5000 unai-app
```

## 🔧 Configuration

### Environment Variables
```bash
export FLASK_ENV=development    # or production
export FLASK_DEBUG=1           # for development
export MAX_FILE_SIZE=52428800  # 50MB limit
```

### Customizing Detection
Edit `app.py` to adjust:
- Confidence thresholds
- Analysis parameters
- File size limits
- Supported formats

## 🎨 Customizing the UI

### Colors and Styling
Edit `static/css/style.css` to change:
- Color schemes
- Layout
- Animations
- Responsive breakpoints

### Functionality
Edit `static/js/app.js` to modify:
- Upload behavior
- Result display
- Error handling
- User interactions

## 🚨 Troubleshooting

### Common Issues

**1. Dependencies Missing**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-dev libmagic1 ffmpeg
```

**2. Virtual Environment Issues**
```bash
# Recreate virtual environment
rm -rf unai_env
python3 -m venv unai_env
source unai_env/bin/activate
pip install -r requirements.txt
```

**3. Port Already in Use**
```bash
# Kill process using port 5000
sudo lsof -ti:5000 | xargs kill -9

# Or run on different port
python app.py --port 5001
```

**4. File Upload Errors**
- Check file size (max 50MB)
- Verify file format is supported
- Ensure uploads/ directory exists and is writable

### Getting Help

1. **Check Logs**: Application logs show detailed error information
2. **Run Tests**: `python test_app.py` to diagnose issues
3. **Health Check**: Visit `/api/health` to verify server status

## 🔮 What's Next?

### Enhance Detection Accuracy
- Train custom models with your data
- Implement additional detection algorithms
- Add support for new file formats

### Scale for Production
- Use gunicorn for production serving
- Add Redis for caching
- Implement rate limiting
- Add user authentication

### Integrate with Other Systems
- Build plugins for content management systems
- Create browser extensions
- Develop mobile applications
- Add batch processing capabilities

## 📊 Performance Tips

### For Better Speed
- Use SSD storage for faster file I/O
- Increase available RAM for large files
- Use multiple worker processes in production
- Cache analysis results for repeated files

### For Better Accuracy
- Preprocess files to standard formats
- Combine multiple detection methods
- Use ensemble models
- Regularly update detection algorithms

## 🎉 You're Ready!

Your UnAI application is now fully functional and ready to detect AI-generated content. The app includes:

- ✅ Complete web interface
- ✅ REST API
- ✅ Multi-format support
- ✅ Modern, responsive design
- ✅ Docker deployment ready
- ✅ Comprehensive documentation
- ✅ Testing suite

**Happy AI detecting!** 🤖🔍

---

*Need help? Check the README.md for detailed documentation or run the test suite to verify your installation.*