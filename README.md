# Personal-Study-Assistant 
A context-aware AI-powered study tool that helps learners summarize content, generate quizzes and flashcards, schedule study sessions, and track their academic progress — all in one intelligent system.

## Project Overview 
The Personal Study Assistant is an end-to-end academic productivity system built using the Model Context Protocol (MCP) and LangGraph-style agentic memory design. It leverages Google Gemini 1.5 Flash via the google-generativeai API to provide real-time study assistance through:
- Dynamic text summarization
- Flashcard generation
- Quiz creation (MCQ, T/F, Short Answer)
- Study session scheduling and logging
- Learning progress analysis
- Personalized study recommendations

## Features
- AI Summarizer : Converts large blocks of study text into concise, focused summaries.
- Flashcard Creator : Instantly converts your study notes into spaced repetition-ready Q&A cards.
- Quiz Generator : Builds customizable quizzes with explanations for self-assessment.
- Study Scheduler : Lets users log and schedule study sessions for structured learning.
- Progress Tracker : Analyzes quiz results and study time to provide learning insights.
- Note Manager : Create, store, and access study notes in a clean interface.

## AI & Tech Stack
- LLM API: Google Gemini (1.5 Flash)
- Prompt Engineering: Multi-stage, structured prompts for summarization, flashcards, quizzes, etc.
- LangGraph Memory: Simulates intelligent agent behavior with stateful flow
- Backend: Python, SQLite for persistent storage
- Key Libraries: google-generativeai, sqlite3, json, datetime

## Installation
`git clone https://github.com/rishi7736/Personal-Study-Assistant.git`

`cd Personal-Study-Assistant`

`pip install -r requirements.txt`
