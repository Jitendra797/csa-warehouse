from fastapi import APIRouter
from datetime import datetime
from app.db.database import pipelines_collection
from app.schemas.models import (
    RunPipelineRequest,
    PipelineStatusResponse, RunPipelineResponse,
    ResponseGetPipelines
)
from app.services.tasks.task_executor import submit_task
from typing import Optional
from bson import ObjectId

run_router = APIRouter()


@run_router.post("/pipelines/run", response_model=RunPipelineResponse)
def run_pipeline(request: RunPipelineRequest) -> RunPipelineResponse:
    result, exec_id = submit_task(
        request.pipeline_id, request.pipeline_name, request.username, request.user_email)

    status = result.get("status", "running")
    executed_at = result.get("executed_at")
    user = result.get("user")

    return RunPipelineResponse(
        status=status,
        execution_id=exec_id,
        executed_at=executed_at,
        user=user
    )


@run_router.get("/pipeline/status", response_model=PipelineStatusResponse)
def get_pipeline_status(dataset_id: str, exec_id: Optional[str]) -> PipelineStatusResponse:
    dataset_object_id = ObjectId(dataset_id)
    pipeline = pipelines_collection.find_one({"_id": dataset_object_id})

    if not pipeline:
        return PipelineStatusResponse(status="No pipeline with given id")

    history = pipeline.get("history")
    if not history:
        return PipelineStatusResponse(status="No history for the pipeline")

    matching_history = [h for h in history if h["exec_id"] == exec_id]

    if not matching_history:
        return PipelineStatusResponse(status="No history is available with the given execution id")

    return PipelineStatusResponse(status=matching_history[0]["status"])


@run_router.get("/pipelines", response_model=ResponseGetPipelines)
def get_pipelines() -> ResponseGetPipelines:
    pipelines_cursor = pipelines_collection.find({})
    pipelines = []

    for doc in pipelines_cursor:
        pipelines.append({
            "_id": str(doc.get("_id")),
            "pipeline_name": doc.get("pipeline_name"),
            "history": doc.get("history", [])
        })

    return ResponseGetPipelines(data=pipelines)


@run_router.get("/pipelines/filter", response_model=ResponseGetPipelines)
def get_filtered_pipelines(pipeline: Optional[str], date: Optional[str]) -> ResponseGetPipelines:
    match_stage = {}
    if pipeline:
        match_stage["pipeline_name"] = {"$regex": pipeline, "$options": "i"}

    aggregation_pipeline = [{"$match": match_stage}]

    if date:
        try:
            # Ensure it's a proper ISO date string
            filter_date = datetime.fromisoformat(date).isoformat()
        except ValueError:
            filter_date = date  # fallback to string if parsing fails

        aggregation_pipeline.append(
            {"$addFields": {
                "history": {
                    "$filter": {
                        "input": "$history",
                        "as": "h",
                        "cond": {
                            "$gte": [
                                {"$toDate": "$$h.executed_at"},
                                {"$toDate": filter_date}
                            ]
                        }
                    }
                }
            }}
        )

    results = list(pipelines_collection.aggregate(aggregation_pipeline))
    return ResponseGetPipelines(data=results)
