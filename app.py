import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from database import Database
from ai_helper import AIHelper
from utils import format_date, calculate_study_streak, get_performance_color

# Initialize database and AI helper
@st.cache_resource
def init_database():
    return Database()

@st.cache_resource
def init_ai_helper():
    return AIHelper()

# Page configuration
st.set_page_config(
    page_title="Personal Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

if 'db' not in st.session_state:
    st.session_state.db = init_database()

if 'ai_helper' not in st.session_state:
    st.session_state.ai_helper = init_ai_helper()

# Sidebar navigation
st.sidebar.title("📚 Study Assistant")
st.sidebar.markdown("---")

pages = {
    "Dashboard": "🏠",
    "Study Planning": "📅", 
    "Notes": "📝",
    "Flashcards": "🎯",
    "Quizzes": "❓",
    "Progress": "📊",
    "Resources": "💡"
}

for page, icon in pages.items():
    if st.sidebar.button(f"{icon} {page}", key=f"nav_{page}", use_container_width=True):
        st.session_state.current_page = page
        st.rerun()

# Main content area
def show_dashboard():
    st.title("🏠 Dashboard")
    st.markdown("Welcome to your Personal Study Assistant!")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get stats from database
    db = st.session_state.db
    
    with col1:
        total_sessions = db.get_study_sessions_count()
        st.metric("Study Sessions", total_sessions)
    
    with col2:
        total_notes = db.get_notes_count()
        st.metric("Notes Created", total_notes)
    
    with col3:
        total_flashcards = db.get_flashcards_count()
        st.metric("Flashcards", total_flashcards)
    
    with col4:
        total_quizzes = db.get_quizzes_count()
        st.metric("Quizzes Taken", total_quizzes)
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    # Get recent sessions for chart
    sessions = db.get_recent_sessions(30)
    if sessions:
        df = pd.DataFrame(sessions)
        df['date'] = pd.to_datetime(df['date'])
        
        # Create activity chart
        fig = px.line(df, x='date', y='duration', 
                     title="Daily Study Time (Last 30 Days)",
                     labels={'duration': 'Minutes', 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No study sessions recorded yet. Start your first session!")
    
    # Study streak
    streak = calculate_study_streak(sessions)
    st.metric("Current Study Streak", f"{streak} days")

def show_study_planning():
    st.title("📅 Study Planning")
    
    tab1, tab2 = st.tabs(["Plan Session", "View Schedule"])
    
    with tab1:
        st.subheader("Plan a New Study Session")
        
        with st.form("study_session_form"):
            subject = st.text_input("Subject")
            topic = st.text_input("Topic")
            duration = st.number_input("Duration (minutes)", min_value=5, max_value=480, value=60)
            date = st.date_input("Date", min_value=datetime.now().date(), value=datetime.now().date())
            time = st.time_input("Time", value=datetime.now().replace(second=0, microsecond=0).time())
            notes = st.text_area("Session Notes (optional)")
            
            if st.form_submit_button("Schedule Session"):
                if subject and topic:
                    db = st.session_state.db
                    session_datetime = datetime.combine(date, time)
                    
                    # Validate that the session is in the future
                    if session_datetime <= datetime.now():
                        st.error("Please schedule the session for a future date and time.")
                    else:
                        success = db.create_study_session(
                            subject=subject,
                            topic=topic,
                            duration=duration,
                            scheduled_time=session_datetime,
                            notes=notes
                        )
                        
                        if success:
                            st.success("Study session scheduled successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to schedule session. Please try again.")
                else:
                    st.error("Please fill in all required fields.")
    
    with tab2:
        st.subheader("Your Study Schedule")
        
        db = st.session_state.db
        upcoming_sessions = db.get_upcoming_sessions()
        
        if upcoming_sessions:
            st.write(f"Found {len(upcoming_sessions)} upcoming study sessions:")
            
            for session in upcoming_sessions:
                # Create a more informative title
                session_title = f"{session['subject']} - {session['topic']}"
                session_time = format_date(session['scheduled_time'])
                
                with st.expander(f"📚 {session_title} | ⏰ {session_time}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Subject:** {session['subject']}")
                        st.write(f"**Topic:** {session['topic']}")
                        st.write(f"**Duration:** {session['duration']} minutes")
                    
                    with col2:
                        st.write(f"**Scheduled:** {session_time}")
                        if session.get('notes'):
                            st.write(f"**Notes:** {session['notes']}")
                        else:
                            st.write("**Notes:** No notes added")
                    
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Mark Complete", key=f"complete_{session['id']}"):
                            if db.complete_study_session(session['id']):
                                st.success("Session marked as complete!")
                                st.rerun()
                            else:
                                st.error("Failed to update session")
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{session['id']}"):
                            if db.delete_study_session(session['id']):
                                st.success("Session deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete session")
        else:
            st.info("No upcoming sessions scheduled. Create a new study session above!")
            
            # Show a sample of recent sessions for reference
            recent_sessions = db.get_recent_sessions(7)
            if recent_sessions:
                st.subheader("Recent Completed Sessions")
                for session in recent_sessions[:3]:  # Show only last 3
                    st.write(f"✅ {session['subject']} - {session['topic']} ({format_date(session['scheduled_time'])})")

def show_notes():
    st.title("📝 Notes Management")
    
    tab1, tab2 = st.tabs(["Create Note", "View Notes"])
    
    with tab1:
        st.subheader("Create a New Note")
        
        with st.form("note_form"):
            title = st.text_input("Note Title")
            subject = st.text_input("Subject")
            content = st.text_area("Content", height=200)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Note"):
                    if title and content:
                        db = st.session_state.db
                        success = db.create_note(title, subject, content)
                        
                        if success:
                            st.success("Note saved successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to save note. Please try again.")
                    else:
                        st.error("Please fill in title and content.")
            
            with col2:
                if st.form_submit_button("Generate AI Summary"):
                    if content:
                        try:
                            ai_helper = st.session_state.ai_helper
                            summary = ai_helper.summarize_text(content)
                            st.info(f"AI Summary: {summary}")
                        except Exception as e:
                            st.error(f"AI summary failed: {str(e)}")
                    else:
                        st.error("Please enter content to summarize.")
    
    with tab2:
        st.subheader("Your Notes")
        
        db = st.session_state.db
        notes = db.get_all_notes()
        
        if notes:
            # Search functionality
            search_term = st.text_input("Search notes...")
            
            filtered_notes = notes
            if search_term:
                filtered_notes = [note for note in notes 
                                if search_term.lower() in note['title'].lower() 
                                or search_term.lower() in note['content'].lower()]
            
            for note in filtered_notes:
                with st.expander(f"{note['title']} - {note['subject'] or 'No Subject'}"):
                    st.write(f"**Created:** {format_date(note['created_at'])}")
                    st.write(note['content'])
                    
                    # AI-powered features
                    st.markdown("**AI Features:**")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("📚 Generate Flashcards", key=f"flashcards_{note['id']}"):
                            try:
                                with st.spinner("Creating flashcards..."):
                                    ai_helper = st.session_state.ai_helper
                                    flashcards = ai_helper.generate_flashcards(note['content'], num_cards=5)
                                    
                                    topic = note['subject'] or note['title']
                                    success_count = 0
                                    
                                    for card in flashcards:
                                        if db.create_flashcard(topic, card['question'], card['answer']):
                                            success_count += 1
                                    
                                    st.success(f"Created {success_count} flashcards from this note!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Failed to generate flashcards: {str(e)}")
                    
                    with col2:
                        if st.button("❓ Create Quiz", key=f"quiz_{note['id']}"):
                            try:
                                with st.spinner("Creating quiz..."):
                                    ai_helper = st.session_state.ai_helper
                                    quiz_data = ai_helper.generate_quiz(note['content'], num_questions=5, difficulty="Medium")
                                    
                                    topic = note['subject'] or note['title']
                                    quiz_id = db.create_quiz(topic, "Medium", quiz_data['questions'])
                                    
                                    if quiz_id:
                                        st.success("Quiz created successfully! Go to Quizzes tab to take it.")
                                        st.rerun()
                                    else:
                                        st.error("Failed to save quiz.")
                            except Exception as e:
                                st.error(f"Failed to generate quiz: {str(e)}")
                    
                    with col3:
                        if st.button("✏️ Edit", key=f"edit_note_{note['id']}"):
                            st.info("Edit functionality - modify content above and save as new version.")
                    
                    with col4:
                        if st.button("🗑️ Delete", key=f"delete_note_{note['id']}"):
                            db.delete_note(note['id'])
                            st.success("Note deleted!")
                            st.rerun()
        else:
            st.info("No notes created yet.")

def show_flashcards():
    st.title("🎯 Flashcards")
    
    tab1, tab2, tab3 = st.tabs(["Generate Flashcards", "Study Mode", "Manage Flashcards"])
    
    with tab1:
        st.subheader("Generate AI Flashcards")
        
        # Option 1: From existing notes
        st.markdown("### Option 1: Generate from Saved Notes")
        db = st.session_state.db
        notes = db.get_all_notes()
        
        if notes:
            note_options = {f"{note['title']} - {note['subject'] or 'No Subject'}": note for note in notes}
            selected_note_name = st.selectbox("Select a note to generate flashcards from", 
                                            [""] + list(note_options.keys()))
            
            if selected_note_name:
                selected_note = note_options[selected_note_name]
                num_cards_note = st.number_input("Number of flashcards from note", min_value=1, max_value=20, value=5, key="note_cards")
                
                if st.button("Generate Flashcards from Note"):
                    try:
                        with st.spinner("Generating flashcards from your note..."):
                            ai_helper = st.session_state.ai_helper
                            flashcards = ai_helper.generate_flashcards(selected_note['content'], num_cards_note)
                            
                            topic = selected_note['subject'] or selected_note['title']
                            success_count = 0
                            
                            for card in flashcards:
                                if db.create_flashcard(topic, card['question'], card['answer']):
                                    success_count += 1
                            
                            st.success(f"Generated {success_count} flashcards from '{selected_note['title']}'!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate flashcards: {str(e)}")
        else:
            st.info("No saved notes available. Create some notes first or use the manual option below.")
        
        st.markdown("---")
        
        # Option 2: Manual input
        st.markdown("### Option 2: Generate from Manual Input")
        with st.form("flashcard_generation_form"):
            topic = st.text_input("Topic")
            content = st.text_area("Study Material", height=200, 
                                 help="Paste your study material here for AI to generate flashcards")
            num_cards = st.number_input("Number of flashcards", min_value=1, max_value=20, value=5)
            
            if st.form_submit_button("Generate Flashcards"):
                if topic and content:
                    try:
                        with st.spinner("Generating flashcards..."):
                            ai_helper = st.session_state.ai_helper
                            flashcards = ai_helper.generate_flashcards(content, num_cards)
                            
                            success_count = 0
                            
                            for card in flashcards:
                                if db.create_flashcard(topic, card['question'], card['answer']):
                                    success_count += 1
                            
                            st.success(f"Generated {success_count} flashcards successfully!")
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"Failed to generate flashcards: {str(e)}")
                else:
                    st.error("Please provide both topic and study material.")
    
    with tab2:
        st.subheader("Study Mode")
        
        db = st.session_state.db
        flashcards = db.get_all_flashcards()
        
        if flashcards:
            # Filter by topic
            topics = list(set([card['topic'] for card in flashcards]))
            selected_topic = st.selectbox("Select topic to study", ["All"] + topics)
            
            if selected_topic != "All":
                flashcards = [card for card in flashcards if card['topic'] == selected_topic]
            
            if 'current_card_index' not in st.session_state:
                st.session_state.current_card_index = 0
            
            if 'show_answer' not in st.session_state:
                st.session_state.show_answer = False
            
            if flashcards:
                current_card = flashcards[st.session_state.current_card_index]
                
                st.write(f"Card {st.session_state.current_card_index + 1} of {len(flashcards)}")
                st.write(f"**Topic:** {current_card['topic']}")
                
                # Question
                st.markdown("### Question:")
                st.write(current_card['question'])
                
                # Answer (toggle)
                if st.session_state.show_answer:
                    st.markdown("### Answer:")
                    st.write(current_card['answer'])
                    
                    # Performance tracking
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("😊 Easy", use_container_width=True):
                            db.update_flashcard_performance(current_card['id'], 'easy')
                            st.session_state.show_answer = False
                            st.session_state.current_card_index = (st.session_state.current_card_index + 1) % len(flashcards)
                            st.rerun()
                    
                    with col2:
                        if st.button("😐 Medium", use_container_width=True):
                            db.update_flashcard_performance(current_card['id'], 'medium')
                            st.session_state.show_answer = False
                            st.session_state.current_card_index = (st.session_state.current_card_index + 1) % len(flashcards)
                            st.rerun()
                    
                    with col3:
                        if st.button("😓 Hard", use_container_width=True):
                            db.update_flashcard_performance(current_card['id'], 'hard')
                            st.session_state.show_answer = False
                            st.session_state.current_card_index = (st.session_state.current_card_index + 1) % len(flashcards)
                            st.rerun()
                else:
                    if st.button("Show Answer", use_container_width=True):
                        st.session_state.show_answer = True
                        st.rerun()
                
                # Navigation
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("← Previous", disabled=st.session_state.current_card_index == 0):
                        st.session_state.current_card_index -= 1
                        st.session_state.show_answer = False
                        st.rerun()
                
                with col2:
                    if st.button("Next →", disabled=st.session_state.current_card_index == len(flashcards) - 1):
                        st.session_state.current_card_index += 1
                        st.session_state.show_answer = False
                        st.rerun()
        else:
            st.info("No flashcards available. Generate some flashcards first!")
    
    with tab3:
        st.subheader("Manage Flashcards")
        
        db = st.session_state.db
        flashcards = db.get_all_flashcards()
        
        if flashcards:
            for card in flashcards:
                with st.expander(f"{card['topic']} - {card['question'][:50]}..."):
                    st.write(f"**Question:** {card['question']}")
                    st.write(f"**Answer:** {card['answer']}")
                    st.write(f"**Created:** {format_date(card['created_at'])}")
                    
                    if st.button("Delete", key=f"delete_flashcard_{card['id']}"):
                        db.delete_flashcard(card['id'])
                        st.success("Flashcard deleted!")
                        st.rerun()
        else:
            st.info("No flashcards available.")

def show_quizzes():
    st.title("❓ Quizzes")
    
    tab1, tab2, tab3 = st.tabs(["Generate Quiz", "Take Quiz", "Quiz History"])
    
    with tab1:
        st.subheader("Generate AI Quiz")
        
        # Option 1: From existing notes
        st.markdown("### Option 1: Generate from Saved Notes")
        db = st.session_state.db
        notes = db.get_all_notes()
        
        if notes:
            note_options = {f"{note['title']} - {note['subject'] or 'No Subject'}": note for note in notes}
            selected_note_name = st.selectbox("Select a note to generate quiz from", 
                                            [""] + list(note_options.keys()), key="quiz_note_select")
            
            if selected_note_name:
                selected_note = note_options[selected_note_name]
                col1, col2 = st.columns(2)
                with col1:
                    num_questions_note = st.number_input("Number of questions from note", min_value=1, max_value=15, value=5, key="note_questions")
                with col2:
                    difficulty_note = st.selectbox("Difficulty for note quiz", ["Easy", "Medium", "Hard"], key="note_difficulty")
                
                if st.button("Generate Quiz from Note"):
                    try:
                        with st.spinner("Generating quiz from your note..."):
                            ai_helper = st.session_state.ai_helper
                            quiz_data = ai_helper.generate_quiz(selected_note['content'], num_questions_note, difficulty_note)
                            
                            topic = selected_note['subject'] or selected_note['title']
                            quiz_id = db.create_quiz(topic, difficulty_note, quiz_data['questions'])
                            
                            if quiz_id:
                                st.success(f"Quiz generated from '{selected_note['title']}'! You can take it below.")
                                st.session_state.current_quiz_id = quiz_id
                                st.rerun()
                            else:
                                st.error("Failed to save quiz.")
                    except Exception as e:
                        st.error(f"Failed to generate quiz: {str(e)}")
        else:
            st.info("No saved notes available. Create some notes first or use the manual option below.")
        
        st.markdown("---")
        
        # Option 2: Manual input
        st.markdown("### Option 2: Generate from Manual Input")
        with st.form("quiz_generation_form"):
            topic = st.text_input("Quiz Topic")
            content = st.text_area("Study Material", height=200)
            num_questions = st.number_input("Number of questions", min_value=1, max_value=15, value=5)
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            
            if st.form_submit_button("Generate Quiz"):
                if topic and content:
                    try:
                        with st.spinner("Generating quiz..."):
                            ai_helper = st.session_state.ai_helper
                            quiz_data = ai_helper.generate_quiz(content, num_questions, difficulty)
                            
                            quiz_id = db.create_quiz(topic, difficulty, quiz_data['questions'])
                            
                            if quiz_id:
                                st.success("Quiz generated successfully!")
                                st.session_state.current_quiz_id = quiz_id
                                st.rerun()
                            else:
                                st.error("Failed to save quiz.")
                    
                    except Exception as e:
                        st.error(f"Failed to generate quiz: {str(e)}")
                else:
                    st.error("Please provide both topic and study material.")
    
    with tab2:
        st.subheader("Take Quiz")
        
        db = st.session_state.db
        available_quizzes = db.get_available_quizzes()
        
        if available_quizzes:
            quiz_options = {f"{quiz['topic']} ({quiz['difficulty']})": quiz['id'] 
                          for quiz in available_quizzes}
            
            selected_quiz_name = st.selectbox("Select a quiz", list(quiz_options.keys()))
            selected_quiz_id = quiz_options[selected_quiz_name]
            
            if st.button("Start Quiz"):
                st.session_state.taking_quiz = True
                st.session_state.current_quiz_id = selected_quiz_id
                st.session_state.quiz_answers = {}
                st.session_state.quiz_question_index = 0
                st.rerun()
            
            # Quiz taking interface
            if st.session_state.get('taking_quiz', False):
                quiz = db.get_quiz_by_id(st.session_state.current_quiz_id)
                questions = quiz['questions']  # Already parsed in database_sqlite.py
                
                if st.session_state.quiz_question_index < len(questions):
                    current_q = questions[st.session_state.quiz_question_index]
                    
                    st.write(f"Question {st.session_state.quiz_question_index + 1} of {len(questions)}")
                    st.write(f"**{current_q['question']}**")
                    
                    # Handle different question types
                    if current_q['type'] == 'multiple_choice':
                        answer = st.radio(
                            "Select your answer:",
                            current_q['options'],
                            key=f"q_{st.session_state.quiz_question_index}"
                        )
                        
                        if st.button("Next Question"):
                            st.session_state.quiz_answers[st.session_state.quiz_question_index] = answer
                            st.session_state.quiz_question_index += 1
                            st.rerun()
                    
                    elif current_q['type'] == 'true_false':
                        answer = st.radio(
                            "True or False?",
                            ['True', 'False'],
                            key=f"q_{st.session_state.quiz_question_index}"
                        )
                        
                        if st.button("Next Question"):
                            st.session_state.quiz_answers[st.session_state.quiz_question_index] = answer
                            st.session_state.quiz_question_index += 1
                            st.rerun()
                    
                    else:  # short_answer
                        answer = st.text_input(
                            "Your answer:",
                            key=f"q_{st.session_state.quiz_question_index}"
                        )
                        
                        if st.button("Next Question"):
                            st.session_state.quiz_answers[st.session_state.quiz_question_index] = answer
                            st.session_state.quiz_question_index += 1
                            st.rerun()
                
                else:
                    # Quiz completed - show results
                    st.subheader("Quiz Completed!")
                    
                    score = 0
                    total_questions = len(questions)
                    
                    for i, question in enumerate(questions):
                        user_answer = st.session_state.quiz_answers.get(i, "")
                        correct_answer = question['correct_answer']
                        
                        st.write(f"**Question {i+1}:** {question['question']}")
                        st.write(f"Your answer: {user_answer}")
                        st.write(f"Correct answer: {correct_answer}")
                        
                        if user_answer.lower().strip() == correct_answer.lower().strip():
                            st.success("Correct!")
                            score += 1
                        else:
                            st.error("Incorrect")
                        st.write("---")
                    
                    percentage = (score / total_questions) * 100
                    st.metric("Final Score", f"{score}/{total_questions} ({percentage:.1f}%)")
                    
                    # Save quiz result
                    db.save_quiz_result(st.session_state.current_quiz_id, score, total_questions)
                    
                    if st.button("Take Another Quiz"):
                        st.session_state.taking_quiz = False
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_question_index = 0
                        st.rerun()
        else:
            st.info("No quizzes available. Generate a quiz first!")
    
    with tab3:
        st.subheader("Quiz History")
        
        db = st.session_state.db
        quiz_results = db.get_quiz_history()
        
        if quiz_results:
            df = pd.DataFrame(quiz_results)
            df['percentage'] = (df['score'] / df['total_questions'] * 100).round(1)
            df['date'] = pd.to_datetime(df['completed_at'])
            
            # Performance chart
            fig = px.line(df, x='date', y='percentage', 
                         title="Quiz Performance Over Time",
                         labels={'percentage': 'Score (%)', 'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Results table
            st.dataframe(df[['topic', 'difficulty', 'score', 'total_questions', 'percentage', 'completed_at']])
        else:
            st.info("No quiz history available.")

def show_progress():
    st.title("📊 Progress Analytics")
    
    db = st.session_state.db
    
    # Study time analytics
    st.subheader("Study Time Analytics")
    sessions = db.get_recent_sessions(30)
    
    if sessions:
        df = pd.DataFrame(sessions)
        df['date'] = pd.to_datetime(df['date'])
        
        # Weekly study time
        df['week'] = df['date'].dt.isocalendar().week
        weekly_data = df.groupby('week')['duration'].sum().reset_index()
        fig = px.bar(weekly_data, x='week', y='duration',
                    title="Weekly Study Time",
                    labels={'duration': 'Minutes', 'week': 'Week'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Subject breakdown
        if 'subject' in df.columns:
            subject_data = df.groupby('subject')['duration'].sum().reset_index()
            fig = px.pie(subject_data, values='duration', names='subject',
                        title="Study Time by Subject")
            st.plotly_chart(fig, use_container_width=True)
    
    # Quiz performance
    st.subheader("Quiz Performance")
    quiz_results = db.get_quiz_history()
    
    if quiz_results:
        df_quiz = pd.DataFrame(quiz_results)
        df_quiz['percentage'] = (df_quiz['score'] / df_quiz['total_questions'] * 100).round(1)
        
        avg_score = df_quiz['percentage'].mean()
        st.metric("Average Quiz Score", f"{avg_score:.1f}%")
        
        # Performance by difficulty
        difficulty_performance = df_quiz.groupby('difficulty')['percentage'].mean().reset_index()
        fig = px.bar(difficulty_performance, x='difficulty', y='percentage',
                    title="Average Performance by Difficulty",
                    labels={'percentage': 'Average Score (%)'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Flashcard performance
    st.subheader("Flashcard Performance")
    flashcard_stats = db.get_flashcard_performance_stats()
    
    if flashcard_stats:
        easy_count = flashcard_stats.get('easy', 0)
        medium_count = flashcard_stats.get('medium', 0)
        hard_count = flashcard_stats.get('hard', 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Easy", easy_count, delta_color="normal")
        with col2:
            st.metric("Medium", medium_count, delta_color="normal")  
        with col3:
            st.metric("Hard", hard_count, delta_color="inverse")

def show_resources():
    st.title("💡 AI Study Resources")
    
    tab1, tab2 = st.tabs(["Get Recommendations", "Study Tips"])
    
    with tab1:
        st.subheader("Get AI Study Recommendations")
        
        with st.form("resource_form"):
            subject = st.text_input("Subject")
            topic = st.text_input("Specific Topic")
            learning_style = st.selectbox("Learning Style", 
                                        ["Visual", "Auditory", "Kinesthetic", "Reading/Writing"])
            difficulty_level = st.selectbox("Current Level", 
                                           ["Beginner", "Intermediate", "Advanced"])
            
            if st.form_submit_button("Get Recommendations"):
                if subject and topic:
                    try:
                        with st.spinner("Generating recommendations..."):
                            ai_helper = st.session_state.ai_helper
                            recommendations = ai_helper.get_study_recommendations(
                                subject, topic, learning_style, difficulty_level
                            )
                            
                            st.subheader("Recommendations:")
                            st.write(recommendations)
                    
                    except Exception as e:
                        st.error(f"Failed to get recommendations: {str(e)}")
                else:
                    st.error("Please provide subject and topic.")
    
    with tab2:
        st.subheader("AI Study Tips")
        
        if st.button("Get General Study Tips"):
            try:
                ai_helper = st.session_state.ai_helper
                tips = ai_helper.get_study_tips()
                st.write(tips)
            except Exception as e:
                st.error(f"Failed to get study tips: {str(e)}")
        
        st.markdown("""
        ## Quick Study Tips:
        
        1. **Pomodoro Technique**: Study for 25 minutes, then take a 5-minute break
        2. **Active Recall**: Test yourself instead of just re-reading
        3. **Spaced Repetition**: Review material at increasing intervals
        4. **Mind Maps**: Visualize connections between concepts
        5. **Teach Others**: Explain concepts to solidify understanding
        """)

# Main app logic
def main():
    # Show the selected page
    if st.session_state.current_page == "Dashboard":
        show_dashboard()
    elif st.session_state.current_page == "Study Planning":
        show_study_planning()
    elif st.session_state.current_page == "Notes":
        show_notes()
    elif st.session_state.current_page == "Flashcards":
        show_flashcards()
    elif st.session_state.current_page == "Quizzes":
        show_quizzes()
    elif st.session_state.current_page == "Progress":
        show_progress()
    elif st.session_state.current_page == "Resources":
        show_resources()

if __name__ == "__main__":
    main()
