import secrets
import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    API_PATH_PREFIX: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = 'localhost'
    SERVER_HOST: str = 'http://localhost:8081'
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str
    MSSQL_HOST: str
    MSSQL_USER: str
    MSSQL_PASSWORD: str
    MSSQL_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        user = os.getenv("MSSQL_USER", "sa")
        password = os.getenv("MSSQL_PASSWORD", "")
        server = os.getenv("MSSQL_HOST", "")
        db = os.getenv("MSSQL_DB", "app")
        driver = os.getenv("MSSQL_DRIVER", "FreeTDS")

        return f"mssql+pyodbc://{user}:{password}@{server}:1433/{db}?driver={driver}"

    class Config:
        case_sensitive = True


settings = Settings()