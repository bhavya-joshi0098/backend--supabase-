from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime
import json

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class DatabaseManager:
    def __init__(self):
        self.supabase = supabase
    
    def create_user(self, name, email, username, password, role='student'):
        """Create a new user"""
        try:
            data = {
                'name': name,
                'email': email,
                'username': username,
                'password': password,
                'role': role,
                'created_at': datetime.now().isoformat()
            }
            result = self.supabase.table('users').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            result = self.supabase.table('users').select('*').eq('username', username).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            result = self.supabase.table('users').select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_all_users(self):
        """Get all users"""
        try:
            result = self.supabase.table('users').select('*').execute()
            return result.data
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def delete_user(self, user_id):
        """Delete user by ID"""
        try:
            result = self.supabase.table('users').delete().eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def create_quiz(self, title, description, created_by, link_token):
        """Create a new quiz"""
        try:
            data = {
                'title': title,
                'description': description,
                'created_by': created_by,
                'link_token': link_token,
                'created_at': datetime.now().isoformat()
            }
            result = self.supabase.table('quizzes').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating quiz: {e}")
            return None
    
    def get_quiz_by_token(self, token):
        """Get quiz by link token"""
        try:
            result = self.supabase.table('quizzes').select('*').eq('link_token', token).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting quiz: {e}")
            return None
    
    def get_quiz_by_id(self, quiz_id):
        """Get quiz by ID"""
        try:
            result = self.supabase.table('quizzes').select('*').eq('id', quiz_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting quiz: {e}")
            return None
    
    def get_quizzes_by_teacher(self, teacher_id):
        """Get all quizzes created by a teacher"""
        try:
            result = self.supabase.table('quizzes').select('*').eq('created_by', teacher_id).execute()
            return result.data
        except Exception as e:
            print(f"Error getting teacher quizzes: {e}")
            return []
    
    def get_all_quizzes(self):
        """Get all quizzes"""
        try:
            result = self.supabase.table('quizzes').select('*').execute()
            return result.data
        except Exception as e:
            print(f"Error getting quizzes: {e}")
            return []
    
    def delete_quiz(self, quiz_id):
        """Delete quiz by ID"""
        try:
            # First delete related questions and results
            self.supabase.table('questions').delete().eq('quiz_id', quiz_id).execute()
            self.supabase.table('results').delete().eq('quiz_id', quiz_id).execute()
            # Then delete the quiz
            result = self.supabase.table('quizzes').delete().eq('id', quiz_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting quiz: {e}")
            return False
    
    def create_question(self, quiz_id, question_text, options, correct_answer):
        """Create a new question"""
        try:
            data = {
                'quiz_id': quiz_id,
                'question_text': question_text,
                'options': json.dumps(options),
                'correct_answer': correct_answer
            }
            result = self.supabase.table('questions').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating question: {e}")
            return None
    
    def get_questions_by_quiz(self, quiz_id):
        """Get all questions for a quiz"""
        try:
            result = self.supabase.table('questions').select('*').eq('quiz_id', quiz_id).execute()
            return result.data
        except Exception as e:
            print(f"Error getting questions: {e}")
            return []
    
    def create_result(self, user_id, quiz_id, score, answers, auto_submitted=False):
        """Create a new quiz result"""
        try:
            data = {
                'user_id': user_id,
                'quiz_id': quiz_id,
                'score': score,
                'answers': json.dumps(answers),
                'completion_time': datetime.now().isoformat(),
                'auto_submitted': auto_submitted
            }
            result = self.supabase.table('results').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating result: {e}")
            return None
    
    def get_user_results(self, user_id):
        """Get all results for a user"""
        try:
            result = self.supabase.table('results').select('*, quizzes(title)').eq('user_id', user_id).execute()
            return result.data
        except Exception as e:
            print(f"Error getting user results: {e}")
            return []
    
    def get_quiz_results(self, quiz_id):
        """Get all results for a specific quiz"""
        try:
            result = self.supabase.table('results').select('*, users(name, email)').eq('quiz_id', quiz_id).execute()
            return result.data
        except Exception as e:
            print(f"Error getting quiz results: {e}")
            return []
    
    def check_user_has_taken_quiz(self, user_id, quiz_id):
        """Check if user has already taken a quiz"""
        try:
            result = self.supabase.table('results').select('*').eq('user_id', user_id).eq('quiz_id', quiz_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error checking quiz result: {e}")
            return None
    
    def get_admin_user(self):
        """Get the admin user"""
        try:
            result = self.supabase.table('users').select('*').eq('username', 'admin').eq('role', 'admin').execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting admin user: {e}")
            return None

    def update_user_password(self, user_id, new_hashed_password):
        """Update user's password"""
        try:
            result = self.supabase.table('users').update({'password': new_hashed_password}).eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating user password: {e}")
            return False

# Global database manager instance
db = DatabaseManager() 
