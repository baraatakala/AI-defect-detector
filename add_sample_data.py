#!/usr/bin/env python3
"""
Add sample data to test the delete functionality
"""

import sqlite3
from datetime import datetime
import os

def add_sample_data():
    """Add sample analysis data to the database"""
    try:
        # Use the database in current directory
        db_path = 'defect_analysis.db'
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Add sample analyses
            sample_analyses = [
                ('sample_building_report.pdf', 'pdf', 3, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ('test_survey_for_delete.txt', 'txt', 5, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ('building_inspection.docx', 'docx', 2, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            ]
            
            for filename, file_type, defect_count, timestamp in sample_analyses:
                cursor.execute('''
                    INSERT INTO analysis (filename, file_type, total_defects, upload_time, analysis_time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (filename, file_type, defect_count, timestamp, timestamp))
                
                analysis_id = cursor.lastrowid
                
                # Add sample defects for each analysis
                sample_defects = [
                    (analysis_id, 'Cracks', 'High', 0.9, 'Visible cracks detected in foundation wall'),
                    (analysis_id, 'Damp', 'Medium', 0.8, 'Moisture stains found in basement area'),
                    (analysis_id, 'Electrical', 'Low', 0.7, 'Outdated wiring system observed'),
                    (analysis_id, 'Mold', 'High', 0.85, 'Black mold growth observed in bathroom'),
                    (analysis_id, 'Structural', 'Medium', 0.75, 'Minor sagging in support beam')
                ]
                
                for defect in sample_defects[:defect_count]:
                    cursor.execute('''
                        INSERT INTO defects (analysis_id, defect_type, severity, confidence, sentence)
                        VALUES (?, ?, ?, ?, ?)
                    ''', defect)
            
            conn.commit()
            print("✅ Sample data added successfully!")
            print("🌐 Now go to http://localhost:5000/dashboard to see the delete buttons!")
            return True
            
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        return False

if __name__ == "__main__":
    add_sample_data()
