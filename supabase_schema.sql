-- Quiz Platform Database Schema for Supabase
-- Run this in your Supabase SQL Editor

-- Enable Row Level Security (RLS)
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS results ENABLE ROW LEVEL SECURITY;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'student' CHECK (role IN ('admin', 'teacher', 'student')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_by BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    link_token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create questions table
CREATE TABLE IF NOT EXISTS questions (
    id BIGSERIAL PRIMARY KEY,
    quiz_id BIGINT NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_answer VARCHAR(255) NOT NULL
);

-- Create results table
CREATE TABLE IF NOT EXISTS results (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id BIGINT NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    answers JSONB NOT NULL,
    completion_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    auto_submitted BOOLEAN DEFAULT FALSE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_quizzes_created_by ON quizzes(created_by);
CREATE INDEX IF NOT EXISTS idx_quizzes_link_token ON quizzes(link_token);
CREATE INDEX IF NOT EXISTS idx_questions_quiz_id ON questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_results_user_id ON results(user_id);
CREATE INDEX IF NOT EXISTS idx_results_quiz_id ON results(quiz_id);
CREATE INDEX IF NOT EXISTS idx_results_user_quiz ON results(user_id, quiz_id);

-- Insert default admin user
-- Password will be hashed by the application
INSERT INTO users (name, email, username, password, role) 
VALUES ('Admin', 'admin@example.com', 'admin', 'admin123', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Row Level Security Policies

-- Users table policies
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- For now, allow all operations (you can restrict this later)
CREATE POLICY "Allow all operations on users" ON users
    FOR ALL USING (true);

-- Quizzes table policies
CREATE POLICY "Anyone can view quizzes" ON quizzes
    FOR SELECT USING (true);

CREATE POLICY "Teachers can create quizzes" ON quizzes
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = created_by 
            AND users.role IN ('teacher', 'admin')
        )
    );

CREATE POLICY "Quiz creators can update their quizzes" ON quizzes
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = created_by 
            AND users.role IN ('teacher', 'admin')
        )
    );

CREATE POLICY "Quiz creators and admins can delete quizzes" ON quizzes
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = created_by 
            AND users.role IN ('teacher', 'admin')
        )
    );

-- Questions table policies
CREATE POLICY "Anyone can view questions" ON questions
    FOR SELECT USING (true);

CREATE POLICY "Teachers can create questions" ON questions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM quizzes q
            JOIN users u ON q.created_by = u.id
            WHERE q.id = quiz_id 
            AND u.role IN ('teacher', 'admin')
        )
    );

CREATE POLICY "Teachers can update questions" ON questions
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM quizzes q
            JOIN users u ON q.created_by = u.id
            WHERE q.id = quiz_id 
            AND u.role IN ('teacher', 'admin')
        )
    );

CREATE POLICY "Teachers can delete questions" ON questions
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM quizzes q
            JOIN users u ON q.created_by = u.id
            WHERE q.id = quiz_id 
            AND u.role IN ('teacher', 'admin')
        )
    );

-- Results table policies
CREATE POLICY "Users can view their own results" ON results
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Teachers can view results for their quizzes" ON results
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM quizzes q
            JOIN users u ON q.created_by = u.id
            WHERE q.id = quiz_id 
            AND u.role IN ('teacher', 'admin')
        )
    );

CREATE POLICY "Users can create their own results" ON results
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

-- For now, allow all operations (you can restrict this later)
CREATE POLICY "Allow all operations on results" ON results
    FOR ALL USING (true); 