from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
from flask_cors import CORS
from functools import wraps
from models import User, Quiz, Question, Result, is_admin
from auth import (
    signup_db, login_db, create_quiz_db,
    get_quiz_by_token, submit_quiz_result,
    get_user_results, get_quiz_results,
    get_teacher_quizzes, get_all_available_quizzes,
    create_teacher_by_admin
)
from database import db
# main.py
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# ADD THESE LINES:
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "https://custom-test-frontend.vercel.app"
])

# ✅ Improved login_required decorator
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

# ✅ Improved role_required decorator
def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                if request.path.startswith("/api/"):
                    return jsonify({"success": False, "message": "Unauthorized"}), 401
                return redirect(url_for("login"))
            user = User.get_by_id(session["user_id"])
            if user.role not in allowed_roles:
                if request.path.startswith("/api/"):
                    return jsonify({"success": False, "message": "Forbidden"}), 403
                flash("Access denied. Insufficient permissions.", "danger")
                return redirect(url_for("dashboard"))
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/")
def index():
    return "Quiz Platform Backend API"

# ---------- Web Routes ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        message, category, status, user = login_db(username, password)
        flash(message=message, category=category)
        if status:
            session["user_id"] = user.id
            session["user_role"] = user.role
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        role = request.form.get("role", "student")
        message, category, status = signup_db(name, email, username, password, role)
        flash(message=message, category=category)
        return redirect(url_for("login" if status else "signup"))
    return render_template("signup.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user = User.get_by_id(session["user_id"])
    if user.role == "teacher":
        quizzes = get_teacher_quizzes(user.id)
        return render_template("teacher_dashboard.html", user=user, quizzes=quizzes)
    elif user.role == "admin":
        # Only admin can access admin dashboard
        if not is_admin(user):
            flash("Access denied. Insufficient permissions.", "danger")
            return redirect(url_for("dashboard"))
        return render_template("admin_dashboard.html", user=user)
    else:
        results = get_user_results(user.id)
        return render_template("student_dashboard.html", user=user, results=results)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))

# ---------- API Routes ----------
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    message, category, status, user = login_db(username, password)
    if status:
        session["user_id"] = user.id
        session["user_role"] = user.role
        return jsonify({
            "success": True,
            "message": message,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        })
    return jsonify({"success": False, "message": message}), 401

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json()
    message, category, status = signup_db(
        data.get("name"),
        data.get("email"),
        data.get("username"),
        data.get("password"),
        data.get("role", "student")
    )
    if status:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

# ---------- Student API Routes ----------
@app.route("/api/student/available-quizzes")
@login_required
def api_student_available_quizzes():
    """Get all available quizzes for students"""
    try:
        quizzes = get_all_available_quizzes(session["user_id"])
        return jsonify({"success": True, "quizzes": quizzes})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/student/results")
@login_required
def api_student_results():
    """Get student's quiz results"""
    try:
        results = get_user_results(session["user_id"])
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/student/quiz/<token>/start")
@login_required
def api_student_start_quiz(token):
    """Start a quiz by token"""
    try:
        quiz_data = get_quiz_by_token(token)
        if not quiz_data:
            return jsonify({"success": False, "message": "Quiz not found"}), 404
        
        # Check if student has already taken this quiz
        existing_result = db.check_user_has_taken_quiz(session["user_id"], quiz_data['id'])
        if existing_result:
            return jsonify({
                "success": False, 
                "message": "You have already taken this quiz",
                "previous_score": existing_result['score']
            }), 400
        
        return jsonify({"success": True, "quiz": quiz_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ---------- Quiz Taking Web Route ----------
@app.route("/quiz/<token>")
@login_required
def take_quiz(token):
    """Web route for taking a quiz"""
    quiz_data = get_quiz_by_token(token)
    if not quiz_data:
        return "Quiz not found", 404
    return render_template("take_quiz.html", quiz=quiz_data, token=token)

# ---------- Teacher/Admin API Routes ----------
@app.route("/api/quiz/create", methods=["POST"])
@login_required
# @role_required(["teacher", "admin"])
def api_create_quiz():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description", "")
    questions = data.get("questions", [])

    success, quiz, message = create_quiz_db(session["user_id"], title, description, questions)

    if success:
        quiz_dict = {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'created_at': quiz.created_at,
            'link_token': quiz.link_token,
            'question_count': len(Question.get_by_quiz(quiz.id))
        }
        return jsonify({"success": True, "message": message, "quiz": quiz_dict})
    return jsonify({"success": False, "message": message}), 400

@app.route("/api/quiz/<token>")
def api_get_quiz(token):
    quiz_data = get_quiz_by_token(token)
    if quiz_data:
        return jsonify({"success": True, "quiz": quiz_data})
    return jsonify({"success": False, "message": "Quiz not found"}), 404

@app.route("/api/quiz/<int:quiz_id>/submit", methods=["POST"])
@login_required
def api_submit_quiz(quiz_id):
    data = request.get_json()
    auto_submitted = data.get("auto_submitted", False)
    success, message = submit_quiz_result(
        session["user_id"], 
        quiz_id, 
        data.get("answers", {}), 
        data.get("score", 0),
        auto_submitted
    )
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

@app.route("/api/results")
@login_required
def api_get_results():
    """Get all results for the current user"""
    try:
        results = get_user_results(session["user_id"])
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/quizzes")
@login_required
@role_required(["teacher", "admin"])
def api_get_quizzes():
    """Get all quizzes for teachers/admins"""
    try:
        quizzes = get_teacher_quizzes(session["user_id"])
        return jsonify({"success": True, "quizzes": quizzes})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/quiz/<int:quiz_id>/results")
@login_required
@role_required(["teacher", "admin"])
def api_quiz_results(quiz_id):
    """Get results for a specific quiz"""
    try:
        results = get_quiz_results(quiz_id)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/user/profile")
@login_required
def api_get_profile():
    """Get current user profile"""
    try:
        user = User.get_by_id(session["user_id"])
        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ---------- Admin API Routes ----------
@app.route('/api/admin/create-teacher', methods=['POST'])
@login_required
def api_admin_create_teacher():
    """Create a new teacher account (admin only)"""
    data = request.get_json()
    success, message = create_teacher_by_admin(
        data.get("name"),
        data.get("email"),
        data.get("username"),
        data.get("password")
    )
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

@app.route('/api/admin/users')
@login_required
@role_required(['admin'])
def api_admin_list_users():
    """Get all users (admin only)"""
    try:
        users_data = db.get_all_users()
        users = []
        for user_data in users_data:
            users.append({
                'id': user_data['id'],
                'name': user_data['name'],
                'email': user_data['email'],
                'username': user_data['username'],
                'role': user_data['role'],
                'created_at': user_data.get('created_at', '')
            })
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
def api_admin_delete_user(user_id):
    """Delete a user (admin only)"""
    try:
        success = db.delete_user(user_id)
        if success:
            return jsonify({"success": True, "message": "User deleted successfully"})
        return jsonify({"success": False, "message": "Failed to delete user"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/admin/quizzes')
@login_required
@role_required(['admin'])
def api_admin_list_quizzes():
    """Get all quizzes (admin only)"""
    try:
        quizzes_data = db.get_all_quizzes()
        quizzes = []
        for quiz_data in quizzes_data:
            creator = User.get_by_id(quiz_data['created_by'])
            questions = Question.get_by_quiz(quiz_data['id'])
            quizzes.append({
                'id': quiz_data['id'],
                'title': quiz_data['title'],
                'description': quiz_data['description'],
                'created_by': creator.name if creator else "Unknown",
                'created_at': quiz_data['created_at'],
                'link_token': quiz_data['link_token'],
                'question_count': len(questions)
            })
        return jsonify({"success": True, "quizzes": quizzes})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/quizzes/<int:quiz_id>', methods=['DELETE'])
@login_required
@role_required(['admin', 'teacher'])
def api_delete_quiz(quiz_id):
    """Delete a quiz"""
    try:
        # Get the quiz to check ownership
        quiz = Quiz.get_by_id(quiz_id)
        if not quiz:
            return jsonify({"success": False, "message": "Quiz not found"}), 404
        
        # Check if user is admin or the quiz creator
        user = User.get_by_id(session["user_id"])
        if user.role != 'admin' and quiz.created_by != user.id:
            return jsonify({"success": False, "message": "You can only delete your own quizzes"}), 403
        
        success = db.delete_quiz(quiz_id)
        if success:
            return jsonify({"success": True, "message": "Quiz deleted successfully"})
        return jsonify({"success": False, "message": "Failed to delete quiz"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ---------- Error Handlers ----------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "message": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"success": False, "message": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)

