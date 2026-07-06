"""
config.py
---------
Centralized loader for all settings and keys, read from the .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    BASE_URL: str = os.getenv("BASE_URL", "https://api.groq.com/openai/v1")
    TARGET_MODEL: str = os.getenv("TARGET_MODEL", "llama-3.1-8b-instant")
    JUDGE_MODEL: str = os.getenv("JUDGE_MODEL", "llama-3.1-8b-instant")

    REQUEST_TIMEOUT_SECONDS: int = 30
    MAX_RETRIES: int = 2
    DELAY_BETWEEN_REQUESTS_SECONDS: float = 1.0  # respect provider rate limits

    @classmethod
    def validate(cls) -> None:
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY.startswith("sk-your-key"):
            raise ValueError(
                "API key is missing or was not updated.\n"
                "   1) Make sure a .env file exists in the project root.\n"
                "   2) Add your real key inside OPENAI_API_KEY."
            )