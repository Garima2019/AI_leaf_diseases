# backend/database.py
import sqlite3
from datetime import datetime

class AnalysisDatabase:
    def __init__(self, db_path="analysis.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()
    
    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                disease_name TEXT,
                severity TEXT,
                analysis TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def save_analysis(self, filename, disease_name, severity, analysis):
        self.conn.execute("""
            INSERT INTO analyses (filename, disease_name, severity, analysis)
            VALUES (?, ?, ?, ?)
        """, (filename, disease_name, severity, analysis))
        self.conn.commit()
    
    def get_history(self, limit=10):
        cursor = self.conn.execute("""
            SELECT * FROM analyses ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        return cursor.fetchall()