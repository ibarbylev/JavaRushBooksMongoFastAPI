from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.db.initial_data import load_books
from app.routers import books
from app.db.local_settings import MONGODB_URL_ATLAS

DB_NAME = "books_db"
BOOKS_JSON = "books.json"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ----------------------
    #        STARTUP
    # ----------------------
    app.state.mongo_client = AsyncIOMotorClient(MONGODB_URL_ATLAS)
    app.state.db = app.state.mongo_client[DB_NAME]

    # Загружаем начальные данные
    await load_books(app.state.db)

    yield

    # ----------------------
    #       SHUTDOWN
    # ----------------------
    app.state.mongo_client.close()


app = FastAPI(
    title="Books API V2(MongoDB + Enum genres)",
    lifespan=lifespan,
)


# Роутеры
app.include_router(books.router)