# app_fixed.py
# Fixed Flask application with robust error handling and simplified ML

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
from docx import Document
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'doc'}

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize detector
if ML_AVAILABLE:
    ml_detector = HybridDefectDetector()
    logger.info("✅ ML detector initialized")
    logger.info(f"Capabilities: {ml_detector.get_capabilities()}")
else:
    ml_detector = None
    logger.info("⚠️ Using rule-based detection only")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('defect_analysis.db')
    cursor = conn.cursor()
    
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS defects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            defect_type TEXT NOT NULL,
            severity TEXT,
            confidence REAL,
            sentence TEXT,
            detection_method TEXT,
            FOREIGN KEY (analysis_id) REFERENCES analysis (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of file"""
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

def detect_defects_fallback(text):
    """Fallback rule-based defect detection"""
    defects = []
    sentences = text.split('.')
    
    defect_patterns = {
        'Cracks': [r'crack[s]?', r'fissure[s]?', r'split[s]?', r'fracture[s]?'],
        'Damp': [r'damp[ness]?', r'moist[ure]?', r'wet[ness]?', r'humid[ity]?'],
        'Corrosion': [r'rust[ing]?', r'corros[ion|ive]', r'oxid[ation|ized]'],
        'Mold': [r'mold', r'mould', r'fungus', r'mildew'],
        'Structural': [r'structural', r'foundation', r'beam', r'support'],
        'Electrical': [r'electrical', r'wiring', r'circuit', r'panel'],
        'Plumbing': [r'plumbing', r'pipe', r'leak', r'drain']
    }
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:
            continue
            
        for defect_type, patterns in defect_patterns.items():
            for pattern in patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    defects.append({
                        'type': defect_type,
                        'sentence': sentence,
                        'confidence': 0.7,
                        'severity': 'Medium',
                        'detection_method': 'rule_based_fallback'
                    })
                    break
    
    return defects

def process_document(file_path, filename):
    """Process document with enhanced detection"""
    try:
        # Extract text
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
        
        # Detect defects
        if ml_detector:
            try:
                defects = ml_detector.detect_defects(text)
                processing_method = 'hybrid_ml'
                ml_confidence = sum(d.get('confidence', 0) for d in defects) / len(defects) if defects else 0
            except Exception as e:
                logger.warning(f"ML detection failed, using fallback: {e}")
                defects = detect_defects_fallback(text)
                processing_method = 'rule_based_fallback'
                ml_confidence = 0.7
        else:
            defects = detect_defects_fallback(text)
            processing_method = 'rule_based_fallback'
            ml_confidence = 0.7
        
        # Calculate file hash
        file_hash = calculate_file_hash(file_path)
        
        # Store in database
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
        
        # Store defects
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

@app.route('/')
def index():
    return render_template('index.html', ml_available=ML_AVAILABLE)

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
            result, error = process_document(file_path, filename)
            if error:
                flash(f'Error processing document: {error}')
                return redirect(url_for('index'))
            
            return render_template('results_simple.html', result=result)
                
        except Exception as e:
            logger.error(f"Upload processing error: {e}")
            flash(f'Processing error: {str(e)}')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload PDF or DOCX files.')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Simple dashboard"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM analysis')
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(total_defects) FROM analysis')
        total_defects = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT id, filename, file_type, total_defects, 
                   processing_method, analysis_time
            FROM analysis 
            ORDER BY analysis_time DESC 
            LIMIT 10
        ''')
        recent_analyses = cursor.fetchall()
        
        cursor.execute('''
            SELECT defect_type, COUNT(*) 
            FROM defects 
            GROUP BY defect_type 
            ORDER BY COUNT(*) DESC
        ''')
        defect_distribution = cursor.fetchall()
        
        conn.close()
        
        return render_template('dashboard_simple.html',
                             total_analyses=total_analyses,
                             total_defects=total_defects,
                             recent_analyses=recent_analyses,
                             defect_distribution=defect_distribution,
                             ml_available=ML_AVAILABLE)
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash(f'Dashboard error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/analysis/<int:analysis_id>')
def analysis_detail(analysis_id):
    """Analysis detail view"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analysis WHERE id = ?', (analysis_id,))
        analysis = cursor.fetchone()
        
        if not analysis:
            flash('Analysis not found')
            return redirect(url_for('dashboard'))
        
        cursor.execute('SELECT * FROM defects WHERE analysis_id = ?', (analysis_id,))
        defects = cursor.fetchall()
        
        conn.close()
        
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
            
            # Get analysis info before deletion for logging
            cursor.execute('SELECT filename FROM analysis WHERE id = ?', (analysis_id,))
            result = cursor.fetchone()
            
            if not result:
                flash('Analysis not found.', 'error')
                return redirect(url_for('dashboard'))
            
            filename = result[0]
            
            # Delete related defects first (cascade delete)
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
def health_status():
    """Health status page"""
    try:
        # Test database connection
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        database_connected = True
        conn.close()
    except:
        database_connected = False
    
    return render_template('health.html',
                         status='healthy' if database_connected else 'unhealthy',
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         ml_available=ML_AVAILABLE,
                         database_connected=database_connected)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ml_available': ML_AVAILABLE,
        'database_connected': True
    })

@app.route('/test-sample')
def test_sample():
    """Test with the sample survey document"""
    try:
        sample_path = 'sample_building_survey.txt'
        if not os.path.exists(sample_path):
            flash('Sample file not found')
            return redirect(url_for('index'))
        
        with open(sample_path, 'r') as f:
            text = f.read()
        
        if ml_detector:
            defects = ml_detector.detect_defects(text)
            capabilities = ml_detector.get_capabilities()
        else:
            defects = detect_defects_fallback(text)
            capabilities = {'ml_available': False, 'rule_based_available': True, 'hybrid_mode': False}
        
        # Format the results like a normal analysis
        result = {
            'filename': 'sample_building_survey.txt (Test Sample)',
            'file_type': 'TXT',
            'total_defects': len(defects),
            'defects': defects,
            'ml_confidence': 0.85,
            'processing_method': 'sample_test',
            'defect_categories': list(set([d['type'] for d in defects]))
        }
        
        return render_template('results.html',
                             filename=result['filename'],
                             total_defects=result['total_defects'],
                             defects=defects,
                             summary=result['defect_categories'],
                             report=result,
                             prev_id=None,
                             next_id=None,
                             is_sample=True)
        
    except Exception as e:
        logger.error(f"Test sample error: {e}")
        flash(f'Error processing sample: {str(e)}')
        return redirect(url_for('index'))

@app.route('/reports')
def reports_history():
    """Show history of all analyzed reports with navigation"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        # Get all reports from analysis table
        cursor.execute('''
            SELECT id, filename, upload_time, file_type, total_defects
            FROM analysis 
            ORDER BY upload_time DESC
        ''')
        
        reports = []
        for row in cursor.fetchall():
            # Determine priority based on defect count
            defect_count = row[4] or 0
            if defect_count >= 15:
                priority = "High Priority"
            elif defect_count >= 5:
                priority = "Medium Priority"
            else:
                priority = "Low Priority"
                
            reports.append({
                'id': row[0],
                'filename': row[1],
                'upload_date': row[2],
                'file_type': row[3],
                'total_defects': defect_count,
                'priority': priority
            })
        
        conn.close()
        
        print(f"✅ Reports history loaded: {len(reports)} reports found")
        
        return render_template('reports_history.html', 
                             reports=reports)
        
    except Exception as e:
        print(f"Error loading reports history: {e}")
        return f"Error loading reports: {str(e)}", 500

@app.route('/report/<int:report_id>')
def view_report(report_id):
    """Display a specific report with navigation"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        # Get report details
        cursor.execute('''
            SELECT id, filename, upload_time, file_type, total_defects, defect_categories
            FROM analysis WHERE id = ?
        ''', (report_id,))
        
        report_data = cursor.fetchone()
        if not report_data:
            return "Report not found", 404
        
        # Get defects for this report
        cursor.execute('''
            SELECT defect_type, severity, confidence, sentence
            FROM defects WHERE analysis_id = ?
            ORDER BY confidence DESC
        ''', (report_id,))
        
        defects = cursor.fetchall()
        
        # Get navigation (previous/next reports)
        cursor.execute('SELECT id FROM analysis WHERE id < ? ORDER BY id DESC LIMIT 1', (report_id,))
        prev_result = cursor.fetchone()
        prev_id = prev_result[0] if prev_result else None
        
        cursor.execute('SELECT id FROM analysis WHERE id > ? ORDER BY id ASC LIMIT 1', (report_id,))
        next_result = cursor.fetchone()
        next_id = next_result[0] if next_result else None
        
        conn.close()
        
        # Format report data
        report = {
            'id': report_data[0],
            'filename': report_data[1],
            'upload_date': report_data[2],
            'file_type': report_data[3],
            'total_defects': report_data[4],
            'defect_categories': json.loads(report_data[5]) if report_data[5] else {}
        }
        
        # Format defects
        formatted_defects = []
        for defect in defects:
            formatted_defects.append({
                'type': defect[0],
                'severity': defect[1],
                'confidence': defect[2],
                'sentence': defect[3],
                'keyword': defect[0].lower()  # Use defect type as keyword
            })
        
        return render_template('results.html',
                             filename=report['filename'],
                             total_defects=report['total_defects'],
                             defects=formatted_defects,
                             summary=report['defect_categories'],
                             report=report,
                             prev_id=prev_id,
                             next_id=next_id)
        
    except Exception as e:
        print(f"Error loading report {report_id}: {e}")
        return f"Error loading report: {str(e)}", 500

if __name__ == '__main__':
    init_database()
    logger.info("Fixed Defect Detector starting...")
    logger.info(f"ML Detection: {'Enabled' if ML_AVAILABLE else 'Disabled'}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
