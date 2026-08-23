import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_PATH: str = "./data/chroma"
    POLICY_DOCUMENT_PATH: str = "../data/policy-manual.md"

    class Config:
        env_file = ".env"

settings = Settings()
