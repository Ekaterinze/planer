# database.py
import sqlite3
from datetime import date
from typing import List, Dict

class DatabaseHelper:
    def __init__(self, db_path="db/planner.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 🔹 Таблица занятий/активностей на день
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    name TEXT NOT NULL,
                    start_time TEXT,
                    end_time TEXT,
                    location TEXT,
                    recurrence TEXT,
                    comment TEXT,
                    contacts TEXT,
                    finished INTEGER NOT NULL DEFAULT 0
                )
            ''')
            # формат "HH:MM" или NULL
                  # "none", "daily", "weekly", "monthly"
            # Индекс для быстрого поиска по дате
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date)')

            # Таблица для заметок на месяц (год+месяц уникальны)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_notes (
                    year INTEGER,
                    month INTEGER,
                    note TEXT,
                    PRIMARY KEY (year, month)
                )
            ''')
            conn.commit()

    
    ''' Работа с занятиями '''

    def add_activity(self, date_obj: date, name: str, 
                 start_time: str = None, end_time: str = None,
                 location: str = None, recurrence: str = None,
                 comment: str = None, contacts: str = None) -> int:
        """Создаёт новое занятие. Возвращает его id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO activities (date, name, start_time, end_time, location, recurrence, comment, contacts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date_obj.isoformat(), name, start_time, end_time, location, recurrence, comment, contacts))
            conn.commit()
            return cursor.lastrowid
        

    def get_activities_by_date(self, date_obj: date) -> List[Dict]:
        """Возвращает список всех занятий за указанную дату, отсортированный по времени начала."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # NULL значения сортируются в конце
            cursor.execute('''
                SELECT * FROM activities 
                WHERE date = ? 
                ORDER BY start_time ASC, end_time ASC
            ''', (date_obj.isoformat(),))
            return [dict(row) for row in cursor.fetchall()]

        
    def get_activities_by_range(self, start_date: date, end_date: date) -> List[Dict]:
        """Полезно для отображения календаря: возвращает занятия за период."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM activities 
                WHERE date BETWEEN ? AND ? 
                ORDER BY date, start_time ASC
            ''', (start_date.isoformat(), end_date.isoformat()))
            return [dict(row) for row in cursor.fetchall()]
        

    def update_activity(self, activity_id: int, 
                 date: str = None, name: str = None,
                 start_time: str = None, end_time: str = None,
                 location: str = None, recurrence: str = None,
                 comment: str = None, contacts: str = None) -> int:
        """Обновляет только переданные поля. Игнорирует None."""
        updates = []
        values = []
        fields = [
            ("name", name), ("start_time", start_time), ("end_time", end_time),
            ("location", location), ("recurrence", recurrence),
            ("comment", comment), ("contacts", contacts)
        ]
        for field, val in fields:
            if val is not None:
                updates.append(f"{field} = ?")
                values.append(val)
                
        if not updates:
            return False
            
        values.append(activity_id)
        query = f"UPDATE activities SET {', '.join(updates)} WHERE id = ?"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
        
    def toggle_activity_finished(self, activity_id: int):
        """Переключает статус finished (0->1, 1->0)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE activities 
                SET finished = NOT finished 
                WHERE id = ?
            ''', (activity_id,))
            conn.commit()

    def delete_activity(self, activity_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
            conn.commit()
            return cursor.rowcount > 0
        

    ''' Работа с заметками на месяц '''

    def get_monthly_note(self, year: int, month: int) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT note FROM monthly_notes WHERE year = ? AND month = ?", (year, month))
            row = cursor.fetchone()
            return row[0] if row else ""

    def save_monthly_note(self, year: int, month: int, note: str):
        if not note.strip():  # пустая или состоит из пробелов
            self.delete_month_note(year, month)
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO monthly_notes (year, month, note) VALUES (?, ?, ?)
                    ON CONFLICT(year, month) DO UPDATE SET note = excluded.note
                ''', (year, month, note))
                conn.commit()

    def delete_month_note(self, year: int, month: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM monthly_notes WHERE year = ? AND month = ?", (year, month))
            conn.commit()