import sqlite3
import json

def debug_report_view():
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        # Get report details
        cursor.execute('''
            SELECT id, filename, upload_time, file_type, total_defects, defect_categories
            FROM analysis WHERE id = ?
        ''', (1,))
        
        report_data = cursor.fetchone()
        print(f"Report data: {report_data}")
        
        if not report_data:
            print("No report found")
            return
        
        # Get defects for this report
        cursor.execute('''
            SELECT defect_type, severity, confidence, sentence
            FROM defects WHERE analysis_id = ?
            ORDER BY confidence DESC
        ''', (1,))
        
        defects = cursor.fetchall()
        print(f"Defects: {defects}")
        
        # Format defects
        formatted_defects = []
        for defect in defects:
            print(f"Processing defect: {defect}")
            formatted_defects.append({
                'category': defect[0],
                'severity': defect[1],
                'confidence': defect[2],
                'description': defect[3]
            })
        
        print(f"Formatted defects: {formatted_defects}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_report_view()
