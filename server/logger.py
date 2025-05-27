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
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT,                 -- 'server' or 'client'
                        segment_name TEXT,
                        send_time TEXT,
                        bitrate INTEGER,
                        client_addr TEXT)
                    ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"[Logger] Error initializing database: {e}")
        except Exception as e:
            print(f"[Logger] Unexpected error during database initialization: {e}")

    
    def log(self, role, segment_name, send_time, bitrate, client_addr):
        try:
            with self.lock, sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO logs (role, segment_name, bitrate, send_time, client_addr)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    role,
                    segment_name,
                    bitrate,
                    send_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
                    client_addr
                ))
                conn.commit()
        except sqlite3.Error as e:
            print(f"[Logger] Error logging data: {e}")
        except Exception as e:
            print(f"[Logger] Unexpected error while logging: {e}")
    
    def get_logs(self, role=None, segment_name=None):
        try:
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
        except sqlite3.Error as e:
            print(f"[Logger] Error retrieving logs: {e}")
            return []
        except Exception as e:
            print(f"[Logger] Unexpected error while retrieving logs: {e}")
            return []
    
    def export_logs(self, output_path='data/logs/exported_logs.csv'):
        try:
            rows = self.get_logs()
            if not rows:
                print("[Logger] No logs to export.")
                return
            
            with open(output_path, 'w', newline= '') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(['id', 'role', 'segment_name', 'send_time', 'bitrate', 'client_addr'])
                writer.writerows(rows)
            print(f"[Logger] Logs exported to {output_path}")
        except (sqlite3.Error, IOError) as e:
            print(f"[Logger] Error exporting logs: {e}")
        except Exception as e:
            print(f"[Logger] Unexpected error during log export: {e}")
     
            
    