import time

import bcrypt

from middleware.error_handler import BadRequestException

MAX_PIN_ATTEMPTS = 5
PIN_LOCK_SECONDS = 300


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


hash_pin = hash_password
verify_pin = verify_password


def check_rate_limit(user) -> None:
    if user.pin_locked_until and user.pin_locked_until > int(time.time()):
        remaining = user.pin_locked_until - int(time.time())
        raise BadRequestException(f"账户已锁定，请{remaining}秒后重试")


def increment_attempts(user) -> None:
    user.pin_attempts += 1
    if user.pin_attempts >= MAX_PIN_ATTEMPTS:
        user.pin_locked_until = int(time.time()) + PIN_LOCK_SECONDS
        user.pin_attempts = 0


def reset_attempts(user) -> None:
    user.pin_attempts = 0
    user.pin_locked_until = None
