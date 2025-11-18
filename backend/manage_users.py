#!/usr/bin/env python3
"""
Safe User Management Script for CAAI
Usage:
  python manage_users.py create-admin <username> <email> <password>
  python manage_users.py reset-password <username> <new_password>
  python manage_users.py change-role <username> <role>
  python manage_users.py list-users
  python manage_users.py delete-user <username>
"""

import sys
from auth.models import get_db, User, hash_password, UserRole

def create_admin(username: str, email: str, password: str, role: str = "superadmin"):
    """Create a new admin/superadmin user"""
    db = next(get_db())
    
    # Check if user exists
    if db.query(User).filter(User.username == username).first():
        print(f"❌ Error: Username '{username}' already exists")
        return
    
    if db.query(User).filter(User.email == email).first():
        print(f"❌ Error: Email '{email}' already exists")
        return
    
    # Validate role
    valid_roles = [r.value for r in UserRole]
    if role not in valid_roles:
        print(f"❌ Error: Invalid role '{role}'. Valid roles: {', '.join(valid_roles)}")
        return
    
    # Create user
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        full_name=username.title(),
        role=role,
        is_active=True,
        is_verified=True
    )
    
    db.add(user)
    db.commit()
    print(f"✅ User '{username}' created with role '{role}'")

def reset_password(username: str, new_password: str):
    """Reset a user's password"""
    db = next(get_db())
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"❌ Error: User '{username}' not found")
        return
    
    user.hashed_password = hash_password(new_password)
    db.commit()
    print(f"✅ Password reset for user '{username}'")

def change_role(username: str, new_role: str):
    """Change a user's role"""
    db = next(get_db())
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"❌ Error: User '{username}' not found")
        return
    
    # Validate role
    valid_roles = [r.value for r in UserRole]
    if new_role not in valid_roles:
        print(f"❌ Error: Invalid role '{new_role}'. Valid roles: {', '.join(valid_roles)}")
        return
    
    user.role = new_role
    db.commit()
    print(f"✅ Role changed to '{new_role}' for user '{username}'")

def list_users():
    """List all users"""
    db = next(get_db())
    
    users = db.query(User).all()
    if not users:
        print("📋 No users found")
        return
    
    print("\n📋 Users:")
    print("-" * 80)
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<15} {'Active':<8}")
    print("-" * 80)
    
    for user in users:
        active = "✓" if user.is_active else "✗"
        print(f"{user.id:<5} {user.username:<20} {user.email:<30} {user.role:<15} {active:<8}")
    
    print("-" * 80)
    print(f"Total: {len(users)} users\n")

def delete_user(username: str):
    """Delete a user"""
    db = next(get_db())
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"❌ Error: User '{username}' not found")
        return
    
    # Confirm deletion
    confirm = input(f"⚠️  Are you sure you want to delete user '{username}'? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Deletion cancelled")
        return
    
    db.delete(user)
    db.commit()
    print(f"✅ User '{username}' deleted")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "create-admin":
            if len(sys.argv) != 5:
                print("Usage: python manage_users.py create-admin <username> <email> <password>")
                sys.exit(1)
            create_admin(sys.argv[2], sys.argv[3], sys.argv[4])
        
        elif command == "reset-password":
            if len(sys.argv) != 4:
                print("Usage: python manage_users.py reset-password <username> <new_password>")
                sys.exit(1)
            reset_password(sys.argv[2], sys.argv[3])
        
        elif command == "change-role":
            if len(sys.argv) != 4:
                print("Usage: python manage_users.py change-role <username> <role>")
                print("Valid roles: user, ca, senior_ca, admin, superadmin")
                sys.exit(1)
            change_role(sys.argv[2], sys.argv[3])
        
        elif command == "list-users":
            list_users()
        
        elif command == "delete-user":
            if len(sys.argv) != 3:
                print("Usage: python manage_users.py delete-user <username>")
                sys.exit(1)
            delete_user(sys.argv[2])
        
        else:
            print(f"❌ Unknown command: {command}")
            print(__doc__)
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
