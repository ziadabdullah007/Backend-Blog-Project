from passlib.context import CryptContext

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# نستخدم bcrypt لتشفير الباسورد
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """
    تشفير كلمة المرور قبل تخزينها في الداتابيز
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    مقارنة الباسورد اللي المستخدم دخله مع المشفر في الداتابيز
    """
    return pwd_context.verify(plain_password, hashed_password)


