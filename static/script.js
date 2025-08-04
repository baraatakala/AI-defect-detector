// Building Defect Detector - Interactive Features

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Building Defect Detector initialized');

    // File upload validation and progress
    const fileInput = document.getElementById('file');
    const uploadForm = document.getElementById('uploadForm');
    const progressBar = document.querySelector('.progress-bar');
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateFile(file);
            }
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const file = fileInput.files[0];
            if (!file) {
                e.preventDefault();
                alert('Please select a file to upload.');
                return false;
            }
            
            showProgress();
        });
    }

    function validateFile(file) {
        const maxSize = 16 * 1024 * 1024; // 16MB
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        
        // Check file size
        if (file.size > maxSize) {
            alert('File size must be less than 16MB');
            fileInput.value = '';
            return false;
        }
        
        // Check file type
        if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().match(/\.(pdf|docx|doc)$/)) {
            alert('Please select a PDF or Word document (DOCX/DOC)');
            fileInput.value = '';
            return false;
        }
        
        // Show file info
        const fileSize = (file.size / 1024 / 1024).toFixed(2);
        console.log(`✅ File selected: ${file.name} (${fileSize}MB)`);
        
        return true;
    }

    function showProgress() {
        if (progressBar) {
            progressBar.style.display = 'block';
            progressText.textContent = 'Uploading and analyzing...';
            
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                
                progressFill.style.width = progress + '%';
                
                if (progress > 30) {
                    progressText.textContent = 'Processing document...';
                }
                if (progress > 60) {
                    progressText.textContent = 'Detecting defects...';
                }
                if (progress > 85) {
                    progressText.textContent = 'Finalizing analysis...';
                    clearInterval(interval);
                }
            }, 200);
        }
    }

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Export functionality for results
    window.exportResults = function(format) {
        const results = document.querySelector('.results-container');
        if (!results) {
            alert('No results to export');
            return;
        }

        if (format === 'json') {
            exportAsJSON();
        } else if (format === 'csv') {
            exportAsCSV();
        }
    };

    function exportAsJSON() {
        try {
            const resultsData = window.analysisResults || {};
            const dataStr = JSON.stringify(resultsData, null, 2);
            downloadFile(dataStr, 'defect-analysis.json', 'application/json');
        } catch (error) {
            console.error('Export error:', error);
            alert('Error exporting results');
        }
    }

    function exportAsCSV() {
        try {
            const defects = window.analysisResults?.defects || [];
            if (defects.length === 0) {
                alert('No defects found to export');
                return;
            }

            let csv = 'Type,Confidence,Severity,Description\\n';
            defects.forEach(defect => {
                csv += `"${defect.type}","${defect.confidence}%","${defect.severity}","${defect.sentence.replace(/"/g, '""')}"\\n`;
            });

            downloadFile(csv, 'defect-analysis.csv', 'text/csv');
        } catch (error) {
            console.error('Export error:', error);
            alert('Error exporting results');
        }
    }

    function downloadFile(content, filename, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }

    // Initialize tooltips
    document.querySelectorAll('[title]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('title');
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 1000;
                pointer-events: none;
            `;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.top - 30) + 'px';
            
            this.addEventListener('mouseleave', function() {
                if (tooltip.parentNode) {
                    tooltip.parentNode.removeChild(tooltip);
                }
            }, { once: true });
        });
    });

    console.log('✅ All interactive features initialized');
});

// Global functions for template access
window.goBack = function() {
    window.history.back();
};

window.printResults = function() {
    window.print();
};
