from fastapi import APIRouter, HTTPException, Request, Header, Depends
from typing import List
from app.services.storage.mongodb_service import get_data_from_collection, get_dataset_card_info
from app.schemas.models import DatasetInfoResponse, BrowseResponse, ManageResponse
from app.auth.user_auth import get_current_user

dataset_info_router = APIRouter()


@dataset_info_router.get("/datasets", response_model=BrowseResponse, operation_id="get_datasets")
async def get_datasets(current_user: dict = Depends(get_current_user)) -> BrowseResponse:
    datasets = get_dataset_card_info()
    return BrowseResponse(data=datasets)


@dataset_info_router.get("/dataset", response_model=DatasetInfoResponse, operation_id="get_dataset_info")
async def get_dataset_info(id: str, current_user: dict = Depends(get_current_user)) -> DatasetInfoResponse:
    try:
        dataset = get_data_from_collection(dataset_id=id)
        if not dataset or dataset == []:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return DatasetInfoResponse(status="success", data=dataset)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@dataset_info_router.get("/user/datasets", response_model=ManageResponse)
async def get_user_datasets(fastapi_request: Request, authorization: str = Header(None)) -> ManageResponse:
    try:
        # Prefer external_id extracted by middleware; fallback to parsing Authorization header
        external_id = getattr(fastapi_request.state, "external_id", None)
        if not external_id and authorization:
            # Lazy import to avoid circular import at module level
            from app.api.endpoints.users.role_check import extract_user_id_from_token

            external_id = extract_user_id_from_token(authorization)

        if not external_id:
            raise HTTPException(
                status_code=401, detail="Missing external id from token")

        datasets = get_data_from_collection(user_id=external_id)
        return ManageResponse(data=datasets)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")
