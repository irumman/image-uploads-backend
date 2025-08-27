# Image Uploads Backend

FastAPI service providing image upload and authentication endpoints.

## API Documentation

See [docs/api.md](docs/api.md) for an overview of available routes and expected request/response bodies.

After running the server, interactive FastAPI documentation is available at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Development

Install dependencies and run the application locally:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run the test suite with:

```bash
pytest
```

