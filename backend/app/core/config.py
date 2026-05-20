from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Banco de leitura
    ORACLE_READ_USER: str
    ORACLE_READ_PASSWORD: str
    ORACLE_READ_HOST: str
    ORACLE_READ_PORT: int = 1521
    ORACLE_READ_SERVICE: str

    # Banco de escrita
    ORACLE_WRITE_USER: str
    ORACLE_WRITE_PASSWORD: str
    ORACLE_WRITE_HOST: str
    ORACLE_WRITE_PORT: int = 1521
    ORACLE_WRITE_SERVICE: str

    # Segurança
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SESSION_SECRET_KEY: str


settings = Settings()
