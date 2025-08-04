from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
import os
import fitz  # PyMuPDF
from docx import Document
import json
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'defect-detector-secret-key-2025'
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
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file_path):
    """Extract text from Word DOCX file using python-docx"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def clean_and_preprocess_text(text):
    """Clean and preprocess text: remove headers, numbers, and blank lines"""
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove empty lines and lines with only numbers/special chars
        line = line.strip()
        if line and not line.isdigit() and len(line) > 3:
            # Skip common headers and footers
            if not any(header in line.lower() for header in ['page', 'report', 'survey', 'date:', 'confidential']):
                cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def detect_defects(text):
    """Detect building defects in text using keyword matching"""
    defect_keywords = {
        'Cracks': ['crack', 'cracked', 'cracking', 'fissure', 'split', 'fracture'],
        'Damp': ['damp', 'moisture', 'wet', 'humidity', 'condensation', 'water damage'],
        'Corrosion': ['corrosion', 'rust', 'corroded', 'oxidation', 'deterioration'],
        'Mold': ['mold', 'mould', 'fungus', 'mildew', 'spores'],
        'Structural': ['structural', 'foundation', 'beam', 'support', 'load-bearing', 'subsidence'],
        'Electrical': ['electrical', 'wiring', 'circuit', 'outlet', 'switch', 'fuse'],
        'Plumbing': ['plumbing', 'pipe', 'leak', 'drainage', 'blockage', 'water pressure']
    }
    
    severity_keywords = {
        'High': ['severe', 'serious', 'critical', 'urgent', 'immediate', 'dangerous'],
        'Medium': ['moderate', 'noticeable', 'concern', 'issue', 'problem'],
        'Low': ['minor', 'slight', 'small', 'minimal']
    }
    
    detected_defects = []
    text_lower = text.lower()
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    
    for defect_type, keywords in defect_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
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
    
    return detected_defects

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload and processing"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
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
                
                # Clean and preprocess text
                cleaned_text = clean_and_preprocess_text(extracted_text)
                
                # Detect defects
                defects = detect_defects(cleaned_text)
                
                # Create summary
                defect_summary = {}
                for defect in defects:
                    defect_type = defect['type']
                    if defect_type in defect_summary:
                        defect_summary[defect_type] += 1
                    else:
                        defect_summary[defect_type] = 1
                
                # Save results to database
                save_analysis_to_db(filename, defects, defect_summary)
                
                # Clean up uploaded file
                os.remove(filepath)
                
                # Prepare data for template
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                return render_template('results_clean.html', 
                                     filename=filename,
                                     defects=defects,
                                     summary=defect_summary,
                                     total_defects=len(defects),
                                     analysis_time=current_time)
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload PDF or DOCX files only.')
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
        print(f"Saved analysis for {filename} to database")
    except Exception as e:
        print(f"Database error: {e}")

@app.route('/dashboard')
def dashboard():
    """Analytics dashboard showing historical data"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analyses ORDER BY timestamp DESC LIMIT 10')
        recent_analyses = cursor.fetchall()
        
        conn.close()
        
        return render_template('dashboard_clean.html', analyses=recent_analyses)
    except Exception as e:
        print(f"Dashboard error: {e}")
        return render_template('dashboard_clean.html', analyses=[])

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """REST API endpoint to return JSON of classified defects"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Process file similar to upload route
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract and process text
        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(filepath)
        else:
            text = extract_text_from_docx(filepath)
        
        cleaned_text = clean_and_preprocess_text(text)
        defects = detect_defects(cleaned_text)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'filename': filename,
            'defects': defects,
            'total_defects': len(defects),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🏗️ Starting Building Defect Detector...")
    print("📝 Open your browser and go to: http://localhost:5000")
    print("🔧 Press Ctrl+C to stop the server")
    app.run(debug=True, port=5000)
