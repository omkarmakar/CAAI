from auth.models import SessionLocal, User, UserSession, AuditLog, get_db
from sqlalchemy.orm import Session


def print_users(db: Session):
    print('\nUsers:')
    users = db.query(User).all()
    for u in users:
        print(f"id={u.id}, username={u.username}, email={u.email}, role={u.role}, active={u.is_active}, last_login={u.last_login}")


def print_sessions(db: Session):
    print('\nActive Sessions:')
    sessions = db.query(UserSession).filter(UserSession.is_active == True).all()
    for s in sessions:
        print(f"id={s.id}, user_id={s.user_id}, created={s.created_at}, expires={s.expires_at}")


def print_audit(db: Session, limit=20):
    print('\nRecent Audit Logs:')
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    for l in logs:
        print(f"id={l.id}, user_id={l.user_id}, action={l.action}, status={l.status}, ts={l.timestamp}, details={l.details}")


if __name__ == '__main__':
    db = next(get_db())
    try:
        print_users(db)
        print_sessions(db)
        print_audit(db, limit=50)
    finally:
        db.close()
