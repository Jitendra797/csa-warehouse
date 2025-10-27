from fastapi import HTTPException, Request
from app.db.crud import get_user_by_external_id
from app.db.database import users_collection
from bson import ObjectId


def get_current_user(request: Request):
    """Get current user from the JWT token via middleware"""
    external_id = getattr(request.state, "external_id", None)
    if not external_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user = get_user_by_external_id(external_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def get_user_details(user_id: str) -> dict:
    """Get user details by user ID from the database."""
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"first_name": "Unknown", "last_name": "User", "email": "unknown@example.com"}
        return {
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "email": user.get("email", "")
        }
    except Exception:
        # If ObjectId conversion fails or any other error
        return {"first_name": "Unknown", "last_name": "User", "email": "unknown@example.com"}
