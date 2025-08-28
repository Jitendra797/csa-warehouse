from uuid import UUID
from fastapi import FastAPI, HTTPException
from app.schemas.models import User, Dataset, ApiResponse
from app.db.crud import (
    create_user, get_user, update_user, delete_user,
)

app = FastAPI 


@app.post("/users/", response_model = ApiResponse)
def create_user_endpoint(user: User):
    create_user(user)
    return ApiResponse(code=201, type="success", message="User created")


@app.get("/users/{user_id}")
def get_user_endpoint(user_id: UUID):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=ApiResponse)
def update_user_endpoint(user_id: UUID, user: User):
    modified = update_user(user_id, user.model_dump(exclude={"id"}))
    if modified == 0:
        raise HTTPException(
            status_code=404, detail="User not found or unchanged")
    return ApiResponse(code=200, type="success", message="User updated")


@app.delete("/users/{user_id}", response_model=ApiResponse)
def delete_user_endpoint(user_id: UUID):
    deleted = delete_user(user_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return ApiResponse(code=200, type="success", message="User deleted")
