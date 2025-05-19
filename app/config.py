from pydantic_settings import BaseSettings  # ✅ actualizado para v2


class Settings(BaseSettings):
    ENVIRONMENT: str = "local"

    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "aula_inteligente"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "admin123"

    CLOUD_DATABASE_URL: str = ""
    CLOUD_NAME: str = ""
    CLOUD_API_KEY: str = ""
    CLOUD_API_SECRET: str = ""
    SECRET_KEY: str = "supersecreto123"

    class Config:
        env_file = ".env"


settings = Settings()


def get_database_url():
    if settings.ENVIRONMENT == "nube":
        return settings.CLOUD_DATABASE_URL
    else:
        return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
