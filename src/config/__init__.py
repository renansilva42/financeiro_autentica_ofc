import os
from pathlib import Path
from pydantic_settings import BaseSettings 

class Settings(BaseSettings):
    OMIE_APP_KEY: str = "4012414987581"
    OMIE_APP_SECRET: str = "954c2407f8290df795a0063abc970206"
    BASE_URL: str = "https://app.omie.com.br/api/v1/"
    
    class Config:
        # Buscar o .env no diretório raiz do projeto
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)