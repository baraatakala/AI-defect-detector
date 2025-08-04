import sqlite3

conn = sqlite3.connect('defect_analysis.db')
cursor = conn.cursor()

print("Tables in database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for table in cursor.fetchall():
    print(f"  - {table[0]}")

print("\nbuilding_surveys table count:")
try:
    cursor.execute("SELECT COUNT(*) FROM building_surveys")
    count = cursor.fetchone()[0]
    print(f"  {count} records")
    
    if count > 0:
        cursor.execute("SELECT id, filename, upload_date, defects_count FROM building_surveys LIMIT 5")
        for row in cursor.fetchall():
            print(f"  - ID:{row[0]} | {row[1]} | {row[2]} | {row[3]} defects")
except Exception as e:
    print(f"  Error: {e}")

print("\nanalysis table count:")
try:
    cursor.execute("SELECT COUNT(*) FROM analysis")
    count = cursor.fetchone()[0]
    print(f"  {count} records")
    
    if count > 0:
        cursor.execute("SELECT id, filename, upload_time, total_defects FROM analysis LIMIT 5")
        for row in cursor.fetchall():
            print(f"  - ID:{row[0]} | {row[1]} | {row[2]} | {row[3]} defects")
except Exception as e:
    print(f"  Error: {e}")

conn.close()
