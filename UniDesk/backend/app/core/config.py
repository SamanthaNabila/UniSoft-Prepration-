import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/unidesk"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )


settings = Settings()

if not settings.SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be configured before starting UniDesk.")

if (
    settings.SECRET_KEY in {"changeme", "dev-secret-key-change-me"}
    or settings.SECRET_KEY.startswith("<")
    or settings.SECRET_KEY.endswith(">")
):
    raise RuntimeError("SECRET_KEY must not use the default placeholder value.")

if len(settings.SECRET_KEY) < 32:
    raise RuntimeError("SECRET_KEY must contain at least 32 characters.")
