"""
CipherNest - Telegram Crypto Bot
Security utilities and rate limiting
"""

import time
from collections import defaultdict
from typing import Dict


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[int, list] = defaultdict(list)
    
    def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limit"""
        now = time.time()
        # Remove old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        # Record this request
        self.requests[user_id].append(now)
        return True
    
    def reset(self, user_id: int):
        """Reset rate limit for user"""
        if user_id in self.requests:
            del self.requests[user_id]


class DataSanitizer:
    """Ensure data is cleaned up after processing"""
    
    @staticmethod
    def secure_delete(data: dict):
        """Overwrite dict values with None for secure deletion"""
        for key in data:
            data[key] = None
        data.clear()


class InputValidator:
    """Validate and sanitize user inputs"""
    
    # Suspicious patterns that might indicate malicious input
    SUSPICIOUS_PATTERNS = [
        r'<script>',
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'on\w+\s*=',
    ]
    
    @classmethod
    def validate_text(cls, text: str) -> tuple[bool, str]:
        """Validate text input for safety"""
        if not text or len(text.strip()) == 0:
            return False, "Empty input"
        
        if len(text) > 10000:  # 10KB limit for text
            return False, "Input too long (max 10,000 characters)"
        
        # Check for suspicious patterns
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if pattern.lower() in text.lower():
                return False, "Potentially unsafe input detected"
        
        return True, "OK"
    
    @classmethod
    def validate_password(cls, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password too short (min 8 characters)"
        
        if len(password) > 100:
            return False, "Password too long (max 100 characters)"
        
        return True, "OK"
