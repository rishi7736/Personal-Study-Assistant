import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

class Database:
    def __init__(self):
        self.db_file = "study_assistant.db"
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Study sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                duration INTEGER NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                notes TEXT,
                completed INTEGER DEFAULT 0,
                actual_end_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Flashcards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                difficulty TEXT DEFAULT 'normal',
                times_reviewed INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Quizzes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                questions TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Quiz results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                percentage REAL NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    # Study Sessions methods
    def create_study_session(self, subject: str, topic: str, duration: int, 
                           scheduled_time: datetime, notes: str = "") -> bool:
        """Create a new study session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO study_sessions (subject, topic, duration, scheduled_time, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (subject, topic, duration, scheduled_time, notes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating study session: {e}")
            return False
    
    def get_upcoming_sessions(self) -> List[Dict]:
        """Get upcoming study sessions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM study_sessions 
                WHERE scheduled_time >= datetime('now') AND completed = 0
                ORDER BY scheduled_time ASC
            ''')
            
            sessions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return sessions
        except Exception as e:
            print(f"Error fetching upcoming sessions: {e}")
            return []
    
    def get_recent_sessions(self, days: int = 30) -> List[Dict]:
        """Get recent study sessions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            cursor.execute('''
                SELECT *, DATE(scheduled_time) as date FROM study_sessions 
                WHERE scheduled_time >= ? AND completed = 1
                ORDER BY scheduled_time DESC
            ''', (start_date,))
            
            sessions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return sessions
        except Exception as e:
            print(f"Error fetching recent sessions: {e}")
            return []
    
    def complete_study_session(self, session_id: int) -> bool:
        """Mark a study session as completed"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE study_sessions 
                SET completed = 1, actual_end_time = datetime('now')
                WHERE id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error completing study session: {e}")
            return False
    
    def delete_study_session(self, session_id: int) -> bool:
        """Delete a study session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM study_sessions WHERE id = ?', (session_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting study session: {e}")
            return False
    
    def get_study_sessions_count(self) -> int:
        """Get total count of study sessions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM study_sessions WHERE completed = 1')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting sessions count: {e}")
            return 0
    
    # Notes methods
    def create_note(self, title: str, subject: str, content: str) -> bool:
        """Create a new note"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notes (title, subject, content)
                VALUES (?, ?, ?)
            ''', (title, subject, content))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating note: {e}")
            return False
    
    def get_all_notes(self) -> List[Dict]:
        """Get all notes"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM notes ORDER BY created_at DESC')
            notes = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return notes
        except Exception as e:
            print(f"Error fetching notes: {e}")
            return []
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting note: {e}")
            return False
    
    def get_notes_count(self) -> int:
        """Get total count of notes"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM notes')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting notes count: {e}")
            return 0
    
    # Flashcards methods
    def create_flashcard(self, topic: str, question: str, answer: str) -> bool:
        """Create a new flashcard"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO flashcards (topic, question, answer)
                VALUES (?, ?, ?)
            ''', (topic, question, answer))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating flashcard: {e}")
            return False
    
    def get_all_flashcards(self) -> List[Dict]:
        """Get all flashcards"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM flashcards ORDER BY created_at DESC')
            flashcards = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return flashcards
        except Exception as e:
            print(f"Error fetching flashcards: {e}")
            return []
    
    def update_flashcard_performance(self, flashcard_id: int, difficulty: str) -> bool:
        """Update flashcard performance rating"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE flashcards 
                SET difficulty = ?, times_reviewed = times_reviewed + 1, 
                    last_reviewed = datetime('now')
                WHERE id = ?
            ''', (difficulty, flashcard_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating flashcard performance: {e}")
            return False
    
    def delete_flashcard(self, flashcard_id: int) -> bool:
        """Delete a flashcard"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM flashcards WHERE id = ?', (flashcard_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting flashcard: {e}")
            return False
    
    def get_flashcards_count(self) -> int:
        """Get total count of flashcards"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM flashcards')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting flashcards count: {e}")
            return 0
    
    def get_flashcard_performance_stats(self) -> Dict[str, int]:
        """Get flashcard performance statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT difficulty, COUNT(*) as count 
                FROM flashcards 
                GROUP BY difficulty
            ''')
            
            stats = {}
            for row in cursor.fetchall():
                stats[row['difficulty']] = row['count']
            
            conn.close()
            return stats
        except Exception as e:
            print(f"Error getting flashcard stats: {e}")
            return {}
    
    # Quiz methods
    def create_quiz(self, topic: str, difficulty: str, questions: List[Dict]) -> Optional[int]:
        """Create a new quiz"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            questions_json = json.dumps(questions)
            cursor.execute('''
                INSERT INTO quizzes (topic, difficulty, questions)
                VALUES (?, ?, ?)
            ''', (topic, difficulty, questions_json))
            
            quiz_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return quiz_id
        except Exception as e:
            print(f"Error creating quiz: {e}")
            return None
    
    def get_available_quizzes(self) -> List[Dict]:
        """Get all available quizzes"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM quizzes ORDER BY created_at DESC')
            quizzes = []
            
            for row in cursor.fetchall():
                quiz = dict(row)
                quiz['questions'] = json.loads(quiz['questions'])
                quizzes.append(quiz)
            
            conn.close()
            return quizzes
        except Exception as e:
            print(f"Error fetching quizzes: {e}")
            return []
    
    def get_quiz_by_id(self, quiz_id: int) -> Optional[Dict]:
        """Get a quiz by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM quizzes WHERE id = ?', (quiz_id,))
            row = cursor.fetchone()
            
            if row:
                quiz = dict(row)
                quiz['questions'] = json.loads(quiz['questions'])
                conn.close()
                return quiz
            
            conn.close()
            return None
        except Exception as e:
            print(f"Error fetching quiz: {e}")
            return None
    
    def save_quiz_result(self, quiz_id: int, score: int, total_questions: int) -> bool:
        """Save quiz result"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            percentage = (score / total_questions) * 100 if total_questions > 0 else 0
            
            cursor.execute('''
                INSERT INTO quiz_results (quiz_id, score, total_questions, percentage)
                VALUES (?, ?, ?, ?)
            ''', (quiz_id, score, total_questions, percentage))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving quiz result: {e}")
            return False
    
    def get_quiz_history(self) -> List[Dict]:
        """Get quiz history with results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT qr.*, q.topic, q.difficulty 
                FROM quiz_results qr
                JOIN quizzes q ON qr.quiz_id = q.id
                ORDER BY qr.completed_at DESC
            ''')
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            print(f"Error fetching quiz history: {e}")
            return []
    
    def get_quizzes_count(self) -> int:
        """Get total count of quiz attempts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM quiz_results')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting quiz count: {e}")
            return 0