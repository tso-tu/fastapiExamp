from typing import Optional

from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
import asyncpg

# Настройки подключения к PostgreSQL
DATABASE_URL = "postgresql+asyncpg://booknest_user:ThZTf1PkyRjU27NMa1YkQPw7cI8xlOAh@dpg-d4a7s1muk2gs73feeerg-a.frankfurt-postgres.render.com/booknest_db_6jhl"

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание сессии
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Базовая модель
Base = declarative_base()

# Модель Item
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Создание таблиц при старте приложения
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    # Закрытие соединения при завершении работы
    await engine.dispose()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{id}")
async def read_item(id: int, q: Optional[str] = None):
    async with AsyncSessionLocal() as session:
        result = await session.get(Item, item_id)
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"id": result.id, "name": result.name, "description": result.description, "q": q}

@app.post("/items/")
async def create_item(name: str, description: Optional[str] = None):
    async with AsyncSessionLocal() as session:
        item = Item(name=name, description=description)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return {"id": item.id, "name": item.name, "description": item.description}
