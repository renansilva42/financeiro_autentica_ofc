from pydantic_settings import BaseSettings 

class Settings(BaseSettings):
    OMIE_APP_KEY: str
    OMIE_APP_SECRET: str
    BASE_URL: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"