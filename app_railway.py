# app_railway.py
# Production-ready Flask application for Railway deployment

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
import json
import sqlite3
from datetime import datetime
import logging
import hashlib
import secrets

# Import our simplified ML detector
try:
    from ml_defect_detector_simple import HybridDefectDetector
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML module not available, using rule-based detection only")

# Document processing
import fitz  # PyMuPDF
try:
    from docx import Document
except ImportError:
    print("python-docx not available")
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'doc', 'txt'}

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize detector
if ML_AVAILABLE:
    try:
        ml_detector = HybridDefectDetector()
        logger.info("✅ ML detector initialized")
    except Exception as e:
        logger.error(f"ML detector failed to initialize: {e}")
        ml_detector = None
        ML_AVAILABLE = False
else:
    ml_detector = None
    logger.info("⚠️ Using rule-based detection only")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_database():
    """Initialize the SQLite database"""
    try:
        with sqlite3.connect('defect_analysis.db') as conn:
            cursor = conn.cursor()
            
            # Create analysis table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                defect_count INTEGER DEFAULT 0,
                analysis_date TEXT NOT NULL,
                upload_time TEXT NOT NULL,
                file_hash TEXT
            )
            ''')
            
            # Create defects table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS defects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                defect_type TEXT NOT NULL,
                severity TEXT,
                confidence REAL,
                sentence TEXT,
                detection_method TEXT,
                FOREIGN KEY (analysis_id) REFERENCES analysis (id)
            )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

def allowed_file(filename):
    """Check if file type is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_file(file_path, file_type):
    """Extract text from uploaded files"""
    try:
        if file_type == 'pdf':
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        
        elif file_type == 'docx':
            try:
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except:
                return "Error reading DOCX file"
        
        elif file_type == 'txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        return "Unsupported file type"
    
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        return f"Error extracting text: {str(e)}"

def detect_defects_fallback(text):
    """Fallback rule-based defect detection"""
    defects = []
    
    defect_patterns = {
        'Cracks': [r'crack[s]?', r'fracture[s]?', r'split[s]?', r'fissure[s]?'],
        'Damp': [r'damp[ness]?', r'moisture', r'wet[ness]?', r'humid[ity]?'],
        'Mold': [r'mold', r'mould', r'fungus', r'spore[s]?'],
        'Structural': [r'structural', r'foundation', r'beam[s]?', r'support[s]?'],
        'Electrical': [r'electrical', r'wiring', r'cable[s]?', r'outlet[s]?'],
        'Plumbing': [r'plumbing', r'pipe[s]?', r'leak[s]?', r'drain[s]?'],
        'Corrosion': [r'rust[y]?', r'corrosion', r'oxidation', r'deteriorat']
    }
    
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:
            continue
            
        sentence_lower = sentence.lower()
        
        for defect_type, patterns in defect_patterns.items():
            for pattern in patterns:
                if re.search(pattern, sentence_lower):
                    confidence = 0.7 + (len(re.findall(pattern, sentence_lower)) * 0.1)
                    confidence = min(confidence, 0.95)
                    
                    defects.append({
                        'type': defect_type,
                        'sentence': sentence,
                        'confidence': confidence,
                        'severity': 'Medium',
                        'method': 'rule_based'
                    })
                    break
    
    return defects

@app.route('/')
def index():
    """Main upload page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    try:
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Extract text
            file_type = filename.rsplit('.', 1)[1].lower()
            text = extract_text_from_file(file_path, file_type)
            
            # Analyze for defects
            if ml_detector and ML_AVAILABLE:
                try:
                    defects = ml_detector.detect_defects(text)
                except Exception as e:
                    logger.error(f"ML detection failed: {e}")
                    defects = detect_defects_fallback(text)
            else:
                defects = detect_defects_fallback(text)
            
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            # Save to database
            with sqlite3.connect('defect_analysis.db') as conn:
                cursor = conn.cursor()
                
                # Insert analysis
                cursor.execute('''
                    INSERT INTO analysis (filename, file_type, defect_count, analysis_date, upload_time, file_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (filename, file_type, len(defects), 
                     datetime.now().strftime('%Y-%m-%d'), 
                     datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     file_hash))
                
                analysis_id = cursor.lastrowid
                
                # Insert defects
                for defect in defects:
                    cursor.execute('''
                        INSERT INTO defects (analysis_id, defect_type, severity, confidence, sentence, detection_method)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (analysis_id, defect['type'], defect.get('severity', 'Medium'),
                         defect['confidence'], defect['sentence'], defect.get('method', 'unknown')))
                
                conn.commit()
            
            # Clean up uploaded file
            os.remove(file_path)
            
            return redirect(url_for('results', analysis_id=analysis_id))
        
        else:
            flash('File type not allowed. Please upload PDF, DOCX, or TXT files.')
            return redirect(request.url)
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        flash(f'Error processing file: {str(e)}')
        return redirect(url_for('index'))

@app.route('/results/<int:analysis_id>')
def results(analysis_id):
    """Display analysis results"""
    try:
        with sqlite3.connect('defect_analysis.db') as conn:
            cursor = conn.cursor()
            
            # Get analysis info
            cursor.execute('SELECT * FROM analysis WHERE id = ?', (analysis_id,))
            analysis = cursor.fetchone()
            
            if not analysis:
                flash('Analysis not found')
                return redirect(url_for('index'))
            
            # Get defects
            cursor.execute('SELECT * FROM defects WHERE analysis_id = ?', (analysis_id,))
            defects = cursor.fetchall()
            
            return render_template('results_simple.html', 
                                 analysis=analysis, 
                                 defects=defects)
    
    except Exception as e:
        logger.error(f"Results error: {e}")
        flash(f'Error loading results: {str(e)}')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Simple dashboard"""
    try:
        with sqlite3.connect('defect_analysis.db') as conn:
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute('SELECT COUNT(*) FROM analysis')
            total_analyses = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM defects')
            total_defects = cursor.fetchone()[0]
            
            # Get recent analyses
            cursor.execute('''
                SELECT id, filename, file_type, defect_count, analysis_date, upload_time
                FROM analysis 
                ORDER BY upload_time DESC 
                LIMIT 10
            ''')
            recent_analyses = cursor.fetchall()
            
            # Get defect distribution
            cursor.execute('''
                SELECT defect_type, COUNT(*) 
                FROM defects 
                GROUP BY defect_type 
                ORDER BY COUNT(*) DESC
            ''')
            defect_distribution = cursor.fetchall()
            
            return render_template('dashboard_simple.html',
                                 total_analyses=total_analyses,
                                 total_defects=total_defects,
                                 recent_analyses=recent_analyses,
                                 defect_distribution=defect_distribution,
                                 ml_available=ML_AVAILABLE)
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash(f'Dashboard error: {str(e)}')
        return render_template('dashboard_simple.html',
                             total_analyses=0,
                             total_defects=0,
                             recent_analyses=[],
                             defect_distribution=[],
                             ml_available=ML_AVAILABLE)

@app.route('/analysis/<int:analysis_id>')
def analysis_detail(analysis_id):
    """Detailed analysis view"""
    try:
        with sqlite3.connect('defect_analysis.db') as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM analysis WHERE id = ?', (analysis_id,))
            analysis = cursor.fetchone()
            
            if not analysis:
                flash('Analysis not found')
                return redirect(url_for('dashboard'))
            
            cursor.execute('SELECT * FROM defects WHERE analysis_id = ?', (analysis_id,))
            defects = cursor.fetchall()
            
            return render_template('analysis_detail_final.html',
                                 analysis=analysis,
                                 defects=defects)
    
    except Exception as e:
        logger.error(f"Analysis detail error: {e}")
        flash(f'Error loading analysis: {str(e)}')
        return redirect(url_for('dashboard'))

@app.route('/delete_analysis/<int:analysis_id>', methods=['POST'])
def delete_analysis(analysis_id):
    """Delete an analysis and all its related defects"""
    try:
        with sqlite3.connect('defect_analysis.db') as conn:
            cursor = conn.cursor()
            
            # Get analysis info before deletion
            cursor.execute('SELECT filename FROM analysis WHERE id = ?', (analysis_id,))
            result = cursor.fetchone()
            
            if not result:
                flash('Analysis not found.', 'error')
                return redirect(url_for('dashboard'))
            
            filename = result[0]
            
            # Delete related defects first
            cursor.execute('DELETE FROM defects WHERE analysis_id = ?', (analysis_id,))
            defects_deleted = cursor.rowcount
            
            # Delete the analysis
            cursor.execute('DELETE FROM analysis WHERE id = ?', (analysis_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                flash(f'Successfully deleted analysis "{filename}" and {defects_deleted} related defects.', 'success')
                logger.info(f"Deleted analysis {analysis_id}: {filename}")
            else:
                flash('Analysis not found.', 'error')
                
    except Exception as e:
        logger.error(f"Error deleting analysis {analysis_id}: {e}")
        flash(f'Error deleting analysis: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ml_available': ML_AVAILABLE
    })

if __name__ == '__main__':
    init_database()
    logger.info("Building Defect Detector starting for Railway...")
    logger.info(f"ML Detection: {'Enabled' if ML_AVAILABLE else 'Disabled'}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
