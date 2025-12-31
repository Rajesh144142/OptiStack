from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "OptiStack"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Performance experimentation tool for data stores"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    MONGODB_URL: Optional[str] = None
    
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
    MYSQL_HOST: Optional[str] = None
    MYSQL_PORT: int = 3306
    MYSQL_USER: Optional[str] = None
    MYSQL_PASSWORD: Optional[str] = None
    MYSQL_DB: Optional[str] = None
    
    CASSANDRA_HOST: Optional[str] = None
    CASSANDRA_PORT: int = 9042
    CASSANDRA_KEYSPACE: Optional[str] = None
    
    COCKROACHDB_HOST: Optional[str] = None
    COCKROACHDB_PORT: int = 26257
    COCKROACHDB_USER: Optional[str] = None
    COCKROACHDB_PASSWORD: Optional[str] = None
    COCKROACHDB_DB: Optional[str] = None
    
    DYNAMODB_REGION: Optional[str] = None
    DYNAMODB_TABLE: Optional[str] = None
    
    INFLUXDB_URL: Optional[str] = None
    INFLUXDB_TOKEN: Optional[str] = None
    INFLUXDB_ORG: Optional[str] = None
    INFLUXDB_BUCKET: Optional[str] = None
    
    ELASTICSEARCH_URL: Optional[str] = None
    ELASTICSEARCH_USER: Optional[str] = None
    ELASTICSEARCH_PASSWORD: Optional[str] = None
    
    OPENTELEMETRY_ENABLED: bool = False
    OPENTELEMETRY_ENDPOINT: Optional[str] = None
    
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

