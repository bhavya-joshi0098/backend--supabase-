from database import db
from utils import gen_hash
from datetime import datetime
import json

class User:
    def __init__(self, id, name, email, username, password, role, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.role = role
        self.created_at = created_at
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        user_data = db.get_user_by_username(username)
        if user_data:
            return User(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role'],
                created_at=user_data.get('created_at')
            )
        return None
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        user_data = db.get_user_by_id(user_id)
        if user_data:
            return User(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role'],
                created_at=user_data.get('created_at')
            )
        return None
    
    @staticmethod
    def create(name, email, username, password, role='student'):
        """Create a new user"""
        hashed_password = gen_hash(password)
        user_data = db.create_user(name, email, username, hashed_password, role)
        if user_data:
            return User(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role'],
                created_at=user_data.get('created_at')
            )
        return None

class Quiz:
    def __init__(self, id, title, description, created_by, link_token, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.created_by = created_by
        self.link_token = link_token
        self.created_at = created_at
    
    @staticmethod
    def get_by_token(token):
        """Get quiz by link token"""
        quiz_data = db.get_quiz_by_token(token)
        if quiz_data:
            return Quiz(
                id=quiz_data['id'],
                title=quiz_data['title'],
                description=quiz_data['description'],
                created_by=quiz_data['created_by'],
                link_token=quiz_data['link_token'],
                created_at=quiz_data.get('created_at')
            )
        return None
    
    @staticmethod
    def get_by_id(quiz_id):
        """Get quiz by ID"""
        quiz_data = db.get_quiz_by_id(quiz_id)
        if quiz_data:
            return Quiz(
                id=quiz_data['id'],
                title=quiz_data['title'],
                description=quiz_data['description'],
                created_by=quiz_data['created_by'],
                link_token=quiz_data['link_token'],
                created_at=quiz_data.get('created_at')
            )
        return None
    
    @staticmethod
    def create(title, description, created_by, link_token):
        """Create a new quiz"""
        quiz_data = db.create_quiz(title, description, created_by, link_token)
        if quiz_data:
            return Quiz(
                id=quiz_data['id'],
                title=quiz_data['title'],
                description=quiz_data['description'],
                created_by=quiz_data['created_by'],
                link_token=quiz_data['link_token'],
                created_at=quiz_data.get('created_at')
            )
        return None

class Question:
    def __init__(self, id, quiz_id, question_text, options, correct_answer):
        self.id = id
        self.quiz_id = quiz_id
        self.question_text = question_text
        self.options = options if isinstance(options, list) else json.loads(options)
        self.correct_answer = correct_answer
    
    @staticmethod
    def get_by_quiz(quiz_id):
        """Get all questions for a quiz"""
        questions_data = db.get_questions_by_quiz(quiz_id)
        questions = []
        for q_data in questions_data:
            questions.append(Question(
                id=q_data['id'],
                quiz_id=q_data['quiz_id'],
                question_text=q_data['question_text'],
                options=q_data['options'],
                correct_answer=q_data['correct_answer']
            ))
        return questions
    
    @staticmethod
    def create(quiz_id, question_text, options, correct_answer):
        """Create a new question"""
        question_data = db.create_question(quiz_id, question_text, options, correct_answer)
        if question_data:
            return Question(
                id=question_data['id'],
                quiz_id=question_data['quiz_id'],
                question_text=question_data['question_text'],
                options=question_data['options'],
                correct_answer=question_data['correct_answer']
            )
        return None

class Result:
    def __init__(self, id, user_id, quiz_id, score, answers, completion_time, auto_submitted=False):
        self.id = id
        self.user_id = user_id
        self.quiz_id = quiz_id
        self.score = score
        self.answers = answers if isinstance(answers, dict) else json.loads(answers)
        self.completion_time = completion_time
        self.auto_submitted = auto_submitted
    
    @staticmethod
    def get_or_none(condition):
        """Get result based on condition (simplified for compatibility)"""
        # This is a simplified version for compatibility with existing code
        # In practice, you'd need to parse the condition
        return None
    
    @staticmethod
    def create(user_id, quiz_id, score, answers, auto_submitted=False):
        """Create a new result"""
        result_data = db.create_result(user_id, quiz_id, score, answers, auto_submitted)
        if result_data:
            return Result(
                id=result_data['id'],
                user_id=result_data['user_id'],
                quiz_id=result_data['quiz_id'],
                score=result_data['score'],
                answers=result_data['answers'],
                completion_time=result_data['completion_time'],
                auto_submitted=result_data.get('auto_submitted', False)
            )
        return None

def ensure_default_admin():
    """Ensure default admin user exists"""
    admin_user = db.get_admin_user()
    if not admin_user:
        User.create(
            name='Admin',
            email='admin@example.com',
            username='admin',
            password='admin123',
            role='admin'
        )

def is_admin(user):
    """Check if user is admin"""
    return user and user.role == 'admin' and user.username == 'admin'

# Initialize default admin
ensure_default_admin()
