# app_enhanced.py
# Enhanced Flask application with ML, image processing, and location visualization

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
import json
import sqlite3
from datetime import datetime
import logging
import hashlib
import secrets

# Import our enhanced modules
try:
    from ml_defect_detector import HybridDefectDetector
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML module not available, falling back to rule-based detection")

try:
    from image_defect_processor import ImageDefectProcessor
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    print("Image processing not available")

# Original modules
import fitz  # PyMuPDF
from docx import Document
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'}

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize processors
if ML_AVAILABLE:
    ml_detector = HybridDefectDetector()
    logger.info("ML detector initialized")
else:
    ml_detector = None

if IMAGE_PROCESSING_AVAILABLE:
    image_processor = ImageDefectProcessor()
    logger.info("Image processor initialized")
else:
    image_processor = None

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_image_file(filename):
    image_extensions = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in image_extensions

def is_document_file(filename):
    doc_extensions = {'pdf', 'docx', 'doc'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in doc_extensions

def init_database():
    """Initialize SQLite database with enhanced schema"""
    conn = sqlite3.connect('defect_analysis.db')
    cursor = conn.cursor()
    
    # Enhanced analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            analysis_time TIMESTAMP,
            total_defects INTEGER,
            defect_categories TEXT,
            ml_confidence_score REAL,
            processing_method TEXT,
            file_hash TEXT
        )
    ''')
    
    # Enhanced defects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS defects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            defect_type TEXT NOT NULL,
            severity TEXT,
            confidence REAL,
            sentence TEXT,
            location TEXT,
            coordinates TEXT,
            detection_method TEXT,
            FOREIGN KEY (analysis_id) REFERENCES analysis (id)
        )
    ''')
    
    # New image analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            image_name TEXT,
            defects_found INTEGER,
            confidence_scores TEXT,
            annotated_image_path TEXT,
            processing_time REAL,
            FOREIGN KEY (analysis_id) REFERENCES analysis (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of file for duplicate detection"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""

def detect_defects_basic(text):
    """Basic rule-based defect detection (fallback)"""
    defects = []
    sentences = text.split('.')
    
    defect_patterns = {
        'Cracks': [
            r'crack[s]?', r'fissure[s]?', r'split[s]?', r'fracture[s]?'
        ],
        'Damp': [
            r'damp[ness]?', r'moist[ure]?', r'wet[ness]?', r'humid[ity]?'
        ],
        'Corrosion': [
            r'rust[ing]?', r'corros[ion|ive]', r'oxid[ation|ized]'
        ],
        'Mold': [
            r'mold', r'mould', r'fungus', r'mildew'
        ],
        'Structural': [
            r'structural damage', r'beam damage', r'foundation issue',
            r'wall damage', r'ceiling damage'
        ],
        'Electrical': [
            r'electrical fault', r'wiring issue', r'electrical damage',
            r'power problem'
        ],
        'Plumbing': [
            r'plumbing issue', r'pipe damage', r'leak[age]?',
            r'water damage'
        ]
    }
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:
            continue
            
        for defect_type, patterns in defect_patterns.items():
            for pattern in patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    confidence = 0.7  # Basic confidence
                    defects.append({
                        'type': defect_type,
                        'sentence': sentence,
                        'confidence': confidence,
                        'severity': 'Medium',
                        'detection_method': 'rule_based'
                    })
                    break
    
    return defects

def process_document(file_path, filename):
    """Process document with enhanced ML detection"""
    try:
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            file_type = 'PDF'
        elif filename.lower().endswith(('.docx', '.doc')):
            text = extract_text_from_docx(file_path)
            file_type = 'DOCX'
        else:
            return None, "Unsupported file type"
        
        if not text or len(text.strip()) < 50:
            return None, "No readable text found in document"
        
        # Use ML detector if available, otherwise fall back to basic
        if ml_detector and ML_AVAILABLE:
            try:
                defects = ml_detector.detect_defects(text)
                processing_method = 'hybrid_ml'
                ml_confidence = sum(d.get('confidence', 0) for d in defects) / len(defects) if defects else 0
            except Exception as e:
                logger.warning(f"ML detection failed, using basic: {e}")
                defects = detect_defects_basic(text)
                processing_method = 'rule_based'
                ml_confidence = 0.7
        else:
            defects = detect_defects_basic(text)
            processing_method = 'rule_based'
            ml_confidence = 0.7
        
        # Calculate file hash for duplicate detection
        file_hash = calculate_file_hash(file_path)
        
        # Store results in database
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        defect_categories = list(set([d['type'] for d in defects]))
        
        cursor.execute('''
            INSERT INTO analysis 
            (filename, file_type, analysis_time, total_defects, defect_categories, 
             ml_confidence_score, processing_method, file_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            filename, file_type, datetime.now(), len(defects), 
            json.dumps(defect_categories), ml_confidence, processing_method, file_hash
        ))
        
        analysis_id = cursor.lastrowid
        
        # Store individual defects
        for defect in defects:
            cursor.execute('''
                INSERT INTO defects 
                (analysis_id, defect_type, severity, confidence, sentence, detection_method)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id, defect['type'], defect.get('severity', 'Medium'),
                defect.get('confidence', 0.7), defect['sentence'],
                defect.get('detection_method', processing_method)
            ))
        
        conn.commit()
        conn.close()
        
        return {
            'analysis_id': analysis_id,
            'filename': filename,
            'file_type': file_type,
            'total_defects': len(defects),
            'defects': defects,
            'ml_confidence': ml_confidence,
            'processing_method': processing_method,
            'defect_categories': defect_categories
        }, None
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return None, f"Processing error: {str(e)}"

def process_images(file_path, filename):
    """Process image file for visual defect detection"""
    if not image_processor or not IMAGE_PROCESSING_AVAILABLE:
        return None, "Image processing not available"
    
    try:
        # Process the image
        result = image_processor.process_image(file_path, filename)
        
        if "error" in result:
            return None, result["error"]
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return None, f"Image processing error: {str(e)}"

@app.route('/')
def index():
    return render_template('index_enhanced.html', 
                         ml_available=ML_AVAILABLE,
                         image_processing_available=IMAGE_PROCESSING_AVAILABLE)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            if is_document_file(filename):
                # Process document
                result, error = process_document(file_path, filename)
                if error:
                    flash(f'Error processing document: {error}')
                    return redirect(url_for('index'))
                
                return render_template('results_enhanced.html', 
                                     result=result,
                                     result_type='document')
            
            elif is_image_file(filename):
                # Process image
                result, error = process_images(file_path, filename)
                if error:
                    flash(f'Error processing image: {error}')
                    return redirect(url_for('index'))
                
                return render_template('results_enhanced.html', 
                                     result=result,
                                     result_type='image')
            
            else:
                flash('Unsupported file type')
                return redirect(url_for('index'))
                
        except Exception as e:
            logger.error(f"Upload processing error: {e}")
            flash(f'Processing error: {str(e)}')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Enhanced dashboard with ML and image analysis statistics"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        # Get analysis statistics
        cursor.execute('SELECT COUNT(*) FROM analysis')
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(total_defects) FROM analysis')
        total_defects = cursor.fetchone()[0] or 0
        
        # Get processing method distribution
        cursor.execute('''
            SELECT processing_method, COUNT(*) 
            FROM analysis 
            GROUP BY processing_method
        ''')
        method_distribution = dict(cursor.fetchall())
        
        # Get recent analyses
        cursor.execute('''
            SELECT id, filename, file_type, total_defects, 
                   ml_confidence_score, processing_method, analysis_time
            FROM analysis 
            ORDER BY analysis_time DESC 
            LIMIT 10
        ''')
        recent_analyses = cursor.fetchall()
        
        # Get defect type distribution
        cursor.execute('''
            SELECT defect_type, COUNT(*) 
            FROM defects 
            GROUP BY defect_type 
            ORDER BY COUNT(*) DESC
        ''')
        defect_distribution = cursor.fetchall()
        
        # Get average confidence by method
        cursor.execute('''
            SELECT processing_method, AVG(ml_confidence_score) 
            FROM analysis 
            WHERE ml_confidence_score IS NOT NULL
            GROUP BY processing_method
        ''')
        confidence_by_method = dict(cursor.fetchall())
        
        conn.close()
        
        return render_template('dashboard_enhanced.html',
                             total_analyses=total_analyses,
                             total_defects=total_defects,
                             method_distribution=method_distribution,
                             recent_analyses=recent_analyses,
                             defect_distribution=defect_distribution,
                             confidence_by_method=confidence_by_method,
                             ml_available=ML_AVAILABLE,
                             image_processing_available=IMAGE_PROCESSING_AVAILABLE)
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash(f'Dashboard error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/analysis/<int:analysis_id>')
def analysis_detail(analysis_id):
    """Enhanced analysis detail view with location visualization"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        # Get analysis info
        cursor.execute('''
            SELECT * FROM analysis WHERE id = ?
        ''', (analysis_id,))
        analysis = cursor.fetchone()
        
        if not analysis:
            flash('Analysis not found')
            return redirect(url_for('dashboard'))
        
        # Get defects
        cursor.execute('''
            SELECT * FROM defects WHERE analysis_id = ?
        ''', (analysis_id,))
        defects = cursor.fetchall()
        
        # Get image analysis if available
        cursor.execute('''
            SELECT * FROM image_analysis WHERE analysis_id = ?
        ''', (analysis_id,))
        image_analysis = cursor.fetchone()
        
        conn.close()
        
        # Prepare data for location visualization
        defect_data = []
        for defect in defects:
            defect_data.append({
                'type': defect[2],  # defect_type
                'severity': defect[3],  # severity
                'confidence': defect[4],  # confidence
                'sentence': defect[5],  # sentence
                'location': defect[6] or 'unknown',  # location
                'detection_method': defect[8]  # detection_method
            })
        
        return render_template('analysis_detail_enhanced.html',
                             analysis=analysis,
                             defects=defect_data,
                             image_analysis=image_analysis,
                             defect_json=json.dumps(defect_data))
    
    except Exception as e:
        logger.error(f"Analysis detail error: {e}")
        flash(f'Error loading analysis: {str(e)}')
        return redirect(url_for('dashboard'))

@app.route('/api/health')
def health_check():
    """Enhanced health check with system status"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ml_available': ML_AVAILABLE,
        'image_processing_available': IMAGE_PROCESSING_AVAILABLE,
        'database_connected': True
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM analysis')
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(total_defects) FROM analysis')
        total_defects = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT processing_method, COUNT(*) 
            FROM analysis 
            GROUP BY processing_method
        ''')
        method_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return jsonify({
            'total_analyses': total_analyses,
            'total_defects': total_defects,
            'method_distribution': method_stats,
            'ml_available': ML_AVAILABLE,
            'image_processing_available': IMAGE_PROCESSING_AVAILABLE
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_database()
    logger.info("Enhanced Defect Detector starting...")
    logger.info(f"ML Detection: {'Enabled' if ML_AVAILABLE else 'Disabled'}")
    logger.info(f"Image Processing: {'Enabled' if IMAGE_PROCESSING_AVAILABLE else 'Disabled'}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
