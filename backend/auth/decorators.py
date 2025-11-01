from fastapi import Depends, HTTPException, status
from functools import wraps
from .models import User, UserRole
from .jwt_auth import get_current_user

def authenticated_agent_access(agent_name: str):
    """Decorator for agent endpoints that require authentication and specific agent access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check agent access
            if not current_user.can_access_agent(agent_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to agent: {agent_name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def role_required(required_role: UserRole):
    """Decorator for endpoints that require specific role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not current_user.has_role(required_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {required_role.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Common decorators
admin_required = role_required(UserRole.ADMIN)
superadmin_required = role_required(UserRole.SUPERADMIN)