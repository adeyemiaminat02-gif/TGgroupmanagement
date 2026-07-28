import os
from typing import AsyncGenerator
from sqlalchemy import BigInteger, Boolean, Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import Config

# Ensure data directory exists for SQLite
if Config.DATABASE_URL.startswith("sqlite"):
    os.makedirs("./data", exist_ok=True)

engine = create_async_engine(Config.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

class GroupSettings(Base):
    __tablename__ = "group_settings"

    chat_id = Column(BigInteger, primary_key=True)
    welcome_enabled = Column(Boolean, default=True)
    welcome_text = Column(Text, default="Welcome {mention} to {chat}!")
    goodbye_text = Column(Text, default="{first} left the group.")
    verification_enabled = Column(Boolean, default=False)
    anti_spam_enabled = Column(Boolean, default=True)
    rules_text = Column(Text, nullable=True)
    max_warnings = Column(Integer, default=Config.MAX_WARNINGS)
    clean_welcome = Column(Boolean, default=True)

class UserWarning(Base):
    __tablename__ = "user_warnings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    reason = Column(String(255), default="No reason provided")
    warned_at = Column(DateTime, server_default=func.now())

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(64), nullable=False)
    file_id = Column(String(255), nullable=True)
    media_type = Column(String(32), default="text")  # text, photo, document, sticker
    content = Column(Text, nullable=True)

class Filter(Base):
    __tablename__ = "filters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    keyword = Column(String(128), nullable=False)
    reply_text = Column(Text, nullable=False)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
