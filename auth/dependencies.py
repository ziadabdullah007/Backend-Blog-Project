from fastapi import Depends, HTTPException
from auth.jwt_handler import get_current_user


# حماية أي endpoint
def require_user(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return current_user