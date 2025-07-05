#!/usr/bin/env python3
"""
Debug script to check admin user and test login
"""

from database import db
from auth import login_db
from utils import gen_hash, check_hash

def check_admin_user():
    """Check admin user in database"""
    print("🔍 Checking admin user...")
    
    # Get admin user from database
    admin_user = db.get_admin_user()
    
    if admin_user:
        print("✅ Admin user found:")
        print(f"   ID: {admin_user['id']}")
        print(f"   Username: {admin_user['username']}")
        print(f"   Name: {admin_user['name']}")
        print(f"   Email: {admin_user['email']}")
        print(f"   Role: {admin_user['role']}")
        print(f"   Password hash: {admin_user['password'][:20]}...")
        
        # Test password
        test_password = "admin123"
        is_valid = check_hash(admin_user['password'], test_password)
        print(f"   Password 'admin123' valid: {is_valid}")
        
        return admin_user
    else:
        print("❌ Admin user not found")
        return None

def test_login():
    """Test login functionality"""
    print("\n🔍 Testing login...")
    
    # Test with correct credentials
    message, category, status, user = login_db("admin", "admin123")
    print(f"Login result: {status}")
    print(f"Message: {message}")
    
    if user:
        print(f"User: {user.name} ({user.role})")
    else:
        print("No user returned")

def create_admin_if_missing():
    """Create admin user if missing"""
    print("\n🔍 Creating admin user if missing...")
    
    from models import User
    
    # Try to create admin user
    admin_user = User.create(
        name='Admin',
        email='admin@example.com',
        username='admin',
        password='admin123',
        role='admin'
    )
    
    if admin_user:
        print("✅ Admin user created successfully")
        return admin_user
    else:
        print("❌ Failed to create admin user")
        return None

if __name__ == "__main__":
    print("🚀 Debug Admin User")
    print("=" * 30)
    
    # Check existing admin
    admin = check_admin_user()
    
    if not admin:
        # Create admin if missing
        admin = create_admin_if_missing()
    
    # Test login
    test_login() 