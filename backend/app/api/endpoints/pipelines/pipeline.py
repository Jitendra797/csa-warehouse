from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from app.db.database import pipelines_collection, pipelines_history_collection, users_collection
from app.services.storage.mongodb_service import get_pipelines
from app.schemas.models import RunPipelineRequest, PipelineStatus, RunPipelineResponse, GetPipelinesResponse
from app.services.tasks.task_executor import submit_task
from app.auth.user_auth import get_current_user, get_user_details
from typing import Optional
from bson import ObjectId

run_router = APIRouter()


@run_router.get("/pipelines", response_model=GetPipelinesResponse, operation_id="get_pipelines")
def get_pipelines_endpoint(current_user: dict = Depends(get_current_user)) -> GetPipelinesResponse:
    pipelines = get_pipelines()
    return GetPipelinesResponse(data=pipelines)


@run_router.post("/pipelines/run", response_model=RunPipelineResponse, operation_id="run_pipeline")
def run_pipeline(request: RunPipelineRequest, fastapi_request: Request, current_user: dict = Depends(get_current_user)) -> RunPipelineResponse:
    result, exec_id = submit_task(
        dataset_id=request.pipeline_id,
        dataset_name=request.pipeline_name,
        user_id=str(current_user.get("_id")),
        pipeline_id=request.pipeline_id,
    )
    status = result.get("status", "running")
    executed_at = result.get("executed_at")
    return RunPipelineResponse(status=status, execution_id=exec_id, executed_at=executed_at)


@run_router.get("/pipeline/status", response_model=PipelineStatus, operation_id="get_pipeline_status")
def get_pipeline_status(pipeline_id: str, execution_id: str, current_user: dict = Depends(get_current_user)) -> PipelineStatus:
    pipeline = pipelines_collection.find_one({"_id": ObjectId(pipeline_id)})

    if not pipeline:
        raise HTTPException(
            status_code=404, detail="No pipeline with the given pipeline_id")
    history_doc = pipelines_history_collection.find_one({
        "execution_id": execution_id
    })

    if not history_doc:
        raise HTTPException(
            status_code=404, detail="No history available with the given execution_id")

    status = history_doc["status"]
    return status


@run_router.get("/pipelines/filter", response_model=GetPipelinesResponse)
def get_filtered_pipelines(pipeline: Optional[str], date: Optional[str]) -> GetPipelinesResponse:
    match_stage = {}
    if pipeline:
        match_stage["pipeline_name"] = {"$regex": pipeline, "$options": "i"}

    # Get filtered pipelines
    pipelines_cursor = pipelines_collection.find(match_stage)
    pipelines = []

    for doc in pipelines_cursor:
        # Get history from pipelines_history collection
        history_ids = doc.get("history_ids", [])
        history = []

        for history_id in history_ids:
            # history_id is now an ObjectId, use it directly
            history_doc = pipelines_history_collection.find_one(
                {"_id": history_id})
            if history_doc:
                # Apply date filter if provided
                if date:
                    try:
                        filter_date = datetime.fromisoformat(date).isoformat()
                        if history_doc.get("created_at") >= filter_date:
                            user_details = get_user_details(
                                history_doc.get("user_id"))
                            history.append({
                                "_id": str(history_doc.get("_id")),
                                "exec_id": history_doc.get("exec_id"),
                                "status": history_doc.get("status"),
                                "first_name": user_details["first_name"],
                                "last_name": user_details["last_name"],
                                "email": user_details["email"],
                                "created_at": history_doc.get("created_at"),
                                "updated_at": history_doc.get("updated_at")
                            })
                    except ValueError:
                        # If date parsing fails, include all history
                        user_details = get_user_details(
                            history_doc.get("user_id"))
                        history.append({
                            "_id": str(history_doc.get("_id")),
                            "exec_id": history_doc.get("exec_id"),
                            "status": history_doc.get("status"),
                            "first_name": user_details["first_name"],
                            "last_name": user_details["last_name"],
                            "email": user_details["email"],
                            "created_at": history_doc.get("created_at"),
                            "updated_at": history_doc.get("updated_at")
                        })
                else:
                    user_details = get_user_details(history_doc.get("user_id"))
                    history.append({
                        "_id": str(history_doc.get("_id")),
                        "exec_id": history_doc.get("exec_id"),
                        "status": history_doc.get("status"),
                        "first_name": user_details["first_name"],
                        "last_name": user_details["last_name"],
                        "email": user_details["email"],
                        "created_at": history_doc.get("created_at"),
                        "updated_at": history_doc.get("updated_at")
                    })

        pipelines.append(
            {
                "_id": str(doc.get("_id")),
                "pipeline_name": doc.get("pipeline_name"),
                "is_enabled": doc.get("is_enabled", True),
                "history_ids": [str(hid) for hid in doc.get("history_ids", [])],
                "history": history
            }
        )

    return GetPipelinesResponse(data=pipelines)
