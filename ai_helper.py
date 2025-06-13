import json
import os
from typing import List, Dict, Any, Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-generativeai not installed. AI features will be disabled.")

class AIHelper:
    def __init__(self):
        self.model = "gemini-1.5-flash"
        self.api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDFTDcxmCt2fudd107fLce-BsifAe8BMRw")
        self.client = None
        
        if not GENAI_AVAILABLE:
            print("Google Generative AI library not available. Please install: pip install google-generativeai")
            return
            
        if self.api_key == "your-api-key-here":
            print("Warning: GEMINI_API_KEY not found in environment variables")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        except Exception as e:
            print(f"Failed to initialize Gemini client: {e}")
            self.client = None
    
    def summarize_text(self, text: str) -> str:
        """Generate a summary of the provided text"""
        if not self.client:
            return "AI summarization not available. Please check your API key and library installation."
        
        try:
            prompt = f"Please provide a concise summary of the following text, highlighting the key points and main ideas:\n\n{text}"
            
            response = self.client.generate_content(prompt)
            
            return response.text
        except Exception as e:
            return f"Failed to summarize text: {str(e)}"
    
    def generate_flashcards(self, content: str, num_cards: int = 5) -> List[Dict[str, str]]:
        """Generate flashcards from study material"""
        if not self.client:
            return [{"question": "AI service not available", "answer": "Please check your API key and library installation."}]
        
        try:
            prompt = f"""
            Based on the following study material, create {num_cards} flashcards.
            Each flashcard should have a clear question and a comprehensive answer.
            Focus on the most important concepts, facts, and relationships.
            
            Study Material:
            {content}
            
            Please respond with a JSON object containing an array of flashcards, where each flashcard has:
            - question: A clear, specific question
            - answer: A comprehensive answer
            
            Format: {{"flashcards": [{{"question": "...", "answer": "..."}}, ...]}}
            """
            
            response = self.client.generate_content(prompt)
            
            # Extract JSON from response text
            response_text = response.text.strip()
            # Find JSON content between curly braces
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                result = json.loads(json_text)
                return result.get('flashcards', [])
            else:
                return [{"question": "Error parsing response", "answer": "Could not extract flashcards from AI response."}]
        
        except Exception as e:
            return [{"question": "Generation failed", "answer": f"Failed to generate flashcards: {str(e)}"}]
    
    def generate_quiz(self, content: str, num_questions: int = 5, difficulty: str = "Medium") -> Dict[str, Any]:
        """Generate a quiz from study material"""
        if not self.client:
            return {
                "questions": [{
                    "question": "AI service not available",
                    "type": "multiple_choice",
                    "options": ["Please check your API key", "Install google-generativeai", "Verify configuration", "Contact support"],
                    "correct_answer": "Please check your API key",
                    "explanation": "AI quiz generation requires proper API setup."
                }]
            }
        
        try:
            prompt = f"""
            Based on the following study material, create a {difficulty.lower()} difficulty quiz with {num_questions} questions.
            Use a mix of question types: multiple choice, true/false, and short answer.
            
            Study Material:
            {content}
            
            Please respond with a JSON object containing:
            - questions: Array of question objects
            
            Each question should have:
            - question: The question text
            - type: "multiple_choice", "true_false", or "short_answer"
            - options: Array of options (for multiple choice only)
            - correct_answer: The correct answer
            - explanation: Brief explanation of why the answer is correct
            
            For multiple choice: provide 4 options (A, B, C, D)
            For true/false: options should be ["True", "False"]
            For short answer: no options needed
            
            Format: {{"questions": [{{"question": "...", "type": "...", "options": [...], "correct_answer": "...", "explanation": "..."}}, ...]}}
            """
            
            response = self.client.generate_content(prompt)
            
            # Extract JSON from response text
            response_text = response.text.strip()
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                result = json.loads(json_text)
                return result
            else:
                return {"questions": [{"question": "Error parsing response", "type": "short_answer", "correct_answer": "Failed", "explanation": "Could not extract quiz from AI response."}]}
        
        except Exception as e:
            return {"questions": [{"question": "Generation failed", "type": "short_answer", "correct_answer": "Error", "explanation": f"Failed to generate quiz: {str(e)}"}]}
    
    def get_study_recommendations(self, subject: str, topic: str, learning_style: str, difficulty_level: str) -> str:
        """Get personalized study recommendations"""
        if not self.client:
            return "AI recommendations not available. Please check your API key and library installation."
        
        try:
            prompt = f"""
            Please provide personalized study recommendations for:
            - Subject: {subject}
            - Topic: {topic}
            - Learning Style: {learning_style}
            - Current Level: {difficulty_level}
            
            Include:
            1. Specific study strategies that work well for {learning_style} learners
            2. Recommended resources (books, websites, videos, etc.)
            3. Practice exercises or activities
            4. Time management suggestions
            5. Assessment methods to track progress
            
            Tailor the recommendations to the {difficulty_level} level and focus on actionable advice.
            """
            
            response = self.client.generate_content(prompt)
            
            return response.text
        
        except Exception as e:
            return f"Failed to get study recommendations: {str(e)}"
    
    def get_study_tips(self) -> str:
        """Get general study tips and strategies"""
        if not self.client:
            return "AI study tips not available. Please check your API key and library installation."
        
        try:
            prompt = """
            Provide a comprehensive set of study tips and strategies that are scientifically proven to be effective. 
            Include tips for:
            1. Memory retention and recall
            2. Focus and concentration
            3. Time management
            4. Note-taking strategies
            5. Test preparation
            6. Dealing with study stress
            7. Creating effective study environments
            
            Make the advice practical and actionable.
            """
            
            response = self.client.generate_content(prompt)
            
            return response.text
        
        except Exception as e:
            return f"Failed to get study tips: {str(e)}"
    
    def analyze_learning_progress(self, quiz_scores: List[float], study_hours: List[float], topics: List[str]) -> str:
        """Analyze learning progress and provide insights"""
        if not self.client:
            return "AI progress analysis not available. Please check your API key and library installation."
        
        try:
            prompt = f"""
            Analyze the following learning data and provide insights:
            
            Quiz Scores (percentages): {quiz_scores}
            Study Hours per Session: {study_hours}
            Topics Studied: {topics}
            
            Please provide:
            1. Overall progress assessment
            2. Strengths and areas for improvement
            3. Specific recommendations for better performance
            4. Study pattern analysis
            5. Suggestions for upcoming study sessions
            
            Be encouraging but honest about areas that need work.
            """
            
            response = self.client.generate_content(prompt)
            
            return response.text
        
        except Exception as e:
            return f"Failed to analyze learning progress: {str(e)}"
    
    def explain_concept(self, concept: str, subject: str, complexity_level: str = "intermediate") -> str:
        """Explain a concept in detail"""
        if not self.client:
            return "AI concept explanation not available. Please check your API key and library installation."
        
        try:
            prompt = f"""
            Please explain the concept of "{concept}" in {subject} at a {complexity_level} level.
            
            Include:
            1. Clear definition
            2. Key components or aspects
            3. Real-world examples or applications
            4. Common misconceptions to avoid
            5. Related concepts or connections
            
            Make the explanation clear, engaging, and appropriate for the specified complexity level.
            """
            
            response = self.client.generate_content(prompt)
            
            return response.text
        
        except Exception as e:
            return f"Failed to explain concept: {str(e)}"
