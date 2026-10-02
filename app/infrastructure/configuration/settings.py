import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    jooble_api_key: str
    jooble_base_url: str
    gateway_user_id_header: str


@lru_cache
def get_settings() -> Settings:
    values = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "JOOBLE_API_KEY": os.getenv("JOOBLE_API_KEY"),
        "JOOBLE_BASE_URL": os.getenv("JOOBLE_BASE_URL"),
        "GATEWAY_USER_ID_HEADER": os.getenv("GATEWAY_USER_ID_HEADER"),
    }
    missing = [name for name, value in values.items() if not value or not value.strip()]
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")

    return Settings(
        database_url=values["DATABASE_URL"].strip(),
        jooble_api_key=values["JOOBLE_API_KEY"].strip(),
        jooble_base_url=values["JOOBLE_BASE_URL"].rstrip("/"),
        gateway_user_id_header=values["GATEWAY_USER_ID_HEADER"].strip(),
    )
