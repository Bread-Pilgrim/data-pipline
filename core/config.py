from pydantic_settings import BaseSettings


class Configs(BaseSettings):
    CRAWL_URL: str

    class Config:
        env_file = ".env"
