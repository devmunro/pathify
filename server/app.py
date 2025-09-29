from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from routes.auth import router as auth_router
from routes.hikes import router as hike_router

app = FastAPI(
    title="Pathify Backend",
    description="API for tracking hikes, recording GPS paths, and managing user authentication.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/", summary="Welcome message", tags=["General"])
def hello():
    """Simple welcome message for the API."""
    return {"message": "Welcome to the Pathify API"}

# -----------------------------
# Include Routers with Tags
# -----------------------------
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(hike_router, prefix="/hike", tags=["Hikes"])

# -----------------------------
# Custom OpenAPI
# -----------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="API for tracking hikes, recording GPS paths, and managing authentication.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi