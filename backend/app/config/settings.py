# settings.py
from pydantic import MongoDsn, SecretStr, Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Warehouse"
    # High-level environment name, controlled via ENVIRONMENT env var.
    # Example values: "development", "staging", "production"
    environment: str = Field(default="development", env="ENVIRONMENT")
    # When True we treat the app as running in developer/local mode and use MinIO.
    # When False (e.g. in production) we use AWS S3.
    dev_mode: bool = Field(default=True, env="DEV_MODE")
    logs_directory: str = "logs/"
    debug: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


class DatabaseSettings(BaseSettings):
    mongodb_uri: MongoDsn
    mongodb_database: str = "uploads"
    minio_presigned_url_expiry: int = Field(default=3600)

    class Config:
        env_file = ".env"
        extra = "ignore"


# class AWSSettings(BaseSettings):
#     aws_region: str = "us-east-1"
#     aws_access_key_id: str
#     aws_secret_access_key: str
#     s3_bucket_name: str
#     s3_presigned_url_expiry: int = 3600

#     class Config:
#         env_file = ".env"
#         extra = "ignore"


class MinIOSettings(BaseSettings):
    MINIO_ENDPOINT: str = Field(..., env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: SecretStr = Field(..., env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: SecretStr = Field(..., env="MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME: str = Field(default="datasets", env="MINIO_BUCKET_NAME")
    MINIO_PRESIGNED_URL_EXPIRY: int = 3600

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()


# @lru_cache()
# def get_aws_settings() -> AWSSettings:
#     return AWSSettings()


@lru_cache()
def get_minio_settings() -> MinIOSettings:
    return MinIOSettings()
