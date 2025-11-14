# Security Best Practices

## Environment Variables

Never commit sensitive information to the repository. Use environment variables for all secrets:

### Required Environment Variables

1. **JWT_SECRET_KEY** - Secret key for JWT token generation
   - Generate a strong random key: `openssl rand -hex 32`
   - Set in production: `export JWT_SECRET_KEY="your-generated-key"`

2. **DATABASE_URL** - Database connection string
   - Development: `sqlite:///./auth.db`
   - Production: Use PostgreSQL or other production database

3. **GOOGLE_API_KEY** - For Gemini AI integration
   - Get from: https://makersuite.google.com/app/apikey

## Files to Keep Private

The following files contain sensitive data and are excluded from Git:

- `backend/auth.db` - User database with hashed passwords
- `backend/*.csv` - May contain financial data
- `backend/.env` - Environment variables with secrets
- `backend/initialize_system.py` - Contains default admin password
- `backend/reset_password.py` - Password reset utility
- `backend/update_admin.py` - Admin modification utility

## Initial Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Update all values in `.env` with your actual credentials

3. Never share or commit the `.env` file

## Password Security

- **Default Admin Password**: The default admin password set during initialization should be changed immediately after first login
- **Minimum Requirements**: 8+ characters
- **Storage**: All passwords are hashed using secure algorithms before storage
- **Never** store passwords in plain text

## Production Deployment

Before deploying to production:

1. ✅ Change `JWT_SECRET_KEY` to a strong random value
2. ✅ Change default admin password
3. ✅ Set `ENVIRONMENT=production`
4. ✅ Set `DEBUG=false`
5. ✅ Use HTTPS for all API communication
6. ✅ Restrict CORS origins to specific domains
7. ✅ Use production-grade database (PostgreSQL/MySQL)
8. ✅ Enable rate limiting
9. ✅ Set up proper logging (without sensitive data)
10. ✅ Regular security audits

## CORS Configuration

In production, update `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Database Backups

- Regular backups of `auth.db` (or production database)
- Store backups securely with encryption
- Test restore procedures regularly

## Audit Logging

- All authentication attempts are logged
- Admin actions are tracked in the audit log
- Review logs regularly for suspicious activity

## Security Updates

- Keep all dependencies updated: `pip install --upgrade -r requirements.txt`
- Monitor security advisories for FastAPI, JWT libraries, and other dependencies
- Apply security patches promptly

## Reporting Security Issues

If you discover a security vulnerability, please email: omkarmakar07@gmail.com

Do NOT create public GitHub issues for security vulnerabilities.
