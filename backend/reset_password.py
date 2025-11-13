"""
Reset password for omkarmakar07@gmail.com
"""
from auth.models import create_tables, User, get_db, hash_password

def reset_password():
    """Reset password for admin user"""
    create_tables()
    
    db = next(get_db())
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == "omkarmakar07@gmail.com").first()
        
        if not user:
            print("❌ User not found!")
            return
        
        # Set new password
        new_password = "Admin@2024"
        user.hashed_password = hash_password(new_password)
        
        db.commit()
        
        print("✅ Password reset successfully!")
        print(f"\n📧 Email: {user.email}")
        print(f"👤 Username: {user.username}")
        print(f"🔑 New Password: {new_password}")
        print(f"👑 Role: {user.role}")
        print(f"\n⚠️  Please login and change your password immediately!")
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()
