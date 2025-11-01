import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .models import User, UserSession, AuditLog, get_db, UserRole
import secrets
import os

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()

class JWTManager:
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

class AuthMiddleware:
    def __init__(self):
        self.jwt_manager = JWTManager()
    
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """Get current authenticated user"""
        token = credentials.credentials
        payload = self.jwt_manager.verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    async def get_current_active_user(
        self,
        current_user: User = Depends(lambda: AuthMiddleware().get_current_user)
    ) -> User:
        """Get current active user"""
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user
    
    def require_role(self, required_role: UserRole):
        """Dependency to require specific role"""
        def role_checker(current_user: User = Depends(lambda: AuthMiddleware().get_current_user)) -> User:
            if not current_user.has_role(required_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {required_role.value}"
                )
            return current_user
        return role_checker
    
    def require_agent_access(self, agent_name: str):
        """Dependency to require agent access"""
        def agent_access_checker(current_user: User = Depends(lambda: AuthMiddleware().get_current_user)) -> User:
            if not current_user.can_access_agent(agent_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to agent: {agent_name}"
                )
            return current_user
        return agent_access_checker

# Initialize auth middleware
auth_middleware = AuthMiddleware()

# Common dependencies
get_current_user = auth_middleware.get_current_user
get_current_active_user = auth_middleware.get_current_active_user
require_admin = auth_middleware.require_role(UserRole.ADMIN)
require_superadmin = auth_middleware.require_role(UserRole.SUPERADMIN)

class AuditLogger:
    @staticmethod
    def log_action(
        db: Session,
        user_id: Optional[int],
        action: str,
        resource: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success"
    ):
        """Log user action to audit log"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )
        db.add(audit_log)
        db.commit()
    
    @staticmethod
    def log_authentication(
        db: Session,
        user_id: Optional[int],
        action: str,
        request: Request,
        status: str = "success",
        details: Optional[str] = None
    ):
        """Log authentication-related actions"""
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        AuditLogger.log_action(
            db=db,
            user_id=user_id,
            action=action,
            resource="authentication",
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )