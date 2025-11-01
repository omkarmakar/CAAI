from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import hashlib
import secrets
from enum import Enum

# Database setup
DATABASE_URL = "sqlite:///./caai_auth.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', role='{self.role}')>"
    
    def has_role(self, required_role: UserRole) -> bool:
        """Check if user has the required role or higher privileges"""
        role_hierarchy = {
            UserRole.USER: 0,
            UserRole.ADMIN: 1,
            UserRole.SUPERADMIN: 2
        }
        user_level = role_hierarchy.get(UserRole(self.role), 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level
    
    def can_access_agent(self, agent_name: str) -> bool:
        """Check if user can access specific agent based on role"""
        # Define agent access rules
        agent_access = {
            UserRole.USER: [
                "DocAuditAgent", "BookBotAgent", "InsightBotAgent", 
                "TaxBot", "GSTAgent"
            ],
            UserRole.ADMIN: [
                "DocAuditAgent", "BookBotAgent", "InsightBotAgent", 
                "TaxBot", "GSTAgent", "ClientCommAgent", "ComplianceCheckAgent"
            ],
            UserRole.SUPERADMIN: ["*"]  # Access to all agents
        }
        
        user_role = UserRole(self.role)
        allowed_agents = agent_access.get(user_role, [])
        
        return "*" in allowed_agents or agent_name in allowed_agents

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(128), unique=True, index=True, nullable=False)
    refresh_token = Column(String(128), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(user_id='{self.user_id}', active='{self.is_active}')>"

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="success")  # success, failed, error
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', user_id='{self.user_id}', status='{self.status}')>"

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        salt, stored_hash = hashed_password.split(":", 1)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash == stored_hash
    except ValueError:
        return False

def generate_tokens():
    """Generate session and refresh tokens"""
    session_token = secrets.token_urlsafe(64)
    refresh_token = secrets.token_urlsafe(64)
    return session_token, refresh_token