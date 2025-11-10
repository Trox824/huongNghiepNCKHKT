"""
Authentication and user management service
"""
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import User
from app.services.logger import logger


class AuthService:
    """Service for handling user authentication, registration, and password management."""

    def __init__(self, db: Session):
        self.db = db

    # =====================
    # PASSWORD UTILITIES
    # =====================

    @staticmethod
    def prepare_password(password: str) -> str:
        """Prepare a password for storage (strip whitespace)."""
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Strip any whitespace
        return password.strip()

    @staticmethod
    def verify_password(plain_password: str, stored_password: str) -> bool:
        """Verify a plaintext password against the stored version."""
        # Strip any whitespace
        plain_password = plain_password.strip()
        
        return plain_password == stored_password

    # =====================
    # USER OPERATIONS
    # =====================

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Fetch a user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email."""
        if not email:
            return None
        return self.db.query(User).filter(User.email == email).first()

    def create_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        is_admin: bool = False,
    ) -> User:
        """Create a new user with plain password."""
        prepared_password = self.prepare_password(password)
        user = User(
            username=username.strip(),
            email=email.strip() if email else None,
            password=prepared_password,
            is_admin=is_admin,
        )
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            logger.warning("Failed to create user %s: %s", username, exc)
            raise ValueError("Tên đăng nhập hoặc email đã tồn tại") from exc

        self.db.refresh(user)
        logger.info("Created user: %s", username)
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        user = self.get_user_by_username(username.strip())
        if not user:
            return None
        if not user.is_active:
            logger.warning("Inactive user attempted login: %s", username)
            return None
        if not self.verify_password(password, user.password):
            return None
        return user


