from fastapi import APIRouter, HTTPException
from typing import List
from app.services.storage.mongodb_service import get_data_from_collection
from app.schemas.models import DatasetInfoResponse, BrowseResponse, ManageResponse

dataset_info_router = APIRouter()

@dataset_info_router.get("/datasets", response_model = BrowseResponse)
async def get_datasets() -> BrowseResponse:
    data = get_data_from_collection()
    # print(data)
    return BrowseResponse(data = data)

@dataset_info_router.get("/dataset", response_model = DatasetInfoResponse) 
async def get_dataset_info(id: str) -> DatasetInfoResponse:
    try:
        dataset = get_data_from_collection(dataset_id = id)
        
        if not dataset or dataset == []:
            raise HTTPException(
                status_code = 404,
                detail = "Dataset not found"
            )
        # print(dataset) 
        return DatasetInfoResponse(status = "success", data = dataset) 
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"Internal server error: {str(e)}"
        )
    
@dataset_info_router.get("/user/datasets", response_model = ManageResponse)
async def get_user_datasets(user_id: str) -> ManageResponse:
    try:
        datasets = get_data_from_collection(user_id = user_id)
        print(datasets)
        
        return ManageResponse(data = datasets) 

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"Internal server error: {str(e)}"
        )