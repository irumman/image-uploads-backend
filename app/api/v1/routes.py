from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks, Query, Depends
from app.services.image_uploads.schemas import ImageUploadResponse, ImageUploadInputRequest
from app.services.image_uploads.uploads import upload_service
from app.services.auth.email_password.email_registration import email_registration
from app.services.auth.email_password.login_user_pass import LoginUserPass
from app.services.auth.email_password.schemas import (EmailRegistrationInput, EmailRegistrationResponse,
                                                      LoginEmailInput, LoginEmailResponse)

router = APIRouter()

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...), metadata: str = Form(...)):
    try:
        meta_obj = ImageUploadInputRequest.model_validate_json(metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid upload metadata")
    upload_resp = await upload_service.upload_image(
        file,
        user_id=meta_obj.user_id,
        chapter=meta_obj.chapter,
        ayat_start=meta_obj.ayat_start,
        ayat_end=meta_obj.ayat_end
    )
    return upload_resp

@router.post("/register", response_model=EmailRegistrationResponse, status_code=201)
async def register(user_in: EmailRegistrationInput):
    response: EmailRegistrationResponse = await email_registration.register(user_data=user_in)
    return response


@router.get("/verify-email", response_model=str, status_code=200)
async def register(token: str = Query(..., description="JWT sent in the verification link"),):
    response: str = await email_registration.verify_email(token=token)
    return response

@router.post("/login",response_model=LoginEmailResponse, status_code=200)
async def login(body: LoginEmailInput, login_user_pass: LoginUserPass = Depends()
):
    resp = await login_user_pass.login_with_password(body.email, body.password)
    return resp


@router.get("/")
async  def root():
    return {"message": "Hello World"}