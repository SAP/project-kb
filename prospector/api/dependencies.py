from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# ======================================
# AUTH STUFF
# The following is taken from https://fastapi.tiangolo.com/tutorial/security/first-steps/
# with slight modifications to support roles.
# This will be moved to a separate file eventually,
# as explained here: https://fastapi.tiangolo.com/tutorial/bigger-applications/

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "roles": ["user"],
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "roles": ["user", "admin"],
        "hashed_password": "fakehashedsecret2",
        "disabled": False,
    },
}


class User(BaseModel):
    username: str
    email: Optional[str] = None
    roles: Optional[list] = []
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


def fake_decode_token(token):
    # TODO This doesn't provide any security at all
    user = get_user(fake_users_db, token)
    return user


def fake_hash_password(password: str):
    # TODO This doesn't provide any security at all
    return "fakehashed" + password


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
