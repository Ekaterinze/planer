# database.py
import sqlite3
from datetime import date

class DatabaseHelper:
    def __init__(self, db_path="db/planner.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Таблица для заметок на день (дата уникальна)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_notes (
                    date TEXT PRIMARY KEY,
                    note TEXT
                )
            ''')
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

    def get_daily_note(self, date_obj: date) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT note FROM daily_notes WHERE date = ?", (date_obj.isoformat(),))
            row = cursor.fetchone()
            return row[0] if row else ""

    def save_daily_note(self, date_obj: date, note: str):
        if not note.strip():
            self.delete_daily_note(date_obj)
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO daily_notes (date, note) VALUES (?, ?)
                    ON CONFLICT(date) DO UPDATE SET note = excluded.note
                ''', (date_obj.isoformat(), note))
                conn.commit()

    def delete_daily_note(self, date_obj: date):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM daily_notes WHERE date = ?", (date_obj.isoformat(),))
            conn.commit()

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