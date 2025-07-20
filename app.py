import os
import io
import magic
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import cv2
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from transformers import pipeline
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip
import tempfile
import logging
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
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

class SimpleAIDetector(nn.Module):
    """Simple CNN-based AI detector for images"""
    def __init__(self, num_classes=2):
        super(SimpleAIDetector, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.AdaptiveAvgPool2d((7, 7))
        )
        self.classifier = nn.Sequential(
            nn.Linear(128 * 7 * 7, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

# Initialize models
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
image_detector = SimpleAIDetector().to(device)

# Image preprocessing
image_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def allowed_file(filename, file_type):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[file_type]

def get_file_type(filepath):
    """Determine file type using python-magic"""
    try:
        mime = magic.from_file(filepath, mime=True)
        if mime.startswith('image/'):
            return 'image'
        elif mime.startswith('video/'):
            return 'video'
        elif mime.startswith('audio/'):
            return 'audio'
        else:
            return 'unknown'
    except Exception as e:
        logger.error(f"Error determining file type: {e}")
        return 'unknown'

def detect_ai_image(image_path):
    """Detect if an image is AI-generated using multiple techniques"""
    try:
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        
        # Method 1: Statistical analysis
        img_array = np.array(image)
        
        # Check for unusual patterns that might indicate AI generation
        # 1. Pixel distribution analysis
        pixel_variance = np.var(img_array)
        pixel_mean = np.mean(img_array)
        
        # 2. Edge detection analysis
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # 3. Frequency domain analysis
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.log(np.abs(f_shift) + 1)
        freq_variance = np.var(magnitude_spectrum)
        
        # 4. Texture analysis using Local Binary Patterns
        def calculate_lbp_variance(image):
            lbp_values = []
            for i in range(1, image.shape[0]-1):
                for j in range(1, image.shape[1]-1):
                    center = image[i, j]
                    binary_string = ''
                    for di in [-1, -1, -1, 0, 0, 1, 1, 1]:
                        for dj in [-1, 0, 1, -1, 1, -1, 0, 1]:
                            if len(binary_string) < 8:
                                neighbor = image[i + di, j + dj]
                                binary_string += '1' if neighbor >= center else '0'
                    lbp_values.append(int(binary_string, 2))
            return np.var(lbp_values) if lbp_values else 0
        
        lbp_variance = calculate_lbp_variance(gray)
        
        # Simple scoring system based on statistical features
        ai_score = 0
        
        # AI-generated images often have:
        # - More uniform pixel distribution
        if pixel_variance < 1000:
            ai_score += 0.2
        
        # - Smoother edges
        if edge_density < 0.1:
            ai_score += 0.2
        
        # - Different frequency characteristics
        if freq_variance > 15:
            ai_score += 0.2
        
        # - More uniform textures
        if lbp_variance < 500:
            ai_score += 0.2
        
        # Additional heuristics for common AI artifacts
        # Check for perfect symmetries or repeated patterns
        height, width = gray.shape
        if height > 100 and width > 100:
            # Check for unusual uniformity in quarters
            quarters = [
                gray[:height//2, :width//2],
                gray[:height//2, width//2:],
                gray[height//2:, :width//2],
                gray[height//2:, width//2:]
            ]
            quarter_vars = [np.var(q) for q in quarters]
            if max(quarter_vars) - min(quarter_vars) < 100:
                ai_score += 0.2
        
        confidence = min(ai_score * 100, 95)  # Cap at 95%
        is_ai = ai_score > 0.5
        
        return {
            'is_ai_generated': is_ai,
            'confidence': confidence,
            'features': {
                'pixel_variance': float(pixel_variance),
                'edge_density': float(edge_density),
                'frequency_variance': float(freq_variance),
                'texture_variance': float(lbp_variance)
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
    """Detect if a video is AI-generated"""
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        fps = clip.fps
        
        # Extract frames for analysis
        frame_times = np.linspace(0, min(duration, 30), min(10, int(duration)))  # Max 10 frames
        frames_analysis = []
        
        for t in frame_times:
            frame = clip.get_frame(t)
            
            # Convert frame to PIL Image and analyze
            frame_image = Image.fromarray(frame)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                frame_image.save(temp_file.name)
                frame_result = detect_ai_image(temp_file.name)
                frames_analysis.append(frame_result['confidence'])
                os.unlink(temp_file.name)
        
        clip.close()
        
        # Average confidence across frames
        avg_confidence = np.mean(frames_analysis) if frames_analysis else 0
        
        # Additional video-specific checks
        # AI videos often have consistent quality/style across frames
        confidence_variance = np.var(frames_analysis) if len(frames_analysis) > 1 else 0
        
        # Lower variance might indicate AI generation
        if confidence_variance < 100:
            avg_confidence += 10
        
        is_ai = avg_confidence > 50
        
        return {
            'is_ai_generated': is_ai,
            'confidence': min(avg_confidence, 95),
            'frames_analyzed': len(frames_analysis),
            'duration': duration
        }
        
    except Exception as e:
        logger.error(f"Error analyzing video: {e}")
        return {
            'is_ai_generated': False,
            'confidence': 0,
            'error': str(e)
        }

def detect_ai_audio(audio_path):
    """Detect if audio is AI-generated"""
    try:
        # Load audio file
        y, sr = librosa.load(audio_path, sr=None)
        
        # Extract features
        # 1. Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        
        # 2. MFCCs (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # 3. Tempo and rhythm
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # Analyze features for AI characteristics
        ai_score = 0
        
        # AI-generated audio often has:
        # - More consistent spectral characteristics
        spectral_variance = np.var(spectral_centroids)
        if spectral_variance < 1000000:
            ai_score += 0.2
        
        # - Regular patterns in MFCCs
        mfcc_variance = np.mean([np.var(mfcc) for mfcc in mfccs])
        if mfcc_variance < 100:
            ai_score += 0.2
        
        # - Consistent tempo
        if len(beats) > 10:
            beat_intervals = np.diff(beats)
            beat_variance = np.var(beat_intervals)
            if beat_variance < 0.1:
                ai_score += 0.2
        
        # - Unusual frequency distribution
        if np.mean(spectral_rolloff) > sr * 0.4:
            ai_score += 0.2
        
        confidence = min(ai_score * 100, 95)
        is_ai = ai_score > 0.5
        
        return {
            'is_ai_generated': is_ai,
            'confidence': confidence,
            'features': {
                'spectral_variance': float(spectral_variance),
                'mfcc_variance': float(mfcc_variance),
                'tempo': float(tempo),
                'duration': len(y) / sr
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
        file_type = get_file_type(filepath)
        
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
    app.run(debug=True, host='0.0.0.0', port=5000)