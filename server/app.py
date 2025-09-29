from fastapi import FastAPI
from routes.auth import router as auth_router

app = FastAPI(title="Pathify Backend")

@app.get("/")
def hello():
    return {"message": "Hello"}

app.include_router(auth_router, prefix="/auth")
print("Main router loaded")
