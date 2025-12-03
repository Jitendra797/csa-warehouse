from app.config.settings import get_settings
from .minio_service import MinioStorageService
from .s3_service import S3StorageService


def get_storage_service():
    """
    Return the appropriate storage service based on environment flags.

    - If DEV_MODE is true (default), use MinIO.
    - If DEV_MODE is false (e.g. in production), use AWS S3.
    """
    settings = get_settings()

    # Use the dedicated dev_mode flag, falling back to True if missing.
    dev_mode = getattr(settings, "dev_mode", True)

    if dev_mode:
        return MinioStorageService()

    return S3StorageService()


