import uuid 
import requests
import mimetypes
import pandas as pd
from io import BytesIO
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.schemas.models import CreateDatasetInformationRequest, CreateDatasetInformationResponse, PresignedURLRequest, DatasetInformation, PresignedURLResponse
from app.services.storage.mongodb_service import get_data_from_collection, store_to_mongodb
from app.services.storage.minio_service import get_minio_service

datasets_router = APIRouter()

@datasets_router.get("/presignedURL", response_model = PresignedURLResponse)
def get_presigned_url(request: PresignedURLRequest) -> PresignedURLResponse:
    minio_service = get_minio_service()
    url, object_name = minio_service.generate_presigned_url(filename = request.filename, user_id = request.user_id)
    return PresignedURLResponse(upload_url = url, object_name = object_name)

# Dummy api just to test the backend upload and create api
@datasets_router.post("/upload")
async def upload_file(request: PresignedURLRequest):
    try:
        minio_service = get_minio_service()
        upload_url, object_name = minio_service.generate_presigned_url(
            filename=request.filename, user_id=request.user_id
        )

        # Read the file (local file example)
        file_path = "/workspaces/warehouse/csa-warehouse/backend/test.csv"
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Upload via presigned URL (blocking)
        put_resp = requests.put(upload_url, data=file_content)
        if put_resp.status_code not in [200, 201]:
            raise HTTPException(status_code=500, detail="Failed to upload to MinIO")

        return {
            "status": "success",
            "message": f"File '{file_path}' uploaded via presigned URL",
            "object_name": object_name,
            "user_id": request.user_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
@datasets_router.post("/create", response_model = CreateDatasetInformationResponse)
async def create_dataset(request: CreateDatasetInformationRequest) -> CreateDatasetInformationResponse:
    try:
        new_dataset_id = uuid.uuid4().hex
        minio_service = get_minio_service() 

        # Pull file from MinIO 
        response = minio_service.get_object(
            object_name = request.file_object 
        )
        if not response:
            raise {
                "Error": "File not Found"
            }
        
        file_content = response.read()
        file_type = mimetypes.guess_type(request.file_object)[0] or "application/octet-stream"
        response.close()
        response.release_conn() 
    
        df = pd.read_csv(BytesIO(file_content)) 
        dataset_records = df.to_dict(orient = "records")

        mongo_result = store_to_mongodb(
            dataset_id = new_dataset_id, 
            dataset_name = request.dataset_name,
            user_id = request.user_id,
            username = request.user_name,
            dataset_df = dataset_records
        )

        # Build DatasetInformation object for response
        created_dataset_info = DatasetInformation(
            id = mongo_result["id"],
            dataset_name = request.dataset_name,
            description = request.description,
            permission = request.permission,
            dataset_type = request.dataset_type,
            tags = request.tags,
            dataset_id = new_dataset_id,
            is_temporal = request.is_temporal,
            is_spatial = request.is_spatial,
            pulled_from_pipeline = False,
            user_email = request.user_email,
            user_name = request.user_name,
            user_id = request.user_id,
            created_at = mongo_result["created_at"],
            updated_at = mongo_result["inserted_at"],
            data = dataset_records
        )

        return CreateDatasetInformationResponse(
            status  ="success",
             message = "Error",
            data = created_dataset_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )