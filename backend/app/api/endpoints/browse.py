from fastapi import APIRouter
from app.services.storage.mongodb_service import get_data_from_collection
from app.schemas.models import BrowseResponse 

browser_router = APIRouter()

@browser_router.get("/browse", response_model = BrowseResponse)
async def browse_datasets():
    data = get_data_from_collection()
    return {"data": data}
