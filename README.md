# Building Defect Detector 🏗️

A professional AI-powered web application that analyzes building survey reports (PDF/DOCX) to automatically detect and classify potential defects.

## 🌟 Features

- **Smart File Processing**: Support for PDF and DOCX building survey reports
- **AI Defect Detection**: Automated detection of 7 defect categories:
  - 🏠 **Structural Issues** (cracks, foundation, beams)
  - 💧 **Moisture & Damp** (water damage, humidity, condensation)
  - ⚡ **Electrical Problems** (wiring, corrosion, circuits)
  - 🔧 **Plumbing Issues** (leaks, blockages, pressure)
  - 🦠 **Mold & Fungus** (growth, spores, mildew)
  - 🔩 **Corrosion & Rust** (metal deterioration, oxidation)
  - 🏗️ **General Structural** (load-bearing, subsidence)
- **Severity Assessment**: Automatic severity classification (High/Medium/Low)
- **Visual Analytics**: Interactive charts and dashboards
- **Data Export**: CSV export functionality
- **Historical Tracking**: Database storage with analysis history
- **REST API**: `/api/predict` endpoint for programmatic access
- **Production Ready**: Logging, error handling, security features

## 🚀 Quick Start

### Development Mode
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app_simple.py

# Open browser
http://localhost:5000
```

### Production Deployment
```bash
# Windows
deploy.bat

# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Start production server
python app_production.py
```

## 📁 Project Structure

```
building-defect-detector/
├── app_simple.py              # Development version
├── app_production.py          # Production version with enhanced features
├── requirements.txt           # Development dependencies
├── requirements_production.txt # Production dependencies
├── deploy.bat / deploy.sh     # Deployment scripts
├── .env.example              # Environment configuration template
├── templates/                # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── results.html
│   └── dashboard.html
├── static/                   # CSS, JS, images
│   ├── style.css
│   └── results.js
├── uploads/                  # Temporary file storage
├── sample_building_survey.txt # Test document
└── README.md
```

## 🎯 Usage

1. **Upload a Document**: 
   - Navigate to the upload page
   - Select a PDF or DOCX building survey report
   - Click "Analyze Report"

2. **View Results**:
   - See detected defects categorized by type
   - Review severity assessments
   - Examine context sentences
   - View interactive pie charts

3. **Export Data**:
   - Download results as CSV
   - Access historical analyses via dashboard

4. **API Usage**:
   ```bash
   curl -X POST -F "file=@survey.pdf" http://localhost:5000/api/predict
   ```

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key
PORT=5000
MAX_CONTENT_LENGTH=16777216
LOG_LEVEL=INFO
```

### File Limits
- **Maximum file size**: 16MB
- **Supported formats**: PDF, DOCX, DOC
- **Text extraction**: PyMuPDF for PDF, python-docx for Word

## 🧪 Testing

```bash
# Run all tests
python test_app.py

# Test with sample data
python test_sample.py

# Health check
curl http://localhost:5000/health
```

## 📊 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main dashboard |
| GET/POST | `/upload` | File upload and processing |
| GET | `/dashboard` | Analytics dashboard |
| POST | `/api/predict` | JSON API for defect detection |
| GET | `/health` | Health check |

### API Response Format
```json
{
  "filename": "survey.pdf",
  "defects": [
    {
      "type": "Cracks",
      "keyword": "crack",
      "sentence": "Foundation shows visible cracks...",
      "severity": "Medium"
    }
  ],
  "total_defects": 5,
  "timestamp": "2025-08-04T10:30:00",
  "status": "success"
}
```

## 🔐 Security Features

- **File Validation**: Strict file type checking
- **Secure Filenames**: Sanitized upload names
- **File Cleanup**: Automatic temporary file removal
- **Input Validation**: Text length and content checks
- **Error Handling**: Comprehensive exception management
- **Logging**: Detailed application logs

## 🚀 Deployment Options

### Local Development
```bash
python app_simple.py
```

### Production Server
```bash
# Using built-in server
python app_production.py

# Using Gunicorn (recommended)
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 app_production:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements_production.txt .
RUN pip install -r requirements_production.txt
COPY . .
EXPOSE 5000
CMD ["python", "app_production.py"]
```

## 📈 Performance & Scalability

- **Text Processing**: Optimized for documents up to 16MB
- **Database**: SQLite for development, easily upgradeable to PostgreSQL
- **Caching**: Ready for Redis integration
- **Load Balancing**: Stateless design for horizontal scaling

## 🤖 AI Enhancement Opportunities

The current system uses rule-based keyword matching. Ready for ML upgrades:

```python
# Future ML integration points:
# 1. Replace keyword matching with BERT/spaCy models
# 2. Add image analysis for embedded photos
# 3. Implement confidence scoring
# 4. Add custom model training interface
```

## 🛠️ Troubleshooting

### Common Issues

**Import Errors**: 
```bash
pip install -r requirements_production.txt
```

**File Upload Issues**: 
- Check file size (max 16MB)
- Verify file format (PDF/DOCX/DOC)
- Ensure uploads/ directory exists

**Database Errors**: 
```bash
python -c "import sqlite3; sqlite3.connect('defect_analysis.db')"
```

## 📝 License

MIT License - Feel free to use and modify for your projects.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Test your changes
4. Submit a pull request

## 📞 Support

- 📧 Issues: Use GitHub Issues
- 📚 Documentation: See inline code comments
- 🔧 Configuration: Check `.env.example`
