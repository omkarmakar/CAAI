import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'caai_auth.db'

if not DB_PATH.exists():
    print('Database file not found:', DB_PATH)
    exit(1)

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print('\nUsers:')
try:
    for row in cur.execute('SELECT id, username, email, role, is_active, last_login FROM users ORDER BY id'):
        print(dict(row))
except Exception as e:
    print('Error reading users:', e)

print('\nActive Sessions:')
try:
    for row in cur.execute('SELECT id, user_id, session_token, refresh_token, created_at, expires_at, is_active FROM user_sessions ORDER BY id'):
        print({k: row[k] for k in row.keys() if k!='session_token' and k!='refresh_token'})
except Exception as e:
    print('Error reading sessions:', e)

print('\nRecent Audit Logs:')
try:
    for row in cur.execute('SELECT id, user_id, action, details, status, timestamp FROM audit_logs ORDER BY id DESC LIMIT 50'):
        print(dict(row))
except Exception as e:
    print('Error reading audit logs:', e)

conn.close()
