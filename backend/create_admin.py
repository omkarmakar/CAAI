"""
Create initial admin user for CAAI system
"""
from auth.models import create_tables, User, get_db, hash_password, UserRole

def create_admin_user():
    """Create the initial admin user"""
    create_tables()
    
    db = next(get_db())
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "omkarmakar07@gmail.com").first()
        
        if existing_admin:
            print("✅ Admin user already exists!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Username: {existing_admin.username}")
            print(f"   Role: {existing_admin.role}")
            return
        
        # Create admin user
        admin_user = User(
            username="omkarmakar",
            email="omkarmakar07@gmail.com",
            hashed_password=hash_password("admin@2024"),
            full_name="Omkar Makar",
            role=UserRole.ADMIN.value,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"\n📧 Email: omkarmakar07@gmail.com")
        print(f"👤 Username: omkarmakar")
        print(f"🔑 Password: admin@2024")
        print(f"👑 Role: {admin_user.role}")
        print(f"\n⚠️  Please change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
