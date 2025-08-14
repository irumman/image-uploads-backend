from fastapi import HTTPException, Depends
from pydantic import EmailStr
from starlette import status

from app.services.auth.email_password.jwt_helper import jwt_helper
from app.db.crud.app_users import AppUserCrud
from app.db.pg_engine import get_db_session
from app.services.auth.email_password.schemas import LoginEmailResponse


class LoginUserPass:

    def __init__(self, session=Depends(get_db_session)):
        self.session = session

    async def login_with_password(self, email: EmailStr, password: str) -> LoginEmailResponse:
        user = await AppUserCrud(self.session).get_active_user_by_email(email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

        if user.password is None or not jwt_helper.verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        #TODO: add session info
        # Issue JWT with user id as sub
        sub = {"id": user.id}
        token =  jwt_helper.create_access_token(sub=sub, secret=jwt_helper.secret_key, expires_minutes=1400)
        resp = LoginEmailResponse(access_token=token, token_type="bearer", message="Login successful")
        return resp