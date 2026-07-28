import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "TGgroupmanagementbot")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/bot.db")
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
    LOG_GROUP_ID: int = int(os.getenv("LOG_GROUP_ID", "0"))
    MAX_WARNINGS: int = int(os.getenv("MAX_WARNINGS", "3"))
    VERIFY_TIMEOUT: int = int(os.getenv("VERIFY_TIMEOUT", "120"))
    AUTO_DELETE_WELCOME: int = int(os.getenv("AUTO_DELETE_WELCOME", "30"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is missing!")
