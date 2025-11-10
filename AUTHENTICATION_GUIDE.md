# Authentication System Guide

## Overview

This application now includes a complete user authentication system with login, registration, and logout functionality.

## Features

- ✅ User registration with email (optional)
- ✅ Secure password hashing using bcrypt
- ✅ Login/logout functionality
- ✅ Session management
- ✅ Protected pages (authentication required)
- ✅ Sidebar hidden on login page
- ✅ Password validation (minimum 6 characters)
- ✅ Duplicate username/email prevention

## How It Works

### Database Model

The `User` model in `app/database/models.py` stores:
- `username` (unique, required)
- `email` (unique, optional)
- `hashed_password` (bcrypt-hashed)
- `is_active` (default: True)
- `is_admin` (default: False)
- Timestamps (created_at, updated_at)

### Authentication Service

`app/services/auth_service.py` provides:
- **Password hashing**: Uses passlib with bcrypt (auto-truncates to 72 bytes)
- **Password verification**: Compares plain password with hashed password
- **User creation**: Creates new users with validation
- **User authentication**: Validates credentials

### Login Flow

1. User visits app → sees login/registration form (sidebar hidden)
2. User enters credentials and clicks "Đăng nhập"
3. System verifies credentials against database
4. On success:
   - User info stored in `st.session_state['user']`
   - Page reloads
   - Sidebar appears with user info and logout button
   - User can access all protected pages

### Registration Flow

1. User clicks "Đăng ký" tab
2. Fills in:
   - Username (required)
   - Email (optional)
   - Password (required, min 6 characters)
   - Confirm password (required)
3. System validates:
   - All required fields filled
   - Password length >= 6 characters
   - Passwords match
   - Username/email not already taken
4. On success:
   - User created in database with hashed password
   - Form switches to login mode
   - User can log in immediately

### Protected Pages

All pages check for authentication:
```python
if 'user' not in st.session_state or not st.session_state['user']:
    st.warning("VUI LÒNG ĐĂNG NHẬP ĐỂ TRUY CẬP TÍNH NĂNG NÀY.")
    st.switch_page("main.py")
    st.stop()
```

### Logout Flow

1. User clicks "Đăng xuất" in sidebar
2. System clears session state:
   - `st.session_state['user'] = None`
   - `st.session_state['student_id'] = None`
   - Other related session data cleared
3. Page reloads to login screen

## Password Security

### Bcrypt Configuration

The system uses passlib's CryptContext with bcrypt:
```python
_pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__truncate_error=True  # Auto-truncate passwords to 72 bytes
)
```

### Password Handling

- Passwords are stripped of whitespace before processing
- Bcrypt has a 72-byte limit; passlib auto-truncates if needed
- Passwords are hashed before storage (never stored in plain text)
- Same truncation applied during verification for consistency

## User Session State

When logged in, `st.session_state['user']` contains:
```python
{
    "id": user.id,
    "username": user.username,
    "email": user.email,
    "is_admin": user.is_admin
}
```

## Testing the System

### Test Registration
1. Go to `http://localhost:8501/`
2. Click "Đăng ký"
3. Enter:
   - Username: `testuser`
   - Email: `test@example.com` (optional)
   - Password: `testpass123`
   - Confirm: `testpass123`
4. Click "Đăng ký"
5. Should see success message and switch to login

### Test Login
1. After registration, login with same credentials
2. Should see main app with sidebar
3. Sidebar shows username and logout button

### Test Protected Pages
1. Try accessing a page without logging in
2. Should redirect to main login page

### Test Logout
1. While logged in, click "Đăng xuất"
2. Should return to login page
3. Session cleared, can't access protected pages

## Troubleshooting

### "Password cannot be longer than 72 bytes" Error
**Fixed**: The system now auto-truncates passwords to 72 bytes using passlib's `bcrypt__truncate_error=True` configuration.

### Can't Access Pages After Login
- Check that `st.session_state['user']` is set
- Verify database connection is working
- Check authentication guard in page files

### Duplicate Username Error
- Usernames must be unique
- Try a different username
- Check database for existing users

### Login Fails with Correct Password
- Password may have extra whitespace
- System now strips whitespace automatically
- Try re-registering if problem persists

## Database Initialization

To initialize the database with the User table:
```bash
python init_db.py
```

This will:
1. Create all database tables (including `users`)
2. Load RIASEC framework
3. Optionally load sample data

## Future Enhancements

Possible improvements:
- Password reset functionality
- Email verification
- Two-factor authentication (2FA)
- Password strength requirements
- Account lockout after failed attempts
- Session timeout
- Remember me functionality
- Social login (Google, Facebook, etc.) using Streamlit's built-in OpenID Connect

For social login implementation, see: https://docs.streamlit.io/develop/concepts/connections/authentication

