import io
import requests
import pandas as pd
import mimetypes
from ..config.logging import get_logger
from app.db.database import datasets_collection
from app.services.storage.minio_service import get_minio_service

logger = get_logger("db")
minio_service = get_minio_service()


def download_and_store_file(file_url):
    try:
        logger.info(f"Attempting to download file from URL: {file_url}")
        response = requests.get(file_url)
        logger.debug(f"HTTP response status: {response.status_code}")
        response.raise_for_status()  # Raise an error for bad responses

        # Convert CSV to pandas DataFrame
        csv_content = response.content.decode("utf-8")
        df = pd.read_csv(io.StringIO(csv_content))
        records = df.to_dict(orient="records")

        logger.info(f"Successfully downloaded and converted file from {file_url}")
        return records
    except requests.RequestException as e:
        logger.error(f"Error downloading file from {file_url}: {str(e)}")
        print(f"Error downloading file: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing file from {file_url}: {str(e)}")
        return None


# Store file metadata in MongoDB
def store_file_metadata(filename, content_type, file_url):
    logger.info(f"Storing metadata for file: {filename}")
    records = download_and_store_file(file_url)
    if records is None:
        logger.warning(f"Failed to process file: {file_url}")
        print("Failed to download or convert the file. Try looking at the URL accessibility.")
        return
    document = {"filename": filename, "type": content_type, "url": file_url, "data": records}
    result = datasets_collection.insert_one(document)
    logger.info(f"File metadata stored in MongoDB with ID: {result.inserted_id}")


def upload_file_to_presigned_url(file_path: str):
    filename = file_path.split("/")[-1]
    upload_url = minio_service.generate_presigned_url(filename)

    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or "application/octet-stream"

    with open(file_path, "rb") as f:
        response = requests.put(upload_url, data=f, headers={"Content-Type": mime_type})

    if response.status_code == 200:
        print("Upload successful!")
        store_file_metadata(filename, mime_type, upload_url.split("?")[0])
        print("File URL (MinIO):", upload_url.split("?")[0])
    else:
        print("Upload failed with code:", response.status_code)
        print(response.text)
