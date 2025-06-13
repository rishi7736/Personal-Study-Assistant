from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd

def format_date(date_string) -> str:
    """Format datetime string for display"""
    try:
        if isinstance(date_string, str):
            # Handle PostgreSQL timestamp format
            if '.' in date_string:
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(date_string)
        elif hasattr(date_string, 'strftime'):
            # Already a datetime object
            dt = date_string
        else:
            return str(date_string)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        return str(date_string)

def calculate_study_streak(sessions: List[Dict]) -> int:
    """Calculate current study streak (consecutive days with study sessions)"""
    if not sessions:
        return 0
    
    try:
        # Convert sessions to dates
        dates = []
        for session in sessions:
            if session.get('completed', False):
                date_str = session.get('date') or session.get('scheduled_time', '')
                if date_str:
                    try:
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        dates.append(dt.date())
                    except:
                        continue
        
        if not dates:
            return 0
        
        # Sort dates and remove duplicates
        unique_dates = sorted(set(dates), reverse=True)
        
        # Calculate streak
        streak = 0
        current_date = datetime.now().date()
        
        for date in unique_dates:
            if date == current_date or date == current_date - timedelta(days=streak):
                streak += 1
                current_date = date
            else:
                break
        
        return streak
    
    except Exception as e:
        print(f"Error calculating study streak: {e}")
        return 0

def get_performance_color(score: float) -> str:
    """Get color based on performance score"""
    if score >= 90:
        return "green"
    elif score >= 70:
        return "orange"
    else:
        return "red"

def calculate_study_stats(sessions: List[Dict]) -> Dict[str, Any]:
    """Calculate comprehensive study statistics"""
    if not sessions:
        return {
            'total_sessions': 0,
            'total_hours': 0,
            'average_session_length': 0,
            'subjects_studied': 0,
            'most_studied_subject': None,
            'weekly_average': 0
        }
    
    try:
        df = pd.DataFrame(sessions)
        
        # Basic stats
        total_sessions = len(df)
        total_minutes = df['duration'].sum() if 'duration' in df.columns else 0
        total_hours = total_minutes / 60
        average_session_length = df['duration'].mean() if 'duration' in df.columns else 0
        
        # Subject analysis
        subjects = df['subject'].unique() if 'subject' in df.columns else []
        subjects_studied = len(subjects)
        
        most_studied_subject = None
        if 'subject' in df.columns:
            subject_counts = df['subject'].value_counts()
            most_studied_subject = subject_counts.index[0] if len(subject_counts) > 0 else None
        
        # Weekly average (assuming last 4 weeks)
        weekly_average = total_hours / 4 if total_hours > 0 else 0
        
        return {
            'total_sessions': total_sessions,
            'total_hours': round(total_hours, 1),
            'average_session_length': round(average_session_length, 1),
            'subjects_studied': subjects_studied,
            'most_studied_subject': most_studied_subject,
            'weekly_average': round(weekly_average, 1)
        }
    
    except Exception as e:
        print(f"Error calculating study stats: {e}")
        return {
            'total_sessions': 0,
            'total_hours': 0,
            'average_session_length': 0,
            'subjects_studied': 0,
            'most_studied_subject': None,
            'weekly_average': 0
        }

def format_duration(minutes: int) -> str:
    """Format duration in minutes to human readable format"""
    if minutes < 60:
        return f"{minutes} min"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hr"
        else:
            return f"{hours} hr {remaining_minutes} min"

def get_study_session_summary(sessions: List[Dict], days: int = 7) -> Dict[str, Any]:
    """Get summary of study sessions for the last N days"""
    if not sessions:
        return {
            'sessions_count': 0,
            'total_time': 0,
            'subjects': [],
            'daily_average': 0
        }
    
    try:
        # Filter sessions from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_sessions = []
        
        for session in sessions:
            session_date = session.get('date') or session.get('scheduled_time', '')
            if session_date:
                try:
                    dt = datetime.fromisoformat(session_date.replace('Z', '+00:00'))
                    if dt >= cutoff_date:
                        recent_sessions.append(session)
                except:
                    continue
        
        if not recent_sessions:
            return {
                'sessions_count': 0,
                'total_time': 0,
                'subjects': [],
                'daily_average': 0
            }
        
        sessions_count = len(recent_sessions)
        total_time = sum(session.get('duration', 0) for session in recent_sessions)
        subjects = list(set(session.get('subject', '') for session in recent_sessions if session.get('subject')))
        daily_average = total_time / days
        
        return {
            'sessions_count': sessions_count,
            'total_time': total_time,
            'subjects': subjects,
            'daily_average': round(daily_average, 1)
        }
    
    except Exception as e:
        print(f"Error getting study session summary: {e}")
        return {
            'sessions_count': 0,
            'total_time': 0,
            'subjects': [],
            'daily_average': 0
        }

def validate_quiz_data(quiz_data: Dict) -> bool:
    """Validate quiz data structure"""
    try:
        if not isinstance(quiz_data, dict):
            return False
        
        questions = quiz_data.get('questions', [])
        if not isinstance(questions, list) or len(questions) == 0:
            return False
        
        for question in questions:
            if not isinstance(question, dict):
                return False
            
            required_fields = ['question', 'type', 'correct_answer']
            if not all(field in question for field in required_fields):
                return False
            
            # Validate question type specific requirements
            question_type = question.get('type')
            if question_type == 'multiple_choice':
                if 'options' not in question or not isinstance(question['options'], list):
                    return False
                if len(question['options']) < 2:
                    return False
            elif question_type == 'true_false':
                if 'options' not in question:
                    question['options'] = ['True', 'False']  # Auto-add if missing
        
        return True
    
    except Exception as e:
        print(f"Error validating quiz data: {e}")
        return False

def get_difficulty_emoji(difficulty: str) -> str:
    """Get emoji representation for difficulty level"""
    difficulty_map = {
        'easy': '😊',
        'medium': '😐',
        'hard': '😓',
        'Easy': '😊',
        'Medium': '😐',
        'Hard': '😓'
    }
    return difficulty_map.get(difficulty, '😐')

def calculate_quiz_performance_trend(quiz_results: List[Dict]) -> Dict[str, Any]:
    """Calculate performance trend from quiz results"""
    if not quiz_results or len(quiz_results) < 2:
        return {
            'trend': 'insufficient_data',
            'trend_percentage': 0,
            'latest_score': 0,
            'average_score': 0
        }
    
    try:
        # Sort by date
        sorted_results = sorted(quiz_results, key=lambda x: x.get('date_taken', ''))
        
        # Calculate percentages
        percentages = []
        for result in sorted_results:
            score = result.get('score', 0)
            total = result.get('total_questions', 1)
            percentage = (score / total) * 100 if total > 0 else 0
            percentages.append(percentage)
        
        latest_score = percentages[-1]
        average_score = sum(percentages) / len(percentages)
        
        # Calculate trend (compare last 3 vs previous 3, or available data)
        mid_point = len(percentages) // 2
        if len(percentages) >= 4:
            recent_avg = sum(percentages[mid_point:]) / len(percentages[mid_point:])
            earlier_avg = sum(percentages[:mid_point]) / len(percentages[:mid_point])
        else:
            recent_avg = percentages[-1]
            earlier_avg = percentages[0]
        
        trend_percentage = recent_avg - earlier_avg
        
        if trend_percentage > 5:
            trend = 'improving'
        elif trend_percentage < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'trend_percentage': round(trend_percentage, 1),
            'latest_score': round(latest_score, 1),
            'average_score': round(average_score, 1)
        }
    
    except Exception as e:
        print(f"Error calculating quiz performance trend: {e}")
        return {
            'trend': 'error',
            'trend_percentage': 0,
            'latest_score': 0,
            'average_score': 0
        }
