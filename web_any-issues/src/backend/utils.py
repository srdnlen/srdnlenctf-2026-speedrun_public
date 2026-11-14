import hashlib
import secrets
import threading
import time

PBKDF2_ROUNDS = 100_000


def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ROUNDS)

    return f"{salt}${digest.hex()}"


def verify_password(stored, password):

    try:
        salt, digest = stored.split("$", 1)
    except (ValueError, AttributeError):
        return False
    
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ROUNDS)
    return secrets.compare_digest(check.hex(), digest)


class RateLimiter:

    def __init__(self, min_interval):
        self.min_interval = min_interval
        self._last = {}
        self._lock = threading.Lock()

    def hit(self, key):
        now = time.time()

        with self._lock:
            if len(self._last) > 10000:
                for k in [k for k, t in self._last.items() if now - t > self.min_interval]:
                    del self._last[k]
            if now - self._last.get(key, 0) < self.min_interval:
                return True
            
            self._last[key] = now

            return False
