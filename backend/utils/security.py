from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError
from config import get

SECRET = get("security.jwt_secret")
EXPIRE_DAYS = int(get("security.jwt_expire_days"))
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_token(uid: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=EXPIRE_DAYS)
    payload = {"uid": uid, "exp": expire}
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload.get("uid")
    except JWTError:
        return None
