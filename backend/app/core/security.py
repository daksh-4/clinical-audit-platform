"""
Security utilities for authentication, password hashing, and encryption.
"""
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
import bcrypt
from cryptography.fernet import Fernet

from app.core.config import settings


# Password hashing using bcrypt directly
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    """
    try:
        # Ensure inputs are bytes
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    # Ensure password is bytes
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password meets security requirements.
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not (has_upper and has_lower and has_digit and has_special):
        return False, "Password must contain uppercase, lowercase, digit, and special character"
    
    return True, None


# JWT token handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# PII Encryption using Fernet (symmetric encryption)
class PIIEncryption:
    """
    Handle encryption/decryption of PII fields.
    """
    
    def __init__(self):
        self.cipher = Fernet(settings.FERNET_KEY.encode())
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value.
        """
        if not plaintext:
            return plaintext
        
        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a string value.
        """
        if not ciphertext:
            return ciphertext
        
        decrypted = self.cipher.decrypt(ciphertext.encode())
        return decrypted.decode()
    
    def encrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """
        Encrypt specific fields in a dictionary.
        """
        encrypted_data = data.copy()
        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """
        Decrypt specific fields in a dictionary.
        """
        decrypted_data = data.copy()
        for field in fields:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt(decrypted_data[field])
        return decrypted_data


pii_encryption = PIIEncryption()


# Pseudonymisation
import hashlib


def generate_pseudonym(identifier: str, salt: str) -> str:
    """
    Generate a consistent pseudonym from an identifier.
    
    Args:
        identifier: The original identifier (e.g., NHS number)
        salt: Site or audit-specific salt
    
    Returns:
        SHA-256 hash as hexadecimal string
    """
    combined = f"{identifier}:{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()


# Audit trail utilities
def generate_audit_event(
    user_id: str,
    action: str,
    resource: str,
    resource_id: str,
    success: bool = True,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Generate a standardized audit log entry.
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "resource_id": resource_id,
        "success": success,
        "metadata": metadata or {},
    }
