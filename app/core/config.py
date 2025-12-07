from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # === DATABASE ===
    DATABASE_URL: str = (
        "mysql+pymysql://root:"
        "bsbZgQBHGh2jNP2GAbN2l2hag5VmrzBjJw8p5thK3AbbZhHuAkYxKQOPHEWiZpUw"
        "@adsodigital.sbs:3306/inventory_db"
    )

    # === JWT CONFIG ===
    secret_key: str = "tu_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
