from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    name: str = "fastapibasic"
    version: str = "0.0.0"

    model_config = SettingsConfigDict(env_file=".env")
