import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = "https://vfznezrsgygvdztmaejj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZmem5lenJzZ3lndmR6dG1hZWpqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2ODc5MDIsImV4cCI6MjA2NzI2MzkwMn0.n-U4sUJUGU1WbNeoaSC-30-nMuHEdw5Vvh8nvLw4pEE"

# Flask Configuration
SECRET_KEY = 'your-secret-key-here'  # Change this in production

# Database table names
USERS_TABLE = "users"
QUIZZES_TABLE = "quizzes"
QUESTIONS_TABLE = "questions"
RESULTS_TABLE = "results" 