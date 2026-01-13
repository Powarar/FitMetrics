from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    SYNC_DATABASE_URL: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM: str

    REDIS_URL: str
    CACHE_TTL_DEFAULT: int


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.test", extra="ignore")
    TEST_DATABASE_URL: str

settings = Settings() # type: ignore
test_settings = TestSettings() # type: ignore
