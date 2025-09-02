from pydantic import BaseModel, EmailStr, ConfigDict


class EmailRegistrationInput(BaseModel):
    name: str
    email: EmailStr
    password: str

class EmailRegistrationResponse(BaseModel):
    name: str
    email: EmailStr
    message: str
    model_config = ConfigDict(from_attributes=True)

class VerifyEmailResponse(BaseModel):
    message: str

class LoginEmailInput(BaseModel):
    email: EmailStr
    password: str

class UserInfo(BaseModel):
    id: int
    name: str
    email: EmailStr


class LoginEmailResponse(BaseModel):
    user: UserInfo
    access_token: str
    token_type: str = "Bearer"
    message: str
    refresh_token: str | None = None


class LogoutInput(BaseModel):
    refresh_token: str


class LogoutResponse(BaseModel):
    message: str
