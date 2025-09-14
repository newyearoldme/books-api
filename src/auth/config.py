from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class AuthConfig(BaseSettings):
    SECRET_KEY: str = Field()
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

auth_config = AuthConfig()
