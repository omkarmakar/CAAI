"""
Update existing user to admin and add admin-only registration
"""
from auth.models import create_tables, User, get_db, hash_password, UserRole

def update_to_admin():
    """Update omkarmakar07@gmail.com to admin"""
    create_tables()
    
    db = next(get_db())
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == "omkarmakar07@gmail.com").first()
        
        if not user:
            print("❌ User not found!")
            return
        
        # Update to admin
        user.role = UserRole.ADMIN.value
        user.is_active = True
        user.is_verified = True
        user.full_name = "Omkar Makar"
        
        db.commit()
        db.refresh(user)
        
        print("✅ User updated to ADMIN successfully!")
        print(f"\n📧 Email: {user.email}")
        print(f"👤 Username: {user.username}")
        print(f"👑 Role: {user.role}")
        print(f"✓ Status: Active & Verified")
        print(f"\n🔐 You can now login and manage other users!")
        
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_to_admin()
