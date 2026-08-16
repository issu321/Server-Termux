from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.attempts = defaultdict(list)
    
    def is_allowed(self, key, max_attempts=5, window_seconds=300):
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        self.attempts[key] = [t for t in self.attempts[key] if t > window_start]
        
        if len(self.attempts[key]) >= max_attempts:
            return False
        
        self.attempts[key].append(now)
        return True
    
    def reset(self, key):
        if key in self.attempts:
            del self.attempts[key]
    
    def get_remaining(self, key, max_attempts=5, window_seconds=300):
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        self.attempts[key] = [t for t in self.attempts[key] if t > window_start]
        return max(0, max_attempts - len(self.attempts[key]))

limiter = RateLimiter()