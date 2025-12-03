from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AWSSettings(BaseSettings):
    """
    AWS configuration for S3.

    Expected environment variables (with sensible defaults where possible):
      - AWS_REGION (default: "us-east-1")
      - AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY
      - S3_BUCKET_NAME
      - S3_PRESIGNED_URL_EXPIRY (optional, seconds; default: 3600)
    """

    aws_region: str = "us-east-1"
    aws_access_key_id: SecretStr
    aws_secret_access_key: SecretStr
    s3_bucket_name: str
    s3_presigned_url_expiry: int = 3600

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_aws_settings() -> AWSSettings:
    return AWSSettings()


