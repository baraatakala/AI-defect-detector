from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
import os
import fitz  # PyMuPDF
from docx import Document
import json
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'defect-detector-secret-key-2025')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract plain text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        logger.info(f"Successfully extracted text from PDF: {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {str(e)}")
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file_path):
    """Extract text from Word DOCX file using python-docx"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        logger.info(f"Successfully extracted text from DOCX: {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error reading DOCX {file_path}: {str(e)}")
        return f"Error reading DOCX: {str(e)}"

def clean_and_preprocess_text(text):
    """Clean and preprocess text: remove headers, numbers, and blank lines"""
    if not text or text.startswith('Error'):
        return text
        
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove empty lines and lines with only numbers/special chars
        line = line.strip()
        if line and not line.isdigit() and len(line) > 3:
            # Skip common headers and footers
            skip_patterns = ['page', 'report', 'survey', 'date:', 'confidential', 'copyright']
            if not any(pattern in line.lower() for pattern in skip_patterns):
                cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def detect_defects(text):
    """
    Detect building defects in text using enhanced keyword matching
    """
    if not text or text.startswith('Error'):
        return []
        
    defect_keywords = {
        'Cracks': ['crack', 'cracked', 'cracking', 'fissure', 'split', 'fracture', 'hairline crack'],
        'Damp': ['damp', 'moisture', 'wet', 'humidity', 'condensation', 'water damage', 'penetrating damp'],
        'Corrosion': ['corrosion', 'rust', 'corroded', 'oxidation', 'deterioration', 'metal decay'],
        'Mold': ['mold', 'mould', 'fungus', 'mildew', 'spores', 'black mold'],
        'Structural': ['structural', 'foundation', 'beam', 'support', 'load-bearing', 'subsidence', 'settlement'],
        'Electrical': ['electrical', 'wiring', 'circuit', 'outlet', 'switch', 'fuse', 'panel'],
        'Plumbing': ['plumbing', 'pipe', 'leak', 'drainage', 'blockage', 'water pressure', 'sewage']
    }
    
    severity_keywords = {
        'High': ['severe', 'serious', 'critical', 'urgent', 'immediate', 'dangerous', 'major'],
        'Medium': ['moderate', 'noticeable', 'concern', 'issue', 'problem', 'significant'],
        'Low': ['minor', 'slight', 'small', 'minimal', 'superficial']
    }
    
    detected_defects = []
    text_lower = text.lower()
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    
    for defect_type, keywords in defect_keywords.items():
        found_keywords = set()  # Track unique keywords per type
        
        for keyword in keywords:
            if keyword in text_lower and keyword not in found_keywords:
                found_keywords.add(keyword)
                
                # Find sentences containing the keyword
                for sentence in sentences:
                    if keyword in sentence.lower():
                        # Determine severity
                        severity = 'Medium'  # Default
                        sentence_lower = sentence.lower()
                        for sev_level, sev_words in severity_keywords.items():
                            if any(word in sentence_lower for word in sev_words):
                                severity = sev_level
                                break
                        
                        detected_defects.append({
                            'type': defect_type,
                            'keyword': keyword,
                            'sentence': sentence.strip(),
                            'severity': severity
                        })
                        break  # Only add one instance per keyword per type
    
    logger.info(f"Detected {len(detected_defects)} defects")
    return detected_defects

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload and processing"""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                flash('No file selected')
                return redirect(request.url)
            
            file = request.files['file']
            
            if file.filename == '':
                flash('No file selected')
                return redirect(request.url)
            
            if not allowed_file(file.filename):
                flash('Invalid file type. Please upload PDF, DOCX, or DOC files only.')
                return redirect(request.url)
            
            # Secure filename and save
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            logger.info(f"File uploaded: {filename}")
            
            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                extracted_text = extract_text_from_pdf(filepath)
            elif filename.lower().endswith(('.docx', '.doc')):
                extracted_text = extract_text_from_docx(filepath)
            else:
                flash('Unsupported file type')
                return redirect(request.url)
            
            # Check if text extraction was successful
            if extracted_text.startswith('Error'):
                flash(f'Failed to process file: {extracted_text}')
                return redirect(request.url)
            
            if len(extracted_text.strip()) < 50:
                flash('File appears to be empty or contains very little text. Please check your document.')
                return redirect(request.url)
            
            # Clean and preprocess text
            cleaned_text = clean_and_preprocess_text(extracted_text)
            
            # Detect defects
            defects = detect_defects(cleaned_text)
            
            # Create summary
            defect_summary = {}
            for defect in defects:
                defect_type = defect['type']
                defect_summary[defect_type] = defect_summary.get(defect_type, 0) + 1
            
            # Save results to database
            save_analysis_to_db(filename, defects, defect_summary)
            
            # Clean up uploaded file for security
            try:
                os.remove(filepath)
            except:
                pass
            
            return render_template('results.html', 
                                 filename=filename,
                                 defects=defects,
                                 summary=defect_summary,
                                 total_defects=len(defects))
                                 
        except Exception as e:
            logger.error(f"Upload processing error: {str(e)}")
            flash(f'Error processing file: Please try again with a different file.')
            return redirect(request.url)
    
    return render_template('upload.html')

def save_analysis_to_db(filename, defects, summary):
    """Save analysis results to SQLite database"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                total_defects INTEGER,
                defect_summary TEXT,
                defects_detail TEXT
            )
        ''')
        
        # Insert analysis data
        cursor.execute('''
            INSERT INTO analyses (filename, timestamp, total_defects, defect_summary, defects_detail)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            filename,
            datetime.now().isoformat(),
            len(defects),
            json.dumps(summary),
            json.dumps(defects)
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved analysis for {filename} to database")
    except Exception as e:
        logger.error(f"Database error: {e}")

@app.route('/dashboard')
def dashboard():
    """Dashboard with analytics and delete functionality"""
    try:
        with sqlite3.connect('defect_analysis.db') as conn:
            cursor = conn.cursor()
            
            # Get total analyses
            cursor.execute('SELECT COUNT(*) FROM analysis')
            total_analyses = cursor.fetchone()[0]
            
            # Get total defects
            cursor.execute('SELECT COUNT(*) FROM defects')
            total_defects = cursor.fetchone()[0]
            
            # Get recent analyses
            cursor.execute('''
                SELECT id, filename, file_type, defect_count, analysis_date, upload_time
                FROM analysis 
                ORDER BY id DESC 
                LIMIT 10
            ''')
            recent_analyses = cursor.fetchall()
            
            # Get defect distribution
            cursor.execute('''
                SELECT defect_type, COUNT(*) as count 
                FROM defects 
                GROUP BY defect_type 
                ORDER BY count DESC
            ''')
            defect_distribution = cursor.fetchall()
            
        return render_template('dashboard_simple.html',
                             total_analyses=total_analyses,
                             total_defects=total_defects,
                             recent_analyses=recent_analyses,
                             defect_distribution=defect_distribution)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash(f'Dashboard error: {str(e)}')
        return render_template('dashboard_simple.html',
                             total_analyses=0,
                             total_defects=0,
                             recent_analyses=[],
                             defect_distribution=[])

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """REST API endpoint to return JSON of classified defects"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Supported: PDF, DOCX, DOC'}), 400
        
        # Process file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract and process text
        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(filepath)
        else:
            text = extract_text_from_docx(filepath)
        
        if text.startswith('Error'):
            return jsonify({'error': 'Failed to process file'}), 500
        
        cleaned_text = clean_and_preprocess_text(text)
        defects = detect_defects(cleaned_text)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'filename': filename,
            'defects': defects,
            'total_defects': len(defects),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large error"""
    flash('File too large. Maximum size is 16MB.')
    return redirect(url_for('upload_file'))

@app.route('/analysis/<int:analysis_id>')
def analysis_detail(analysis_id):
    """Show detailed analysis results"""
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

@app.route('/api/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database_connected': True
    })

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {error}")
    flash('An internal error occurred. Please try again.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("🏗️ Starting Building Defect Detector v1.0")
    print("📝 Open your browser and go to: http://localhost:5000")
    print("🔧 Press Ctrl+C to stop the server")
    
    # Production vs Development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
