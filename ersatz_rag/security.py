"""
Security module for ERSATZ RAG
Implements authentication, authorization, and security best practices
"""

import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import json


# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authentication
security = HTTPBearer()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
security_logger.addHandler(handler)


class User(BaseModel):
    """User model for authentication"""
    username: str
    role: str = "user"  # user, admin, service
    is_active: bool = True


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid")
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")


def get_current_user(token_data: TokenData = Depends(verify_token)):
    """Get current authenticated user"""
    # In a real implementation, this would fetch user from database
    # For now, return a mock user
    return User(username=token_data.username or "anonymous", role="user")


def authenticate_user(username: str, password: str):
    """Authenticate user credentials"""
    # This is a simplified implementation
    # In production, verify against database/user store
    if username == "admin" and password == "admin":
        return User(username=username, role="admin")
    elif username == "service" and password == "service":
        return User(username=username, role="service")
    return False


class SecureDocumentRequest(BaseModel):
    """Secure document processing request with validation"""
    document_path: str
    qa_suite: list

    @validator('document_path')
    def validate_document_path(cls, v):
        """Validate document path for security"""
        if not v.endswith('.pdf'):
            raise ValueError('Only PDF files are allowed')

        # Prevent directory traversal attacks
        if '..' in v or v.startswith('/'):
            raise ValueError('Invalid file path')

        # Check for suspicious characters
        if any(char in v for char in ['<', '>', '|', '&', ';']):
            raise ValueError('Invalid characters in file path')

        return v

    @validator('qa_suite')
    def validate_qa_suite(cls, v):
        """Validate Q&A suite for security"""
        if not isinstance(v, list):
            raise ValueError('QA suite must be a list')

        if len(v) > 50:
            raise ValueError('Too many questions (max 50)')

        if len(v) == 0:
            raise ValueError('QA suite cannot be empty')

        for i, qa in enumerate(v):
            if not isinstance(qa, dict):
                raise ValueError(f'QA item {i} must be a dictionary')

            question = qa.get('question', '')
            if len(question) > 1000:
                raise ValueError(f'Question {i} too long (max 1000 characters)')

            # Sanitize input - remove potentially dangerous characters
            qa['question'] = re.sub(r'[^\w\s\?\.\,\!\-\(\)\'\"]', '', question)

            expected_answer = qa.get('expected_answer', '')
            if len(expected_answer) > 2000:
                raise ValueError(f'Expected answer {i} too long (max 2000 characters)')

            # Validate required fields
            if not question.strip():
                raise ValueError(f'Question {i} cannot be empty')

        return v


class DataSanitizer:
    """Data sanitization utilities"""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Remove or mask sensitive information"""
        if not text:
            return text

        # Remove potential PII patterns
        patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # SSN
            (r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]'),  # Phone
            (r'\b\d{10}\b', '[PHONE]'),  # Phone (no dashes)
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email
            (r'\b\d{4} \d{4} \d{4} \d{4}\b', '[CREDIT_CARD]'),  # Credit cards
            (r'\b\d{16}\b', '[CREDIT_CARD]'),  # Credit cards (no spaces)
        ]

        sanitized = text
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized

    @staticmethod
    def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data before logging"""
        sanitized = data.copy()

        # Sanitize text fields that might contain sensitive data
        text_fields = ['question', 'answer', 'context', 'document_text', 'error']
        for field in text_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                sanitized[field] = DataSanitizer.sanitize_text(sanitized[field])

        return sanitized


class AuditLogger:
    """Security audit logging"""

    def __init__(self, log_file: str = "/app/logs/audit.log"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def log_event(self, event_type: str, user_id: Optional[str],
                  resource: str, action: str, details: Dict[str, Any] = None,
                  request: Optional[Request] = None):
        """Log security-relevant events"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id or "anonymous",
            "resource": resource,
            "action": action,
            "details": details or {},
            "ip_address": self._get_client_ip(request),
            "user_agent": self._get_user_agent(request)
        }

        # Sanitize audit data
        audit_entry = DataSanitizer.sanitize_log_data(audit_entry)

        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            security_logger.error(f"Failed to write audit log: {e}")

    def log_access(self, user_id: str, resource: str, success: bool, request: Optional[Request] = None):
        """Log access attempts"""
        self.log_event(
            event_type="access_attempt",
            user_id=user_id,
            resource=resource,
            action="access",
            details={"success": success},
            request=request
        )

    def log_api_call(self, endpoint: str, user_id: str, method: str, status_code: int,
                    request: Optional[Request] = None):
        """Log API calls"""
        self.log_event(
            event_type="api_call",
            user_id=user_id,
            resource=endpoint,
            action=method,
            details={"status_code": status_code},
            request=request
        )

    def _get_client_ip(self, request: Optional[Request]) -> str:
        """Get client IP address"""
        if request:
            return request.client.host if request.client else "unknown"
        return "unknown"

    def _get_user_agent(self, request: Optional[Request]) -> str:
        """Get user agent"""
        if request:
            return request.headers.get("user-agent", "unknown")
        return "unknown"


class SecurityConfig:
    """Security configuration validation"""

    REQUIRED_SECRETS = [
        'GEMINI_API_KEY',
        'SECRET_KEY'
    ]

    SECRET_PATTERNS = {
        'GEMINI_API_KEY': r'^[A-Za-z0-9_\-]{20,}$',
        'SECRET_KEY': r'^[A-Za-z0-9_\-]{32,}$'
    }

    @classmethod
    def validate_configuration(cls) -> Dict[str, bool]:
        """Validate all security configurations"""
        results = {}

        # Check required secrets exist
        for secret in cls.REQUIRED_SECRETS:
            if os.getenv(secret):
                results[f"{secret}_exists"] = True
            else:
                results[f"{secret}_exists"] = False

        # Validate secret formats
        for secret, pattern in cls.SECRET_PATTERNS.items():
            value = os.getenv(secret)
            if value and re.match(pattern, value):
                results[f"{secret}_format"] = True
            else:
                results[f"{secret}_format"] = False

        # Check file permissions if .env exists
        env_file = "/Volumes/WS4TB/ERSATZ_RAG/regulus/.env"
        if os.path.exists(env_file):
            import stat
            file_stat = os.stat(env_file)
            permissions = oct(file_stat.st_mode)[-3:]
            results['env_file_permissions'] = permissions == '600'
        else:
            results['env_file_permissions'] = False

        return results

    @classmethod
    def get_security_status(cls) -> str:
        """Get overall security status"""
        validation = cls.validate_configuration()

        critical_failures = [
            'GEMINI_API_KEY_exists',
            'SECRET_KEY_exists'
        ]

        for failure in critical_failures:
            if not validation.get(failure, False):
                return "CRITICAL: Security configuration incomplete"

        format_failures = [
            key for key in validation.keys()
            if key.endswith('_format') and not validation[key]
        ]

        if format_failures:
            return "WARNING: Some secrets may have weak formats"

        return "SECURE: All security configurations validated"


# Global audit logger instance
audit_logger = AuditLogger()


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded"""
    security_logger.warning(f"Rate limit exceeded for {request.client.host if request.client else 'unknown'}")

    # Log to audit
    audit_logger.log_event(
        event_type="rate_limit_exceeded",
        user_id="anonymous",
        resource=request.url.path,
        action=request.method,
        request=request
    )

    raise HTTPException(
        status_code=429,
        detail="Rate limit exceeded. Try again later."
    )


# Rate limiting decorators for different endpoints
GLOBAL_LIMITS = {
    "extract_structure": "10/minute",
    "upsert": "100/minute",
    "search": "200/minute",
    "validate_confidence": "50/minute",
    "process_pipeline": "5/minute"
}


def get_rate_limit(endpoint: str) -> str:
    """Get rate limit for endpoint"""
    return GLOBAL_LIMITS.get(endpoint, "100/minute")
