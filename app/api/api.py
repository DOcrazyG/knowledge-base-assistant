from fastapi import FastAPI
from .user import router as user_router
from .role import router as role_router

app = FastAPI(title="Knowledge-Base-Assistant-API", description="API for Knowledge Base Assistant", version="0.1.0")
app.include_router(user_router)
app.include_router(role_router)


@app.get("/")
def root():
    return {"message": "welcome to Knowledge Base Assistant API"}
