# API Documentation

Base URL: `/api`

The FastAPI application automatically exposes interactive documentation:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

Use these pages to explore endpoints, schemas, and try requests directly from the browser after starting the server.

## Upload Image

- **Endpoint:** `POST /api/upload/`
- **Description:** Upload a new image for a user.
- **Request:** `multipart/form-data` with fields:
  - `file`: image file to upload.
  - `metadata`: JSON string with keys `user_id`, `chapter`, `ayat_start`, `ayat_end`, and `script_id`.
- **Response:** `ImageUploadResponse` describing the stored image.

## List User Uploads

- **Endpoint:** `GET /api/uploads/{user_id}`
- **Description:** Retrieve image uploads for the specified user.
- **Response:** List of `ImageUploadRecord` objects.

## Register User

- **Endpoint:** `POST /api/register`
- **Description:** Create a new user account with email and password credentials.
- **Response:** `EmailRegistrationResponse` and status code `201`.

## Verify Email

- **Endpoint:** `GET /api/verify-email?token=...`
- **Description:** Verify a user's email address using the token sent in the verification email.
- **Response:** Confirmation string.

## Login

- **Endpoint:** `POST /api/login`
- **Description:** Authenticate a user by email and password.
- **Response:** `LoginEmailResponse` containing access and refresh tokens.

## Logout

- **Endpoint:** `POST /api/logout`
- **Description:** Invalidate a user's refresh token and end their session.
- **Response:** `LogoutResponse` confirming logout.

## Root

- **Endpoint:** `GET /api/`
- **Description:** Health check endpoint returning `{"message": "Hello World"}`.

