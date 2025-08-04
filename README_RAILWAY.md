# AI Building Defect Detector - Railway Deployment

🏗️ **Professional building defect detection system ready for Railway deployment**

## 🚀 Quick Deploy to Railway

1. **Connect Repository to Railway**
2. **Deploy automatically** - Railway will detect the configuration
3. **Your app will be live!** 

## ✨ Features

- 📄 **Document Processing**: PDF, DOCX, TXT file analysis
- 🧠 **AI Detection**: Machine learning-powered defect identification  
- 📊 **Interactive Dashboard**: Real-time analytics and visualizations
- 🗑️ **Data Management**: Full CRUD operations with delete functionality
- 📋 **Export**: CSV export of analysis results
- 🎨 **Professional UI**: Bootstrap 5 responsive design

## 🔧 Railway Configuration

- **Runtime**: Python 3.9+
- **Build Command**: Automatic via requirements.txt
- **Start Command**: `gunicorn app_railway:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
- **Health Check**: `/health` endpoint
- **Environment**: Production-ready with error handling

## 📱 How to Use

1. **Upload Document**: PDF, DOCX, or TXT building inspection report
2. **AI Analysis**: System detects defects automatically
3. **View Results**: Interactive dashboard with charts
4. **Manage Data**: Delete old analyses, export CSV reports

## 🛡️ Production Features

- File validation and security
- Error handling and logging
- Health monitoring
- Optimized for Railway platform
- Zero-downtime deployments

---

**Ready to deploy professional building defect detection!** 🎯
