import os
from minio import Minio
from io import BytesIO
from datetime import datetime, timedelta
from app.config.settings import MinIOSettings
from .base_storage import BaseStorage

settings = MinIOSettings()


class MinioStorageService(BaseStorage):
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY.get_secret_value(),
            secret_key=settings.MINIO_SECRET_KEY.get_secret_value(),
            secure=False,
        )
        self.bucket = settings.MINIO_BUCKET_NAME
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
        self.minio_presigned_url_expiry = settings.MINIO_PRESIGNED_URL_EXPIRY

        # Set the bucket policy with dynamic bucket name
        policy = f"""
        {{
            "Version": "2012-10-17",
            "Statement": [
                {{
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::{self.bucket}/*"
                }}
            ]
        }}
        """

        self.client.set_bucket_policy(self.bucket, policy)

    def upload_file(self, file_bytes: bytes, file_name: str) -> str:
        self.client.put_object(self.bucket, file_name, BytesIO(file_bytes), length=len(file_bytes))
        return f"{self.bucket}/{file_name}"

    def generate_presigned_url(self, filename: str, user_id: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, extension = os.path.splitext(filename)
        new_filename = f"{name}_{timestamp}{extension}"
        object_name = f"{user_id}/{new_filename}"

        url = self.client.presigned_put_object(
            self.bucket, object_name, expires=timedelta(seconds=self.minio_presigned_url_expiry)
        )

        return url, object_name

    def generate_download_url(self, filename: str):
        """Generate a presigned URL for downloading a file"""
        url = self.client.presigned_get_object(
            self.bucket, filename, expires=timedelta(seconds=self.minio_presigned_url_expiry)
        )
        return url

    def get_object(self, object_name: str, bucket_name: str = None) -> BytesIO:
        """Get object from MinIO"""
        try:
            bucket_name = bucket_name or self.bucket
            return self.client.get_object(bucket_name, object_name)
        except Exception as e:
            raise ValueError(f"Error getting object from MinIO: {str(e)}")


def get_minio_service():
    return MinioStorageService()
