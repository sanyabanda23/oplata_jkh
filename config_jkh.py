import os
from typing import List
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    con_sql: List[str]
    BOT_TOKEN: str
    BOT_TOKEN_VK: str
    GROUP_ID: int
    REDIS_URL: str
    tg_user_id : int
    URL_payments: str
    URL_payments_2: str
    URL_payments_yki: str
    URL_payments_yki_2: str
    URL_vhod: str
    login_telefon: str
    bank_card: str
    pasword_text: str
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

# Диагностика: проверяем существование .env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if not os.path.exists(env_path):
    logger.error(f".env file not found at: {env_path}")
    logger.info("Current directory: " + os.getcwd())
    logger.info("Files here: " + str(os.listdir(".")))
    raise FileNotFoundError(f".env file not found: {env_path}")
else:
    logger.info(f".env file found at: {env_path}")


# Инициализация конфигурации
settings = Settings()

# Настройка логирования
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(log_file_path, format=settings.FORMAT_LOG, level="INFO", rotation=settings.LOG_ROTATION)