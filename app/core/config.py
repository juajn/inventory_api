from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URI: str = (
        "mysql+pymysql://root:"
        "bsbZgQBHGh2jNP2GAbN2l2hag5VmrzBjJw8p5thK3AbbZhHuAkYxKQOPHEWiZpUw"
        "@adsodigital.sbs:3306/inventory_db"
    )

    class Config:
        env_file = ".env"

settings = Settings()

