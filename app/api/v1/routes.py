from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query, Depends, Request
from app.core.logger import logger

from app.db.pg_engine import get_db_session
from app.api.auth import auth_dependency
from app.services.image_uploads.schemas import (
    ImageUploadResponse,
    ImageUploadInputRequest,
    ImageUploadRecord,
)
from app.services.image_uploads.uploads import upload_service
from app.services.auth.email_password.email_registration import email_registration
from app.services.auth.email_password.login_user_pass import LoginUserPass
from app.services.auth.email_password.logout import Logout
from app.services.auth.email_password.schemas import (
    EmailRegistrationInput,
    EmailRegistrationResponse,
    LoginEmailInput,
    LoginEmailResponse,
    LogoutInput,
    LogoutResponse,
)

router = APIRouter()

# The upload endpoint previously omitted a trailing slash.  FastAPI interprets
# this strictly and would issue a ``307 Temporary Redirect`` when clients send a
# path ending with ``/`` (as the tests do).  Declaring the route with the
# trailing slash avoids the redirect and returns the intended status codes.
@router.post("/upload/", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    metadata: str = Form(...),
    db=Depends(get_db_session),
    user_id: int = Depends(auth_dependency),
):
    try:
        meta_obj = ImageUploadInputRequest.model_validate_json(metadata)
    except Exception:
        logger.exception("Invalid upload metadata")
        raise HTTPException(status_code=400, detail="Invalid upload metadata")
    if meta_obj.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    upload_resp = await upload_service.upload_image(
        db,
        file,
        user_id=user_id,
        chapter=meta_obj.chapter,
        line_start=meta_obj.line_start,
        line_end=meta_obj.line_end,
        script_id=meta_obj.script_id,
    )
    return upload_resp


@router.get("/uploads/{user_id}", response_model=list[ImageUploadRecord])
async def get_user_uploads(user_id: int):
    return await upload_service.get_user_uploads(user_id)

@router.post("/register", response_model=EmailRegistrationResponse, status_code=201)
async def register(user_in: EmailRegistrationInput, db=Depends(get_db_session)):
    response: EmailRegistrationResponse = await email_registration.register(
        db, user_data=user_in
    )
    return response


@router.get("/verify-email", response_model=str, status_code=200)
async def verify_email(
    token: str = Query(..., description="JWT sent in the verification link"),
    db=Depends(get_db_session),
):
    response: str = await email_registration.verify_email(db, token=token)
    return response

@router.post("/login",response_model=LoginEmailResponse, status_code=200)
async def login(body: LoginEmailInput, request: Request, db=Depends(get_db_session)):
    login_user_pass: LoginUserPass = LoginUserPass(db,body.email, body.password)
    resp = await login_user_pass.login_with_password(request=request)
    return resp


@router.post("/logout", response_model=LogoutResponse, status_code=200)
async def logout(body: LogoutInput, db=Depends(get_db_session)):
    service = Logout(db, body.user_id, body.refresh_token)
    return await service.logout()


@router.get("/")
async  def root():
    return {"message": "Hello World"}

