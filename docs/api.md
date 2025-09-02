# API Documentation

Base URL: `/api`

The FastAPI application automatically exposes interactive documentation:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

Use these pages to explore endpoints, schemas, and try requests directly from the browser after starting the server.

## Upload Image

- **Endpoint:** `POST /api/upload/`
- **Description:** Upload a new image for a user.
- **Headers:** `Authorization: Bearer <access_token>`
- **Request:** `multipart/form-data` with fields:
  - `file`: image file to upload.
  - `metadata`: JSON string with keys `chapter`, `line_start`, `line_end`, and `script_id`.
- **Response:** `ImageUploadResponse` describing the stored image.

## List User Uploads

- **Endpoint:** `GET /api/uploads/`
- **Description:** Retrieve image uploads for the authenticated user.
- **Headers:** `Authorization: Bearer <access_token>`
- **Response:** List of `ImageUploadRecord` objects.

## Register User

- **Endpoint:** `POST /api/register`
- **Description:** Create a new user account with email and password credentials.
- **Response:** `EmailRegistrationResponse` and status code `200`.

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
- **Description:** Invalidate the authenticated user's refresh token and end their session. The user ID is taken from the Bearer token.
- **Headers:** `Authorization: Bearer <access_token>`
- **Request:** JSON object with `refresh_token`.
- **Response:** `LogoutResponse` confirming logout.

## Root

- **Endpoint:** `GET /api/`
- **Description:** Health check endpoint returning `{"message": "Hello World"}`.

