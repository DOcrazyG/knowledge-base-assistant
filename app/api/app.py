from fastapi import FastAPI
from fastapi import APIRouter
from contextlib import asynccontextmanager

from .login import router as login_router
from .user import router as user_router
from .role import router as role_router
from .permission import router as permission_router
from .file import router as file_router
from .chat import router as chat_router
from ..core.init_db import init_all
from ..core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_all()
    yield
    await engine.dispose()


app = FastAPI(
    title="Knowledge-Base-Assistant-API",
    description="API for Knowledge Base Assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(login_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(permission_router)
app.include_router(file_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "welcome to Knowledge Base Assistant API"}