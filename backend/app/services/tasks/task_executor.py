import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

from app.utils.erp import pull_dataset
from app.services.storage.mongodb_service import store_to_mongodb
from app.config.logging import LoggerMixin
from app.db.database import pipeline_status, datasets_collection, pipelines_collection

# In-memory store for task metadata
tasks: Dict[str, Dict[str, Any]] = {}

class TaskRunner(LoggerMixin):
    def run_pipeline_task(
        self, dataset_id: str, dataset_name: str, user_id: str, username: str, user_email: str, exec_id: str
    ) -> None:
        self.logger.info(f"[Thread: {threading.current_thread().name}] Starting task {exec_id} for dataset {dataset_id}")

        # Add initial "running" entry to pipeline history
        add_pipeline_history_entry(dataset_name, exec_id, "running", user_id)

        try:
            # Pull fresh dataset from ERP
            dataset = pull_dataset(dataset_name) 
            self.logger.info(f"[{exec_id}] Pulled dataset with {len(dataset)} records.")

            dataset_json = dataset.to_dict(orient="records")

            # Store/update dataset in MongoDB
            result = store_to_mongodb(dataset_id, dataset_name, user_id, username, user_email, dataset_json)
            
            # Get the actual dataset document ID from the result
            dataset_doc_id = result.get("id") 
            
            if result.get("updated"):
                self.logger.info(f"[{exec_id}] Updated existing dataset {dataset_id} with {len(dataset_json)} records.")
            elif result.get("inserted"):
                self.logger.info(f"[{exec_id}] Created new dataset {dataset_id} with {len(dataset_json)} records.")

            # Update in-memory status
            tasks[exec_id]["status"] = "completed"

            # Always create/update pipeline status using the dataset document ID
            pipeline_status.update_one(
                {"_id": dataset_doc_id},
                {
                    "$set": {
                        "_id": dataset_doc_id,
                        "dataset_id": dataset_id,
                        "name": dataset_name,
                        "user_id": user_id,
                        "user_name": username,
                        "user_email": user_email,
                        "exec_id": exec_id,
                        "status": "completed"
                    }
                },
                upsert=True
            )

            # Add "completed" entry to pipeline history
            add_pipeline_history_entry(dataset_name, exec_id, "completed", user_id)

        except Exception as e:
            self.logger.error(f"[{exec_id}] Task failed with error: {e}", exc_info=True)

            # Update in-memory status
            tasks[exec_id]["status"] = "error"

            # Add "failed" entry to pipeline history
            add_pipeline_history_entry(dataset_name, exec_id, "failed", user_id)


def add_pipeline_history_entry(pipeline_name: str, exec_id: str, status: str, user_id: str):
    try:
        current_time = datetime.now(timezone.utc).isoformat()

        # Check if pipeline exists
        existing_pipeline = pipelines_collection.find_one({"pipeline_name": pipeline_name})

        if existing_pipeline:
            # Check if exec_id already exists in history
            pipelines_collection.update_one(
                {"pipeline_name": pipeline_name, "history.exec_id": exec_id},
                {
                    "$set": {
                        "history.$.status": status,
                        "history.$.executed_at": current_time,
                        "history.$.user": user_id
                    }
                }
            )

            # If no existing exec_id found, push new history entry
            pipelines_collection.update_one(
                {"pipeline_name": pipeline_name, "history.exec_id": {"$ne": exec_id}},
                {
                    "$push": {
                        "history": {
                            "exec_id": exec_id,
                            "status": status,
                            "user": user_id,
                            "executed_at": current_time
                        }
                    }
                }
            )
        else:
            # Create new pipeline with first history entry
            pipelines_collection.insert_one({
                "_id": uuid.uuid4().hex,
                "pipeline_name": pipeline_name,
                "history": [{
                    "exec_id": exec_id,
                    "status": status,
                    "user": user_id,
                    "executed_at": current_time
                }]
            })

    except Exception as e:
        print(f"Error adding pipeline history entry: {e}")

task_runner = TaskRunner()

def submit_task(dataset_id: str, dataset_name: str, user_id: str, username: str, user_email: str) -> Tuple[dict, str]:
    exec_id = str(uuid.uuid4())
    current_time = datetime.now(timezone.utc).isoformat()

    # Check if dataset already exists
    existing_dataset = datasets_collection.find_one({"dataset_id": dataset_id})
    
    if existing_dataset:
        # Set pipeline status to running for existing dataset
        pipeline_status.update_one(
            {"_id": existing_dataset["_id"]},
            {
                "$set": {
                    "_id": existing_dataset["_id"],
                    "dataset_id": dataset_id,
                    "name": dataset_name,
                    "user_id": user_id,  
                    "user_name": username,
                    "user_email": user_email,
                    "exec_id": exec_id,
                    "status": "running"
                }
            },
            upsert=True
        )

    tasks[exec_id] = {
        "status": "running",
        "executed_at": current_time,
        "user_id": user_id,
        "user_name": username,
        "user_email": user_email
    }

    # Run task in background thread
    thread = threading.Thread(
        target=task_runner.run_pipeline_task,
        args=(dataset_id, dataset_name, user_id, username, user_email, exec_id),
        name=f"TaskThread-{exec_id[:8]}"
    )
    thread.start()

    return tasks[exec_id], exec_id


def get_task_status(dataset_id: str, user_id: str) -> Dict[str, Any]:
    dataset_doc = datasets_collection.find_one({"dataset_id": dataset_id})
    
    if not dataset_doc:
        return {
            "status": "not found",
            "message": "No dataset found with this ID."
        }
    
    # Check if the requesting user matches the dataset owner
    if dataset_doc.get("user_id") != user_id:
        return {
            "status": "not authorized",
            "message": "You don't have access to this dataset."
        }
    
    result = pipeline_status.find_one({"_id": dataset_doc["_id"]})
    if not result:
        return {
            "status": "not found",
            "message": "No pipeline status found for this dataset."
        }

    return {
        "exec_id": result.get("exec_id"),
        "status": result.get("status", "unknown")
    }


def get_user_datasets(user_id: str) -> Dict[str, Any]:
    """
    Get all datasets that a specific user owns
    """
    try:
        cursor = datasets_collection.find({"user_id": user_id})
        
        documents = []
        for doc in cursor:
            documents.append({
                "_id": str(doc["_id"]),
                "dataset_id": doc.get("dataset_id"),
                "dataset_name": doc.get("dataset_name"),
                "user_id": doc.get("user_id"),
                "user_name": doc.get("user_name"),
                "user_email": doc.get("user_email"),
                "description": doc.get("description", ""),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
                "record_count": doc.get("record_count", 0),
                "pulled_from_pipeline": doc.get("pulled_from_pipeline", False)
            })
        
        return {"datasets": documents}
        
    except Exception as e:
        raise RuntimeError(f"Error fetching user datasets: {e}")
