import os
from pathlib import Path
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_PATH: str = "./data/chroma"
    POLICY_DOCUMENT_PATH: str = "data/policy-manual.md"
    AMENDMENT_DOCUMENT_PATH: str = "data/Amendment No. 2026-01.md"

    class Config:
        env_file = PROJECT_ROOT / ".env"

settings = Settings()
settings.CHROMA_PATH = str((PROJECT_ROOT / settings.CHROMA_PATH).resolve()) if not Path(settings.CHROMA_PATH).is_absolute() else settings.CHROMA_PATH
settings.POLICY_DOCUMENT_PATH = str((PROJECT_ROOT / settings.POLICY_DOCUMENT_PATH).resolve()) if not Path(settings.POLICY_DOCUMENT_PATH).is_absolute() else settings.POLICY_DOCUMENT_PATH
settings.AMENDMENT_DOCUMENT_PATH = str((PROJECT_ROOT / settings.AMENDMENT_DOCUMENT_PATH).resolve()) if not Path(settings.AMENDMENT_DOCUMENT_PATH).is_absolute() else settings.AMENDMENT_DOCUMENT_PATH
