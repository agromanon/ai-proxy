"""
Rate limiting implementation
"""

import time
import threading
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    """Simple rate limiter implementation"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)  # ip -> [timestamps]
        self.lock = threading.Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if a request is allowed for the given identifier
        
        Args:
            identifier: Unique identifier (IP address, API key, etc.)
            
        Returns:
            True if request is allowed, False if rate limited
        """
        with self.lock:
            now = time.time()
            # Remove old requests outside the window
            self.requests[identifier] = [
                timestamp for timestamp in self.requests[identifier]
                if now - timestamp < self.window_seconds
            ]
            
            # Check if we're within the limit
            if len(self.requests[identifier]) < self.max_requests:
                # Add current request
                self.requests[identifier].append(now)
                return True
            else:
                # Rate limit exceeded
                return False
    
    def get_remaining_requests(self, identifier: str) -> int:
        """
        Get remaining requests for an identifier
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Number of remaining requests
        """
        with self.lock:
            now = time.time()
            # Remove old requests outside the window
            self.requests[identifier] = [
                timestamp for timestamp in self.requests[identifier]
                if now - timestamp < self.window_seconds
            ]
            
            return max(0, self.max_requests - len(self.requests[identifier]))
    
    def get_reset_time(self, identifier: str) -> float:
        """
        Get time when rate limit will reset for an identifier
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Timestamp when rate limit resets
        """
        with self.lock:
            if not self.requests[identifier]:
                return time.time()
            
            # Return time of oldest request + window
            oldest = min(self.requests[identifier])
            return oldest + self.window_seconds

# Global rate limiter instance
rate_limiter = RateLimiter()

def check_rate_limit(identifier: str):
    """
    Check rate limit for an identifier
    
    Args:
        identifier: Unique identifier (IP address, API key, etc.)
    """
    if not rate_limiter.is_allowed(identifier):
        from errors.handlers import RateLimitError
        raise RateLimitError(
            f"Rate limit exceeded. Maximum {rate_limiter.max_requests} requests "
            f"per {rate_limiter.window_seconds} seconds."
        )