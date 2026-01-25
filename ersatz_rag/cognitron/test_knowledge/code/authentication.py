"""
Authentication system for medical-grade API
Implements JWT-based authentication with refresh tokens
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class MedicalAuthSystem:
    """
    Medical-grade authentication system with confidence tracking
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expires = timedelta(minutes=15)
        self.refresh_token_expires = timedelta(days=7)
        
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user credentials with medical-grade validation
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            User data if authentication successful, None otherwise
        """
        # Hash password for comparison
        stored_hash = self.get_user_password_hash(email)
        if not stored_hash:
            return None
            
        # Verify password using bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return self.get_user_data(email)
        
        return None
    
    def generate_access_token(self, user_data: Dict[str, Any]) -> str:
        """
        Generate JWT access token with medical-grade claims
        
        Args:
            user_data: User information dictionary
            
        Returns:
            JWT access token string
        """
        now = datetime.utcnow()
        payload = {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'role': user_data['role'],
            'medical_license': user_data.get('medical_license'),
            'iat': now,
            'exp': now + self.access_token_expires,
            'type': 'access'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """
        Generate JWT refresh token for token renewal
        
        Args:
            user_data: User information dictionary
            
        Returns:
            JWT refresh token string
        """
        now = datetime.utcnow()
        payload = {
            'user_id': user_data['id'],
            'iat': now,
            'exp': now + self.refresh_token_expires,
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return claims
        
        Args:
            token: JWT token string
            
        Returns:
            Token claims if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate new access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token if refresh valid, None otherwise
        """
        payload = self.verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return None
            
        # Get current user data
        user_data = self.get_user_data_by_id(payload['user_id'])
        if not user_data:
            return None
            
        return self.generate_access_token(user_data)
    
    def get_user_password_hash(self, email: str) -> Optional[bytes]:
        """Get stored password hash for user"""
        # Mock implementation - would connect to database
        return b'$2b$12$example_hash_for_testing'
    
    def get_user_data(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user data by email"""
        # Mock implementation - would connect to database
        return {
            'id': '123',
            'email': email,
            'role': 'medical_professional',
            'medical_license': 'MD123456'
        }
    
    def get_user_data_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data by ID"""
        # Mock implementation - would connect to database
        return {
            'id': user_id,
            'email': 'doctor@hospital.com',
            'role': 'medical_professional',
            'medical_license': 'MD123456'
        }