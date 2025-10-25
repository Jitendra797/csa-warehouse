import uuid
import mimetypes
import pandas as pd
from io import BytesIO
from datetime import datetime, timezone
from pymongo.collection import Collection
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from app.schemas.models import (
    CreateDatasetInformationRequest,
    CreateDatasetInformationResponse,
    PresignedURLResponse,
    ExtractCsvDataRequest,
    ExtractAndStoreResponse,
    DatasetColumnsResponse,
    DatasetColumnsRequest,
)
from app.db.database import files as files_collection, datasets_collection, dataset_information_collection
from app.services.storage.mongodb_service import store_to_mongodb, get_user_info
from app.services.storage.minio_service import get_minio_service

datasets_router = APIRouter()


@datasets_router.get("/presignedURL", response_model=PresignedURLResponse)
def get_presigned_url(filename: str, user_id: str) -> PresignedURLResponse:
    minio_service = get_minio_service()
    url, object_name = minio_service.generate_presigned_url(
        filename=filename, user_id=user_id)
    return PresignedURLResponse(upload_url=url, object_name=object_name)


@datasets_router.post("/datasets/create", response_model=CreateDatasetInformationResponse)
async def create_dataset(request: CreateDatasetInformationRequest) -> CreateDatasetInformationResponse:
    try:
        dataset_doc = datasets_collection.find_one({"_id": request.dataset_id})

        if not dataset_doc:
            raise HTTPException(
                status_code=404, detail="Dataset not found in datasets_collection")

        # Get user information
        user_info = get_user_info(request.user_id)

        dataset_info = {
            "_id": ObjectId(),
            "dataset_id": ObjectId(request.dataset_id),
            "file_id": ObjectId(request.file_id) if request.file_id else None,
            "dataset_name": request.dataset_name,
            "description": request.description,
            "permission": request.permission,
            "dataset_type": request.dataset_type,
            "tags": request.tags,
            "is_temporal": request.is_temporal,
            "is_spatial": request.is_spatial,
            "temporal_granularities": request.temporal_granularities or [],
            "spatial_granularities": request.spatial_granularities or [],
            "location_columns": request.location_columns or [],
            "time_columns": request.time_columns or [],
            "pulled_from_pipeline": False,
            "pipeline_id": None,  # null for manual datasets
            "user_id": [ObjectId(request.user_id)],
            "username": [user_info["user_name"]],
            "user_email": [user_info["user_email"]],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        dataset_information_collection.insert_one(dataset_info)

        return CreateDatasetInformationResponse(status="success", id=dataset_info["_id"])

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@datasets_router.post("/datasets/extract", response_model=ExtractAndStoreResponse)
def extract_csv(request: ExtractCsvDataRequest) -> ExtractAndStoreResponse:
    new_file_id = uuid.uuid4().hex
    dataset_id = uuid.uuid4().hex
    minio_service = get_minio_service()

    response = minio_service.get_object(object_name=request.file_object)
    if not response:
        raise HTTPException(status_code=404, detail="File not found in MinIO")

    file_content = response.read()
    file_type = mimetypes.guess_type(request.file_object)[
        0] or "application/octet-stream"
    file_size = len(file_content)

    response.close()
    response.release_conn()

    file_metadata = {
        "file_id": new_file_id,
        "file_location": request.file_object,
        "file_type": file_type,
        "file_size": file_size,
        "uploaded_by": request.user_name,
        "user_id": request.user_id,
    }

    files_collection.insert_one(file_metadata)

    try:
        df = pd.read_csv(BytesIO(file_content))
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error parsing CSV: {str(e)}")

    dataset_records = df.to_dict(orient="records")
    current_time = datetime.now(timezone.utc).isoformat()
    datasets_collection.insert_one(
        {
            "_id": ObjectId(dataset_id),
            "data": dataset_records,
            "columns": df.columns.to_list(),
            "record_count": len(dataset_records),
            "created_at": current_time,
            "updated_at": current_time,
        }
    )

    return ExtractAndStoreResponse(status="success", file_id=new_file_id, dataset_id=dataset_id)


@datasets_router.get("/datasets/columns", response_model=DatasetColumnsResponse)
def get_dataset_columns(dataset_id: str, search: str = None) -> DatasetColumnsResponse:
    # Fetch dataset metadata
    dataset = datasets_collection.find_one({"_id": dataset_id})
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    all_columns = dataset.get("columns", [])

    # Apply filtering if search is provided
    if search:
        filtered = [col for col in all_columns if search.lower()
                    in col.lower()]
        filtered = filtered[:10]
        return DatasetColumnsResponse(columns=filtered)
    return DatasetColumnsResponse(columns=all_columns[:10])
