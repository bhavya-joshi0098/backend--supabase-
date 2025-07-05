#!/usr/bin/env python3
"""
Fix admin user password by updating it with proper hash
"""

from database import db
from utils import gen_hash
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

def fix_admin_password():
    """Fix admin user password"""
    print("🔧 Fixing admin user password...")
    
    try:
        # Create Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Generate proper password hash
        hashed_password = gen_hash('admin123')
        print(f"Generated hash: {hashed_password[:20]}...")
        
        # Update admin user password
        result = supabase.table('users').update({
            'password': hashed_password
        }).eq('username', 'admin').execute()
        
        if result.data:
            print("✅ Admin password updated successfully")
            return True
        else:
            print("❌ Failed to update admin password")
            return False
            
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False

def test_admin_login():
    """Test admin login after fix"""
    print("\n🔍 Testing admin login...")
    
    from auth import login_db
    
    message, category, status, user = login_db("admin", "admin123")
    print(f"Login result: {status}")
    print(f"Message: {message}")
    
    if user:
        print(f"User: {user.name} ({user.role})")
        return True
    else:
        print("Login still failing")
        return False

if __name__ == "__main__":
    print("🚀 Fix Admin Password")
    print("=" * 25)
    
    # Fix password
    if fix_admin_password():
        # Test login
        test_admin_login()
    else:
        print("❌ Could not fix password") 