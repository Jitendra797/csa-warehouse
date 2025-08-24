from fastapi import APIRouter
from datetime import datetime 
from app.utils.erp import pull_dataset
from app.db.database import pipelines_collection
from app.schemas.models import PipelineStatusRequest, RunPipelineRequest, PipelineStatusResponse, RunPipelineResponse, RequestGetPipelines, ResponseGetPipelines
from app.services.storage.mongodb_service import store_to_mongodb
from app.services.tasks.task_executor import submit_task, get_task_status

run_router = APIRouter()

@run_router.post("/run", response_model=RunPipelineResponse)
async def run_pipeline(request: RunPipelineRequest):
    dataset = pull_dataset(request.pipeline_id)
    dataset_json = dataset.to_dict(orient="records")
    result = store_to_mongodb(
        request.pipeline_id, request.username, request.user_email, dataset_json)
    return RunPipelineResponse(status="completed")

@run_router.post("/run-pipeline", response_model=RunPipelineResponse)
def run_pipeline(request: RunPipelineRequest):
    result, exec_id = submit_task(request.pipeline_id, request.pipeline_name, request.username, request.user_email)
    print(result)  

    # Map "not found" to "error" for frontend compatibility
    status = result.get("status", "running")
    executed_at = result.get("executed_at") 
    user = result.get("user")  
    
    if status == "not found":
        status = "error"

    return RunPipelineResponse(status = status, executed_at = executed_at, user = user) 

@run_router.post("/pipeline-status", response_model = PipelineStatusResponse)
def get_pipeline_status(request: PipelineStatusRequest):
    pipeline = pipelines_collection.find_one({"_id": request.dataset_id})
    if not pipeline: 
        return PipelineStatusResponse(history = [])

    history = pipeline.get("history", [])
    if not history:
        return PipelineStatusResponse(history = [])

    matching = [h for h in history if h["exec_id"] == request.exec_id]

    return PipelineStatusResponse(history = matching) 

@run_router.get("/pipeline", response_model = ResponseGetPipelines) 
def get_pipeline():
    pipelines = pipelines_collection.find({}) 

    return ResponseGetPipelines(data = list(pipelines))  
     
@run_router.post("/filter-pipelines", response_model = ResponseGetPipelines)
def filter_pipelines(request: RequestGetPipelines):
    match_stage = {}
    if request.pipeline:
        match_stage["pipeline_name"] = {"$regex": request.pipeline, "$options": "i"}

    pipeline = [
        {"$match": match_stage},
    ]

    if request.date:
        pipeline.append(
            {"$addFields": {
                "history": {
                    "$filter": {
                        "input": "$history",
                        "as": "h",
                        "cond": {"$gte": ["$$h.executed_at", request.date]}
                    }
                }
            }}
        )

    results = list(pipelines_collection.aggregate(pipeline))
    return ResponseGetPipelines(data=results)