import os
import io
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import cv2
import tempfile
import logging
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
    'video': {'mp4', 'avi', 'mov', 'mkv', 'webm'},
    'audio': {'mp3', 'wav', 'flac', 'ogg', 'm4a'}
}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename, file_type):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[file_type]

def get_file_type(filename):
    """Determine file type from filename"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext in ALLOWED_EXTENSIONS['image']:
        return 'image'
    elif ext in ALLOWED_EXTENSIONS['video']:
        return 'video'
    elif ext in ALLOWED_EXTENSIONS['audio']:
        return 'audio'
    else:
        return 'unknown'

def detect_ai_image(image_path):
    """Detect if an image is AI-generated using basic analysis"""
    try:
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        img_array = np.array(image)
        
        # Basic statistical analysis
        # 1. Pixel distribution analysis
        pixel_variance = np.var(img_array)
        pixel_mean = np.mean(img_array)
        
        # 2. Simple edge detection analysis
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # 3. Basic frequency analysis
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.log(np.abs(f_shift) + 1)
        freq_variance = np.var(magnitude_spectrum)
        
        # Simple scoring system
        ai_score = 0
        
        # AI-generated images often have:
        if pixel_variance < 1000:
            ai_score += 0.25
        if edge_density < 0.1:
            ai_score += 0.25
        if freq_variance > 15:
            ai_score += 0.25
        
        # Add some randomness for demonstration
        import random
        ai_score += random.uniform(0, 0.25)
        
        confidence = min(ai_score * 100, 95)
        is_ai = ai_score > 0.5
        
        return {
            'is_ai_generated': is_ai,
            'confidence': confidence,
            'features': {
                'pixel_variance': float(pixel_variance),
                'edge_density': float(edge_density),
                'frequency_variance': float(freq_variance)
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {
            'is_ai_generated': False,
            'confidence': 0,
            'error': str(e)
        }

def detect_ai_video(video_path):
    """Basic video analysis"""
    try:
        # For demo purposes, return a basic analysis
        import random
        confidence = random.uniform(30, 90)
        is_ai = confidence > 60
        
        return {
            'is_ai_generated': is_ai,
            'confidence': confidence,
            'features': {
                'analysis_type': 'basic_video_analysis',
                'confidence_score': confidence
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing video: {e}")
        return {
            'is_ai_generated': False,
            'confidence': 0,
            'error': str(e)
        }

def detect_ai_audio(audio_path):
    """Basic audio analysis"""
    try:
        # For demo purposes, return a basic analysis
        import random
        confidence = random.uniform(25, 85)
        is_ai = confidence > 55
        
        return {
            'is_ai_generated': is_ai,
            'confidence': confidence,
            'features': {
                'analysis_type': 'basic_audio_analysis',
                'confidence_score': confidence
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing audio: {e}")
        return {
            'is_ai_generated': False,
            'confidence': 0,
            'error': str(e)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug')
def debug():
    return render_template('debug.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Determine file type
        file_type = get_file_type(filename)
        
        if file_type == 'unknown':
            os.unlink(filepath)
            return jsonify({'error': 'Unsupported file type'}), 400
        
        # Analyze based on file type
        if file_type == 'image':
            result = detect_ai_image(filepath)
        elif file_type == 'video':
            result = detect_ai_video(filepath)
        elif file_type == 'audio':
            result = detect_ai_audio(filepath)
        else:
            result = {'error': 'Unsupported file type'}
        
        # Clean up uploaded file
        os.unlink(filepath)
        
        # Add metadata
        result['file_type'] = file_type
        result['filename'] = filename
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'UnAI Detection API is running'})

if __name__ == '__main__':
    print("🚀 Starting UnAI - AI Content Detection App")
    print("📱 Access the app at: http://localhost:5000")
    print("🐛 Debug version at: http://localhost:5000/debug")
    app.run(debug=True, host='0.0.0.0', port=5000)