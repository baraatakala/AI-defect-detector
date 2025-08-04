from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
import os
import PyMuPDF  # fitz for PDF processing
from docx import Document
import json
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename
import spacy
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
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
        doc = PyMuPDF.open(file_path)
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
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def detect_defects(text):
    """
    Detect building defects in text using keyword matching
    In production, this would use a trained ML model
    """
    defect_keywords = {
        'Cracks': ['crack', 'cracked', 'cracking', 'fissure', 'split'],
        'Damp': ['damp', 'moisture', 'wet', 'humidity', 'condensation'],
        'Corrosion': ['corrosion', 'rust', 'corroded', 'oxidation', 'deterioration'],
        'Mold': ['mold', 'mould', 'fungus', 'mildew', 'spores'],
        'Structural': ['structural', 'foundation', 'beam', 'support', 'load-bearing'],
        'Electrical': ['electrical', 'wiring', 'circuit', 'outlet', 'switch'],
        'Plumbing': ['plumbing', 'pipe', 'leak', 'water damage', 'drainage']
    }
    
    detected_defects = []
    text_lower = text.lower()
    
    for defect_type, keywords in defect_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Find sentences containing the keyword
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        detected_defects.append({
                            'type': defect_type,
                            'keyword': keyword,
                            'sentence': sentence.strip(),
                            'severity': 'Medium'  # Default severity
                        })
                        break  # Only add one instance per keyword
    
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
            
            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                extracted_text = extract_text_from_pdf(filepath)
            elif filename.lower().endswith(('.docx', '.doc')):
                extracted_text = extract_text_from_docx(filepath)
            else:
                flash('Unsupported file type')
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
            
            # Save results to database (optional)
            save_analysis_to_db(filename, defects, defect_summary)
            
            return render_template('results.html', 
                                 filename=filename,
                                 defects=defects,
                                 summary=defect_summary,
                                 total_defects=len(defects))
        else:
            flash('Invalid file type. Please upload PDF or DOCX files only.')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """REST API endpoint to return JSON of classified defects"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
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
        
        return render_template('dashboard.html', analyses=recent_analyses)
    except Exception as e:
        return render_template('dashboard.html', analyses=[])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
