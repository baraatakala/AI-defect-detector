#!/usr/bin/env python3
"""
Add sample data to the analysis table
"""

import sqlite3
from datetime import datetime, timedelta
import json

def add_sample_data():
    """Add sample analysis data to the database"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        # Sample reports data
        sample_reports = [
            {
                'filename': 'BUILDING_INSPECTION_REPORT.docx',
                'file_type': 'docx',
                'total_defects': 21,
                'upload_time': '2025-08-04 03:24:51',
                'defect_categories': '{"structural": 8, "electrical": 5, "plumbing": 4, "mold": 2, "damp": 2}',
                'ml_confidence_score': 0.92,
                'processing_method': 'hybrid_ml'
            },
            {
                'filename': 'Complex_Building_Defect_Report.docx',
                'file_type': 'docx',
                'total_defects': 17,
                'upload_time': '2025-08-04 03:22:54',
                'defect_categories': '{"structural": 6, "electrical": 4, "mold": 3, "safety": 2, "damp": 2}',
                'ml_confidence_score': 0.88,
                'processing_method': 'hybrid_ml'
            },
            {
                'filename': 'residential_inspection_001.pdf',
                'file_type': 'pdf',
                'total_defects': 3,
                'upload_time': '2025-08-01T07:08:00.311648',
                'defect_categories': '{"electrical": 2, "plumbing": 1}',
                'ml_confidence_score': 0.85,
                'processing_method': 'rule_based'
            },
            {
                'filename': 'office_building_inspection.pdf',
                'file_type': 'pdf',
                'total_defects': 5,
                'upload_time': '2025-07-22T07:08:00.321803',
                'defect_categories': '{"hvac": 2, "electrical": 2, "safety": 1}',
                'ml_confidence_score': 0.79,
                'processing_method': 'hybrid_ml'
            },
            {
                'filename': 'commercial_building_survey.docx',
                'file_type': 'docx',
                'total_defects': 4,
                'upload_time': '2025-07-19T07:08:00.321803',
                'defect_categories': '{"structural": 2, "electrical": 1, "plumbing": 1}',
                'ml_confidence_score': 0.82,
                'processing_method': 'rule_based'
            }
        ]
        
        for report in sample_reports:
            cursor.execute('''
                INSERT INTO analysis (
                    filename, file_type, upload_time, analysis_time, 
                    total_defects, defect_categories, ml_confidence_score, 
                    processing_method, file_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report['filename'],
                report['file_type'],
                report['upload_time'],
                report['upload_time'],  # analysis_time same as upload_time
                report['total_defects'],
                report['defect_categories'],
                report['ml_confidence_score'],
                report['processing_method'],
                f"hash_{report['filename']}"  # simple hash placeholder
            ))
            
            analysis_id = cursor.lastrowid
            
            # Add some sample defects for each report
            defect_types = ['Cracks', 'Damp', 'Electrical', 'Mold', 'Structural', 'Plumbing', 'HVAC', 'Safety']
            severities = ['High', 'Medium', 'Low']
            
            for i in range(min(report['total_defects'], 5)):  # Add up to 5 defects per report
                cursor.execute('''
                    INSERT INTO defects (
                        analysis_id, defect_type, severity, confidence, 
                        sentence, detection_method
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    analysis_id,
                    defect_types[i % len(defect_types)],
                    severities[i % len(severities)],
                    0.8 + (i * 0.05),  # confidence between 0.8-0.95
                    f"Sample defect {i+1} detected in {report['filename']}",
                    report['processing_method']
                ))
        
        conn.commit()
        conn.close()
        
        print("✅ Sample data added successfully!")
        print(f"📊 Added {len(sample_reports)} reports with defects")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")

if __name__ == '__main__':
    add_sample_data()
