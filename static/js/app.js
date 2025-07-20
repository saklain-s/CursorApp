class UnAIApp {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentFile = null;
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.analysisSection = document.getElementById('analysisSection');
        this.fileInfo = document.getElementById('fileInfo');
        this.filePreview = document.getElementById('filePreview');
        this.fileName = document.getElementById('fileName');
        this.fileType = document.getElementById('fileType');
        this.loading = document.getElementById('loading');
        this.results = document.getElementById('results');
        this.verdict = document.getElementById('verdict');
        this.verdictText = document.getElementById('verdictText');
        this.confidence = document.getElementById('confidence');
        this.confidenceFill = document.getElementById('confidenceFill');
        this.confidenceText = document.getElementById('confidenceText');
        this.featuresGrid = document.getElementById('featuresGrid');
        this.explanationContent = document.getElementById('explanationContent');
        this.analyzeAnother = document.getElementById('analyzeAnother');
    }

    bindEvents() {
        // File input change
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Upload area click
        this.uploadArea.addEventListener('click', () => this.fileInput.click());

        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        // Analyze another button
        this.analyzeAnother.addEventListener('click', () => this.resetApp());

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    processFile(file) {
        this.currentFile = file;
        
        // Validate file
        if (!this.isValidFile(file)) {
            this.showError('Please select a valid image, video, or audio file.');
            return;
        }

        // Show analysis section
        this.analysisSection.style.display = 'block';
        this.showFileInfo(file);
        this.showLoading();
        
        // Start analysis
        this.analyzeFile(file);
        
        // Scroll to analysis section
        this.analysisSection.scrollIntoView({ behavior: 'smooth' });
    }

    isValidFile(file) {
        const allowedTypes = [
            'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp',
            'video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm',
            'audio/mp3', 'audio/wav', 'audio/flac', 'audio/ogg', 'audio/m4a', 'audio/mpeg'
        ];
        
        return allowedTypes.some(type => file.type.startsWith(type.split('/')[0])) && 
               file.size <= 50 * 1024 * 1024; // 50MB limit
    }

    showFileInfo(file) {
        this.fileName.textContent = file.name;
        this.fileType.textContent = this.getFileTypeDisplay(file.type);
        
        // Show file preview
        this.showFilePreview(file);
    }

    showFilePreview(file) {
        this.filePreview.innerHTML = '';
        
        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.onload = () => URL.revokeObjectURL(img.src);
            this.filePreview.appendChild(img);
        } else if (file.type.startsWith('video/')) {
            const video = document.createElement('video');
            video.src = URL.createObjectURL(file);
            video.muted = true;
            video.onloadeddata = () => URL.revokeObjectURL(video.src);
            this.filePreview.appendChild(video);
        } else if (file.type.startsWith('audio/')) {
            const icon = document.createElement('i');
            icon.className = 'fas fa-music';
            this.filePreview.appendChild(icon);
        } else {
            const icon = document.createElement('i');
            icon.className = 'fas fa-file';
            this.filePreview.appendChild(icon);
        }
    }

    getFileTypeDisplay(mimeType) {
        if (mimeType.startsWith('image/')) return 'Image';
        if (mimeType.startsWith('video/')) return 'Video';
        if (mimeType.startsWith('audio/')) return 'Audio';
        return 'File';
    }

    showLoading() {
        this.loading.style.display = 'block';
        this.results.style.display = 'none';
        this.analyzeAnother.style.display = 'none';
    }

    hideLoading() {
        this.loading.style.display = 'none';
    }

    async analyzeFile(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }

            this.displayResults(result);
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    displayResults(result) {
        this.hideLoading();
        this.results.style.display = 'block';
        this.analyzeAnother.style.display = 'flex';

        // Display verdict
        this.displayVerdict(result.is_ai_generated, result.confidence);

        // Display confidence
        this.displayConfidence(result.confidence);

        // Display features
        this.displayFeatures(result.features, result.file_type);

        // Display explanation
        this.displayExplanation(result.file_type, result.is_ai_generated);
    }

    displayVerdict(isAI, confidence) {
        const verdict = this.verdict;
        const verdictText = this.verdictText;
        
        // Clear previous classes
        verdict.classList.remove('ai', 'human', 'uncertain');
        
        if (confidence < 30) {
            verdict.classList.add('uncertain');
            verdictText.textContent = 'Uncertain';
            verdict.querySelector('i').className = 'fas fa-question-circle';
        } else if (isAI) {
            verdict.classList.add('ai');
            verdictText.textContent = 'Likely AI-Generated';
            verdict.querySelector('i').className = 'fas fa-robot';
        } else {
            verdict.classList.add('human');
            verdictText.textContent = 'Likely Human-Made';
            verdict.querySelector('i').className = 'fas fa-user';
        }
    }

    displayConfidence(confidence) {
        this.confidenceText.textContent = `${Math.round(confidence)}%`;
        this.confidenceFill.style.width = `${confidence}%`;
    }

    displayFeatures(features, fileType) {
        this.featuresGrid.innerHTML = '';
        
        if (!features) return;

        const featureDescriptions = this.getFeatureDescriptions(fileType);
        
        Object.entries(features).forEach(([key, value]) => {
            const featureItem = document.createElement('div');
            featureItem.className = 'feature-item';
            
            const title = document.createElement('h5');
            title.textContent = key.replace(/_/g, ' ');
            
            const description = document.createElement('p');
            description.textContent = featureDescriptions[key] || 'Technical analysis metric';
            
            const valueElement = document.createElement('div');
            valueElement.className = 'feature-value';
            valueElement.textContent = typeof value === 'number' ? 
                value.toFixed(2) : value.toString();
            
            featureItem.appendChild(title);
            featureItem.appendChild(description);
            featureItem.appendChild(valueElement);
            
            this.featuresGrid.appendChild(featureItem);
        });
    }

    getFeatureDescriptions(fileType) {
        const descriptions = {
            image: {
                'pixel_variance': 'Measures pixel distribution uniformity',
                'edge_density': 'Density of detected edges in the image',
                'frequency_variance': 'Frequency domain characteristics',
                'texture_variance': 'Local texture pattern analysis'
            },
            video: {
                'frames_analyzed': 'Number of frames examined',
                'duration': 'Video length in seconds'
            },
            audio: {
                'spectral_variance': 'Spectral characteristic consistency',
                'mfcc_variance': 'Mel-frequency cepstral coefficients',
                'tempo': 'Detected tempo in BPM',
                'duration': 'Audio length in seconds'
            }
        };
        
        return descriptions[fileType] || {};
    }

    displayExplanation(fileType, isAI) {
        const explanations = {
            image: {
                ai: `
                    <p>This image shows characteristics commonly found in AI-generated content:</p>
                    <ul>
                        <li><strong>Pixel Distribution:</strong> AI-generated images often have more uniform pixel distributions</li>
                        <li><strong>Edge Analysis:</strong> Smoother edges and transitions are typical of AI generation</li>
                        <li><strong>Frequency Analysis:</strong> Different frequency domain characteristics compared to natural images</li>
                        <li><strong>Texture Patterns:</strong> More regular texture patterns than typically found in real photos</li>
                    </ul>
                    <p>These patterns are analyzed using computer vision techniques to detect AI generation artifacts.</p>
                `,
                human: `
                    <p>This image shows characteristics more consistent with human-created or natural content:</p>
                    <ul>
                        <li><strong>Natural Variation:</strong> Pixel distributions show natural randomness</li>
                        <li><strong>Authentic Edges:</strong> Edge patterns consistent with real-world photography</li>
                        <li><strong>Organic Textures:</strong> Texture patterns show natural irregularities</li>
                        <li><strong>Frequency Signature:</strong> Frequency domain analysis matches natural image characteristics</li>
                    </ul>
                    <p>The analysis suggests this content was likely created through traditional photography or human artistic methods.</p>
                `
            },
            video: {
                ai: `
                    <p>This video exhibits patterns often associated with AI-generated content:</p>
                    <ul>
                        <li><strong>Frame Consistency:</strong> Unusually consistent quality across frames</li>
                        <li><strong>Temporal Analysis:</strong> Regular patterns in frame-to-frame changes</li>
                        <li><strong>Visual Artifacts:</strong> Subtle artifacts typical of AI video generation</li>
                    </ul>
                    <p>AI-generated videos often show more consistency than natural recordings.</p>
                `,
                human: `
                    <p>This video shows characteristics of authentic, human-created content:</p>
                    <ul>
                        <li><strong>Natural Variation:</strong> Frame quality varies naturally</li>
                        <li><strong>Authentic Motion:</strong> Movement patterns consistent with real-world recording</li>
                        <li><strong>Organic Changes:</strong> Natural variations in lighting and composition</li>
                    </ul>
                    <p>The analysis suggests this is likely authentic video content.</p>
                `
            },
            audio: {
                ai: `
                    <p>This audio file shows patterns that may indicate AI generation:</p>
                    <ul>
                        <li><strong>Spectral Consistency:</strong> More regular spectral characteristics than natural audio</li>
                        <li><strong>MFCC Patterns:</strong> Mel-frequency patterns typical of synthesized audio</li>
                        <li><strong>Temporal Regularity:</strong> Unusually consistent timing patterns</li>
                    </ul>
                    <p>AI-generated audio often lacks the subtle imperfections of natural recordings.</p>
                `,
                human: `
                    <p>This audio shows characteristics of natural, human-created content:</p>
                    <ul>
                        <li><strong>Natural Variation:</strong> Spectral characteristics show organic variation</li>
                        <li><strong>Authentic Patterns:</strong> MFCC analysis consistent with real recordings</li>
                        <li><strong>Organic Timing:</strong> Natural rhythm and tempo variations</li>
                    </ul>
                    <p>The analysis suggests this is likely authentic audio content.</p>
                `
            }
        };

        const explanation = explanations[fileType];
        if (explanation) {
            this.explanationContent.innerHTML = isAI ? explanation.ai : explanation.human;
        } else {
            this.explanationContent.innerHTML = '<p>Analysis completed using advanced machine learning techniques.</p>';
        }
    }

    showError(message) {
        this.hideLoading();
        
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        
        // Insert before analysis section
        this.analysisSection.insertBefore(errorDiv, this.analysisSection.firstChild);
        
        // Remove error after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }

    resetApp() {
        // Hide analysis section
        this.analysisSection.style.display = 'none';
        
        // Reset file input
        this.fileInput.value = '';
        this.currentFile = null;
        
        // Clear any errors
        const errors = this.analysisSection.querySelectorAll('.error');
        errors.forEach(error => error.remove());
        
        // Scroll back to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new UnAIApp();
});

// Add some utility functions for better UX
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}