from models import User, Quiz, Question, Result, ensure_default_admin, is_admin
from utils import gen_hash, check_hash
from database import db
import secrets
import json
from datetime import datetime

# Ensure default admin exists
ensure_default_admin()

def signup_db(name, email, username, password, role='student'):
    if role == 'admin':
        return "Cannot sign up as admin.", 'danger', False
    if role == 'teacher':
        return "Only admin can create teacher accounts.", 'danger', False
    try:
        # Check if user already exists
        existing_user = User.get_by_username(username)
        if existing_user:
            return "Username or email already in use, try different", 'danger', False
        
        # Check if email already exists
        existing_email = db.get_user_by_email(email) if hasattr(db, 'get_user_by_email') else None
        if existing_email:
            return "Username or email already in use, try different", 'danger', False
        
        user = User.create(name=name, email=email, username=username, password=password, role=role)
        if user:
            message, category, status = "Signup is successful.", 'success', True
            return message, category, status
        else:
            return "Signup failed.", 'danger', False
    except Exception as e:
        message, category, status = f"Signup failed: {str(e)}", 'danger', False
        return message, category, status

def create_teacher_by_admin(name, email, username, password):
    try:
        # Check if user already exists
        existing_user = User.get_by_username(username)
        if existing_user:
            return False, "Username or email already in use."
        
        user = User.create(name=name, email=email, username=username, password=password, role='teacher')
        if user:
            return True, "Teacher created successfully."
        else:
            return False, "Failed to create teacher."
    except Exception as e:
        return False, f"Error creating teacher: {str(e)}"

def login_db(username, password):
    try:
        user = User.get_by_username(username)
        if user and check_hash(user.password, password):
            # Only allow admin login for the admin user
            if user.role == 'admin' and user.username != 'admin':
                return "Invalid admin login.", 'danger', False, None
            message, category, status = "Login is successful.", 'success', True
            return message, category, status, user
        else:
            message, category, status = "Invalid username or password", 'danger', False
            return message, category, status, None
    except Exception as e:
        message, category, status = f"Login failed: {str(e)}", 'danger', False
        return message, category, status, None

def create_quiz_db(teacher_id, title, description, questions_data):
    """Create a new quiz with questions"""
    try:
        # Generate unique link token
        link_token = secrets.token_urlsafe(16)
        
        # Create quiz
        quiz = Quiz.create(
            title=title,
            description=description,
            created_by=teacher_id,
            link_token=link_token
        )
        
        if not quiz:
            return False, None, "Failed to create quiz"
        
        # Create questions
        for question_data in questions_data:
            question = Question.create(
                quiz_id=quiz.id,
                question_text=question_data['question_text'],
                options=question_data['options'],
                correct_answer=question_data['correct_answer']
            )
            if not question:
                return False, None, "Failed to create questions"
        
        return True, quiz, "Quiz created successfully"
    except Exception as e:
        return False, None, str(e)

def get_quiz_by_token(token):
    """Get quiz by link token"""
    try:
        quiz = Quiz.get_by_token(token)
        if quiz:
            questions = Question.get_by_quiz(quiz.id)
            questions_list = []
            for q in questions:
                questions_list.append({
                    'id': q.id,
                    'question_text': q.question_text,
                    'options': q.options,
                    'correct_answer': q.correct_answer
                })
            
            # Get creator name
            creator = User.get_by_id(quiz.created_by)
            creator_name = creator.name if creator else "Unknown"
            
            return {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'created_by': creator_name,
                'questions': questions_list
            }
        return None
    except Exception as e:
        print(f"Error getting quiz by token: {e}")
        return None

def submit_quiz_result(user_id, quiz_id, answers, score, auto_submitted=False):
    """Submit quiz result"""
    try:
        result = Result.create(
            user_id=user_id,
            quiz_id=quiz_id,
            score=score,
            answers=answers,
            auto_submitted=auto_submitted
        )
        if result:
            return True, "Result submitted successfully"
        else:
            return False, "Failed to submit result"
    except Exception as e:
        return False, str(e)

def get_user_results(user_id):
    """Get all results for a user"""
    try:
        results_data = db.get_user_results(user_id)
        result_list = []
        for result_data in results_data:
            result_list.append({
                'id': result_data['id'],
                'quiz_title': result_data.get('quizzes', {}).get('title', 'Unknown Quiz'),
                'score': result_data['score'],
                'completion_time': result_data['completion_time'],
                'answers': json.loads(result_data['answers']) if isinstance(result_data['answers'], str) else result_data['answers'],
                'auto_submitted': result_data.get('auto_submitted', False)
            })
        return result_list
    except Exception as e:
        print(f"Error getting user results: {e}")
        return []

def get_quiz_results(quiz_id):
    """Get all results for a specific quiz (for teachers)"""
    try:
        results_data = db.get_quiz_results(quiz_id)
        result_list = []
        for result_data in results_data:
            result_list.append({
                'id': result_data['id'],
                'user_name': result_data.get('users', {}).get('name', 'Unknown User'),
                'user_email': result_data.get('users', {}).get('email', 'Unknown Email'),
                'score': result_data['score'],
                'completion_time': result_data['completion_time'],
                'auto_submitted': result_data.get('auto_submitted', False)
            })
        return result_list
    except Exception as e:
        print(f"Error getting quiz results: {e}")
        return []

def get_teacher_quizzes(teacher_id):
    """Get all quizzes created by a teacher"""
    try:
        quizzes_data = db.get_quizzes_by_teacher(teacher_id)
        quiz_list = []
        for quiz_data in quizzes_data:
            # Get question count
            questions = Question.get_by_quiz(quiz_data['id'])
            quiz_list.append({
                'id': quiz_data['id'],
                'title': quiz_data['title'],
                'description': quiz_data['description'],
                'created_at': quiz_data['created_at'],
                'link_token': quiz_data['link_token'],
                'question_count': len(questions)
            })
        return quiz_list
    except Exception as e:
        print(f"Error getting teacher quizzes: {e}")
        return []

def get_all_available_quizzes(student_id=None):
    """Get all available quizzes for students"""
    try:
        quizzes_data = db.get_all_quizzes()
        quiz_list = []
        for quiz_data in quizzes_data:
            # Check if student has already taken this quiz
            existing_result = None
            if student_id:
                existing_result = db.check_user_has_taken_quiz(student_id, quiz_data['id'])
            
            # Get creator name
            creator = User.get_by_id(quiz_data['created_by'])
            creator_name = creator.name if creator else "Unknown"
            
            # Get question count
            questions = Question.get_by_quiz(quiz_data['id'])
            
            quiz_list.append({
                'id': quiz_data['id'],
                'title': quiz_data['title'],
                'description': quiz_data['description'],
                'created_by': creator_name,
                'created_at': quiz_data['created_at'],
                'link_token': quiz_data['link_token'],
                'question_count': len(questions),
                'already_taken': existing_result is not None,
                'previous_score': existing_result['score'] if existing_result else None
            })
        return quiz_list
    except Exception as e:
        print(f"Error getting available quizzes: {e}")
        return []