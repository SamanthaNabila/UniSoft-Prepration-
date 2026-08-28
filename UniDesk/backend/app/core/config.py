import os

from dotenv import load_dotenv

load_dotenv()

MIN_SECRET_KEY_LENGTH = 32
PLACEHOLDER_SECRET_KEYS = {"changeme", "dev-secret-key-change-me"}


def _load_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY", "")
    looks_like_unfilled_placeholder = secret_key.startswith("<") and secret_key.endswith(">")
    if (
        not secret_key
        or secret_key.lower() in PLACEHOLDER_SECRET_KEYS
        or looks_like_unfilled_placeholder
    ):
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. UniDesk refuses to start "
            "with no secret or a placeholder secret. Generate one with: "
            'python -c "import secrets; print(secrets.token_urlsafe(32))" '
            "and set it in backend/.env."
        )
    if len(secret_key) < MIN_SECRET_KEY_LENGTH:
        raise RuntimeError(
            f"SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters long "
            "(got a shorter value). Generate one with: "
            'python -c "import secrets; print(secrets.token_urlsafe(32))"'
        )
    return secret_key


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/unidesk"
    )
    SECRET_KEY: str = _load_secret_key()
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )


settings = Settings()
