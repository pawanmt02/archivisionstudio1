from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = 'archivision-dev-secret-key-change-in-production'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DATABASE_URL: str = 'sqlite:///./archivision.db'
    COLAB_TUNNEL_URL: str = ''
    CORS_ORIGINS: list = ['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:3000']

settings = Settings()
