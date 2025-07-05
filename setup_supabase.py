#!/usr/bin/env python3
"""
Setup script for Supabase migration
This script helps you set up the database and test the connection.
"""

import sys
import os
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

def test_supabase_connection():
    """Test the Supabase connection"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test connection by trying to fetch from users table
        result = supabase.table('users').select('*').limit(1).execute()
        print("✅ Supabase connection successful!")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def create_default_admin():
    """Create the default admin user"""
    try:
        from utils import gen_hash
        from database import db
        
        # Check if admin already exists
        admin_user = db.get_admin_user()
        if admin_user:
            print("✅ Admin user already exists")
            return True
        
        # Create admin user
        admin_data = db.create_user(
            name='Admin',
            email='admin@example.com',
            username='admin',
            password=gen_hash('admin123'),
            role='admin'
        )
        
        if admin_data:
            print("✅ Default admin user created successfully")
            print(f"   Username: admin")
            print(f"   Password: admin123")
            return True
        else:
            print("❌ Failed to create admin user")
            return False
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def check_tables():
    """Check if all required tables exist"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        tables = ['users', 'quizzes', 'questions', 'results']
        missing_tables = []
        
        for table in tables:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' missing: {e}")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n❌ Missing tables: {', '.join(missing_tables)}")
            print("Please run the SQL schema in your Supabase SQL Editor")
            return False
        else:
            print("✅ All required tables exist")
            return True
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Supabase for Quiz Platform")
    print("=" * 50)
    
    # Test connection
    if not test_supabase_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Check tables
    if not check_tables():
        print("\n❌ Please create the database tables first")
        print("Run the SQL in supabase_schema.sql in your Supabase SQL Editor")
        sys.exit(1)
    
    # Create admin user
    if create_default_admin():
        print("\n✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: python main.py")
        print("3. Login with admin/admin123")
    else:
        print("\n❌ Setup failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 