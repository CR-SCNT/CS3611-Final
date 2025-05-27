import sqlite3
import os
import threading
from datetime import datetime

class Logger:
    def __init__(self, db_path='data/logs/streaming_log.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.lock = threading.Lock()
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,                 -- 'server' or 'client'
                    segment_name TEXT,
                    send_time TEXT,
                    bitrate INTEGER,
                    duration_ms INTEGER,
                    client_id TEXT
                ''')
            conn.commit()
        return
    
    def log(self, role, segment_name, send_time, bitrate, duration_ms, client_id):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (role, segment_name, bitrate_kbps, send_time, recv_time, duration_ms, client_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                role,
                segment_name,
                bitrate,
                send_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
                duration_ms,
                client_id
            ))
            conn.commit()
        return
    
    def get_logs(self, role=None, segment_name=None):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM logs WHERE 1=1'
            params = []
            if role:
                query += ' AND role = ?'
                params.append(role)
            if segment_name:
                query += ' AND segment_name = ?'
                params.append(segment_name)
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def export_logs(self, output_path='data/logs/exported_logs.csv'):
        rows = self.get_logs()
        if not rows:
            print("No logs to export.")
            return
        
        with open(output_path, 'w', newline= '') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(['id', 'role', 'segment_name', 'send_time', 'bitrate_kbps', 'duration_ms', 'client_id'])
            writer.writerows(rows)
        print(f"Logs exported to {output_path}")
        return
     
            
    