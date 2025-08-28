from fastapi import APIRouter, HTTPException
from app.services.storage.mongodb_service import get_data_from_collection
from app.schemas.models import DatasetInfoResponse, BrowseResponse

dataset_info_router = APIRouter()

@dataset_info_router.get("/datasets", response_model = BrowseResponse)
async def get_datasets() -> BrowseResponse:
    data = get_data_from_collection()
    print(data)
    return BrowseResponse(data = data)

@dataset_info_router.get("/datasets/{dataset_id}", response_model = DatasetInfoResponse) 
async def get_dataset_info(dataset_id: str) -> DatasetInfoResponse:
    try:
        dataset = get_data_from_collection(dataset_id = dataset_id)
        
        if not dataset or dataset == []:
            raise HTTPException(
                status_code = 404,
                detail = "Dataset not found"
            )
        
        return DatasetInfoResponse(status = "success", data = dataset) 
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"Internal server error: {str(e)}"
        )