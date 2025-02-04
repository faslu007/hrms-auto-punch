import sqlite3
from datetime import datetime, timedelta

class AttendanceHistory:
    def __init__(self, db_path='attendance.db'):
        self.db_path = db_path
        
    def get_history(self, days=7):
        """
        Retrieves attendance history for the specified number of days
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get records for the specified number of days
            cursor.execute('''
                SELECT action_type, timestamp, status, error_message
                FROM attendance_logs
                WHERE timestamp >= datetime('now', ?)
                ORDER BY timestamp DESC
            ''', (f'-{days} days',))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Error retrieving history: {str(e)}")
            return []
            
        finally:
            conn.close()
    
    def get_daily_summary(self, days=7):
        """
        Returns daily summary of work hours
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            summaries = []
            current_date = datetime.now()
            
            for i in range(days):
                date = current_date - timedelta(days=i)
                date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                cursor.execute('''
                    SELECT action_type, timestamp
                    FROM attendance_logs
                    WHERE status = 'success'
                    AND timestamp BETWEEN ? AND ?
                    ORDER BY timestamp ASC
                ''', (date_start, date_end))
                
                actions = cursor.fetchall()
                total_duration = timedelta()
                last_punch_in = None
                
                for action_type, timestamp in actions:
                    timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                    if action_type == 'punch_in':
                        last_punch_in = timestamp
                    elif action_type == 'punch_out' and last_punch_in:
                        duration = timestamp - last_punch_in
                        total_duration += duration
                        last_punch_in = None
                
                # Handle ongoing session
                if last_punch_in and date.date() == current_date.date():
                    total_duration += current_date - last_punch_in
                
                hours = total_duration.total_seconds() / 3600
                summaries.append({
                    'date': date.date(),
                    'hours': round(hours, 2)
                })
            
            return summaries
            
        except Exception as e:
            print(f"Error retrieving daily summary: {str(e)}")
            return []
            
        finally:
            conn.close() 