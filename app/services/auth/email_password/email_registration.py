from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlalchemy.exc import SQLAlchemyError

from app.db.pg_engine import sessionmanager
from app.db.pg_dml import insert_record, upsert_record
from app.db.models.app_users import AppUser
from app.configs.email_configs import email_conf
from app.services.auth.email_password.jwt_helper import jwt_helper
from app.configs.settings import settings
from app.db.crud.app_users import AppUserCrud

from .schemas import EmailRegistrationInput, EmailRegistrationResponse


class EmailRegistration:
    def __init__(self):
        # Mail client
        self.mailer = FastMail(email_conf.smtp_conf)

    async def _create_user_record(self, user_data, hashed_password) -> AppUser:
        async with sessionmanager.session() as s:
            try:
                user = AppUser(
                    name=user_data.name,
                    email=user_data.email,
                    password=hashed_password
                )
                return await insert_record(s, user)
            except SQLAlchemyError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to insert record: {str(e)}"
                )

    async def _send_confirmation_email(self, user, token: str) -> None:
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[user.email],
            body=(
                f"Hello {user.name},\n\n"
                f"Please confirm your registration by clicking the link below:\n"
                f"{settings.mail_verify_base_url}/verify-email?token={token}\n\n"
                "Thank you!"
            ),
            subtype=MessageType.html
        )
        await self.mailer.send_message(message)

    async def register(self, user_data: EmailRegistrationInput) -> EmailRegistrationResponse:
        # Check for existing user
        async with sessionmanager.session() as s:
            existing = await AppUserCrud(s).get_active_user_by_email(user_data.email)
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the password and create the user record
        hashed_password = jwt_helper.pwd_context.hash(user_data.password)
        user = await self._create_user_record(user_data, hashed_password)

        # Generate email confirmation token
        token = jwt_helper.create_email_token({"sub": user.email})
        await self._send_confirmation_email(user, token)
        return EmailRegistrationResponse(name=user.name, email=user.email,
                                         message="User registered successfully. Confirmation email sent.")


    async def verify_email(self, token: str) -> str:
        payload = jwt_helper.verify_email_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        async with sessionmanager.session() as s:
            try:
                user: AppUser = await AppUserCrud(s).get_inactive_user_by_email(email)
                if user is None:
                    raise HTTPException(status_code=404, detail="User not found")

                if user.is_active:
                    return "Email already verified."

                user.is_active = True
                await upsert_record(s, user)
                return "Email verified successfully."
            except SQLAlchemyError:
                await s.rollback()
                raise HTTPException(status_code=500,
                                    detail="Database error while verifying email")

email_registration = EmailRegistration()
