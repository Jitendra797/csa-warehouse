from fastapi import APIRouter, HTTPException
import traceback
from app.schemas.models import CreateUserFromOAuth, UserResponse
from app.db.crud import find_or_create_user_from_oauth

router = APIRouter()


@router.post("/users/oauth/sync", response_model=UserResponse)
def sync_user_from_oauth(user_data: CreateUserFromOAuth):
    try:
        user = find_or_create_user_from_oauth(user_data)
        return UserResponse(
            id=user.get("_id"),
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            email=user.get("email"),
            phone=user.get("phone"),
            external_id=user.get("external_id", ""),
            role_id=user.get("role_id"),
            created_at=user.get("created_at"),
            updated_at=user.get("updated_at"),
        )
    except Exception as e:
        print("sync_user_from_oauth error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to sync user: {str(e)}")
