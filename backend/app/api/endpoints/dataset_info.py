from fastapi import APIRouter, HTTPException
from app.services.storage.mongodb_service import create_manual_dataset, get_data_from_collection
from app.schemas.models import (
    CreateDatasetInformationRequest,
    CreateDatasetInformationResponse,
    DatasetInformation
)
from datetime import datetime, timezone
from uuid import uuid4

dataset_info_router = APIRouter()

@dataset_info_router.post("/create-dataset-information", response_model = CreateDatasetInformationResponse)
async def create_dataset_information_endpoint(request: CreateDatasetInformationRequest):
    """
    Create a new dataset information entry in the datasets collection.
    
    This endpoint handles manual dataset creation (pulled_from_pipeline = False)
    and generates a new dataset_id for each dataset. 
    """
    try:
        # Generate new dataset_id since user doesn't provide it
        new_dataset_id = uuid4().hex
        
        # Create new dataset using the unified storage system
        result = create_manual_dataset(request, new_dataset_id)

        if result["success"]:
            # Create the response with the dataset information
            created_dataset_info = DatasetInformation(
                id = result["dataset_doc_id"],
                dataset_name = request.dataset_name,
                description = request.description,
                permission = request.permission,
                dataset_type = request.dataset_type,
                tags = request.tags,
                dataset_id = result["dataset_id"],
                file_id = request.file_id,
                is_temporal = request.is_temporal,
                is_spatial = request.is_spatial,
                pulled_from_pipeline = False,
                user_email = request.user_email,
                user_name = request.user_name,
                user_id = request.user_id,
                created_at = result["created_at"],
                updated_at = result["updated_at"],
                pipeline_id = request.pipeline_id
            )

            return CreateDatasetInformationResponse(
                status = "success",
                message = result["message"],
                data = created_dataset_info
            )
        else:
            raise HTTPException(
                status_code = 400,
                detail = result["message"]
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"Internal server error: {str(e)}"
        )

@dataset_info_router.get("/dataset/{dataset_id}")
async def get_dataset_info(dataset_id: str):
    try:
        dataset = get_data_from_collection(dataset_id = dataset_id)
        
        if not dataset or dataset == []:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )
        
        return {
            "status": "success",
            "data": dataset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )