#!/usr/bin/env python3
"""
Database initialization script for CAAI authentication system
"""
import os
import sys
from datetime import datetime

# Add parent directory to path so we can import auth modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.models import create_tables, SessionLocal, User, hash_password, UserRole

def init_database():
    """Initialize database with tables"""
    print("Creating database tables...")
    create_tables()
    print("✅ Database tables created successfully!")

def create_superadmin():
    """Create default superadmin user"""
    db = SessionLocal()
    
    try:
        # Check if superadmin already exists
        existing_superadmin = db.query(User).filter(User.role == UserRole.SUPERADMIN.value).first()
        
        if existing_superadmin:
            print(f"⚠️ SuperAdmin user already exists: {existing_superadmin.username}")
            return
        
        # Create superadmin user
        superadmin_user = User(
            username="superadmin",
            email="superadmin@caai.local",
            hashed_password=hash_password("SuperAdmin@123"),
            full_name="Super Administrator",
            role=UserRole.SUPERADMIN.value,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        db.add(superadmin_user)
        db.commit()
        db.refresh(superadmin_user)
        
        print("✅ SuperAdmin user created successfully!")
        print("   Username: superadmin")
        print("   Email: superadmin@caai.local")
        print("   Password: SuperAdmin@123")
        print("   ⚠️ Please change the default password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating superadmin user: {e}")
        db.rollback()
    finally:
        db.close()

def create_demo_users():
    """Create demo users for testing"""
    db = SessionLocal()
    
    try:
        demo_users = [
            {
                "username": "admin",
                "email": "admin@caai.local",
                "password": "Admin@123",
                "full_name": "Administrator",
                "role": UserRole.ADMIN.value
            },
            {
                "username": "user1",
                "email": "user1@caai.local",
                "password": "User@123",
                "full_name": "Test User 1",
                "role": UserRole.USER.value
            },
            {
                "username": "user2",
                "email": "user2@caai.local",
                "password": "User@123",
                "full_name": "Test User 2",
                "role": UserRole.USER.value
            }
        ]
        
        created_count = 0
        for user_data in demo_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if existing_user:
                continue
            
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            
            db.add(user)
            created_count += 1
        
        db.commit()
        
        if created_count > 0:
            print(f"✅ Created {created_count} demo users!")
            print("   Demo users created with password: User@123 (or Admin@123 for admin)")
        else:
            print("ℹ️ Demo users already exist")
            
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("🚀 Initializing CAAI Authentication Database...")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Create superadmin user
    create_superadmin()
    
    # Ask if user wants to create demo users
    create_demo = input("\n📝 Create demo users for testing? (y/N): ").lower().strip()
    if create_demo in ['y', 'yes']:
        create_demo_users()
    
    print("\n" + "=" * 50)
    print("🎉 Database initialization completed!")
    print("\n📋 Summary:")
    print("   • Database tables created")
    print("   • SuperAdmin user created (superadmin/SuperAdmin@123)")
    if create_demo in ['y', 'yes']:
        print("   • Demo users created")
    print("\n⚠️  Security Reminders:")
    print("   • Change default passwords immediately")
    print("   • Set JWT_SECRET_KEY environment variable in production")
    print("   • Enable HTTPS in production")
    print("   • Configure email verification if needed")

if __name__ == "__main__":
    main()