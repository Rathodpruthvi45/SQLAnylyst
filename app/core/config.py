from pydantic_settings import BaseSettings
from pydantic import Field
class Setting(BaseSettings):
    DB_PATH: str = Field(..., env="DB_PATH")
    GOOGLE_API_KEY: str = Field(..., env="GOOGLE_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings=Setting()