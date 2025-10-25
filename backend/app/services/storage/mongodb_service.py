import math
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
from pymongo.collection import Collection
from bson import ObjectId
from app.schemas.models import CreateDatasetInformationRequest
from app.db.database import datasets_collection, dataset_information_collection, users_collection, pipelines_collection, pipelines_history_collection
from app.schemas.models import PipelineStatus


def get_user_info(user_id: str) -> Dict[str, str]:
    """
    Get user name and email from users collection

    Args:
        user_id: User ID to look up

    Returns:
        Dictionary with user_name and user_email
    """
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            first_name = user.get("first_name", "")
            last_name = user.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip(
            ) if first_name or last_name else ""
            return {
                "user_name": full_name,
                "user_email": user.get("email", "")
            }
        return {"user_name": "", "user_email": ""}
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return {"user_name": "", "user_email": ""}


def store_to_mongodb(
    dataset_id: str,
    dataset_name: str,
    user_id: str,
    username: str,
    user_email: str,
    dataset_records: List[Dict[str, Any]],
    pipeline_id: Optional[str] = None,
) -> Dict[str, Any]:
    current_time = datetime.now(timezone.utc).isoformat()

    # First check if dataset_id already exists in datasets_collection
    existing_data_doc = datasets_collection.find_one({"_id": dataset_id})

    if existing_data_doc:
        # Update existing dataset data
        columns = list(dataset_records[0].keys()) if dataset_records else []

        datasets_collection.update_one(
            {"_id": dataset_id},
            {"$set": {"data": dataset_records, "columns": columns,
                      "record_count": len(dataset_records), "updated_at": current_time}},
        )

        # Check if dataset information exists for this dataset_id
        existing_info = dataset_information_collection.find_one(
            {"dataset_id": dataset_id})

        if existing_info:
            # Update dataset information
            dataset_information_collection.update_one(
                {"_id": existing_info["_id"]}, {
                    "$set": {"updated_at": current_time, "pulled_from_pipeline": True}}
            )

            # Add user_id to array (using addToSet operation)
            if ObjectId(user_id) not in existing_info.get("user_id", []):
                dataset_information_collection.update_one(
                    {"_id": existing_info["_id"]}, {
                        "$addToSet": {"user_id": ObjectId(user_id)}}
                )
        else:
            # Create new dataset information document for existing data
            info_doc_id = ObjectId()
            dataset_info_doc = {
                "_id": info_doc_id,
                "dataset_name": dataset_name,
                # Reference to existing datasets_collection doc
                "dataset_id": ObjectId(dataset_id),
                "file_id": None,  # null for pipeline datasets
                "description": "",
                "tags": [],
                "dataset_type": "",
                "permissions": "public",
                "is_spatial": False,
                "is_temporal": False,
                "pulled_from_pipeline": True,
                "pipeline_id": ObjectId(pipeline_id) if pipeline_id else None,
                "created_at": current_time,
                "updated_at": current_time,
                "user_id": [ObjectId(user_id)],
            }
            dataset_information_collection.insert_one(dataset_info_doc)

        return {
            "id": str(dataset_id),
            "user_id": [user_id],
            "updated": True,
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "record_count": len(dataset_records),
            "created_at": existing_info["created_at"] if existing_info else current_time,
        }

    else:
        # Check if dataset information exists by name (in case dataset_id is new but name exists)
        existing_info = dataset_information_collection.find_one(
            {"dataset_name": dataset_name})

        if existing_info and existing_info["dataset_id"] != dataset_id:
            # Dataset name exists but with different ID - update the existing data document
            columns = list(dataset_records[0].keys()
                           ) if dataset_records else []

            datasets_collection.update_one(
                {"_id": existing_info["dataset_id"]},
                {"$set": {"data": dataset_records, "columns": columns,
                          "record_count": len(dataset_records), "updated_at": current_time}},
            )

            # Update information document
            dataset_information_collection.update_one(
                {"_id": existing_info["_id"]}, {
                    "$set": {"updated_at": current_time, "pulled_from_pipeline": True}}
            )

            # Add user_id only (no username or user_email)
            # $addToSet automatically prevents duplicates
            dataset_information_collection.update_one(
                {"_id": existing_info["_id"]}, {
                    "$addToSet": {"user_id": ObjectId(user_id)}}
            )

            return {
                "id": str(existing_info["dataset_id"]),
                "user_id": user_id,
                "updated": True,
                "dataset_id": existing_info["dataset_id"],
                "dataset_name": dataset_name,
                "record_count": len(dataset_records),
                "created_at": existing_info["created_at"],
            }
        else:
            # Create completely new dataset (both data and information)
            columns = list(dataset_records[0].keys()
                           ) if dataset_records else []

            dataset_doc = {
                "_id": ObjectId(dataset_id),  # Convert string to ObjectId
                "data": dataset_records,
                "columns": columns,
                "record_count": len(dataset_records),
                "created_at": current_time,
                "updated_at": current_time,
            }

            datasets_collection.insert_one(dataset_doc)

            # Create new dataset information document
            info_doc_id = ObjectId()

            dataset_info_doc = {
                "_id": info_doc_id,
                "dataset_name": dataset_name,
                "dataset_id": ObjectId(dataset_id),
                "file_id": None,  # null for pipeline datasets
                "description": "",
                "tags": [],
                "dataset_type": "",
                "permissions": "public",
                "is_spatial": False,
                "is_temporal": False,
                "temporal_granularities": [],
                "spatial_granularities": [],
                "location_columns": [],
                "time_columns": [],
                "pulled_from_pipeline": True,
                "pipeline_id": ObjectId(pipeline_id) if pipeline_id else None,
                "created_at": current_time,
                "updated_at": current_time,
                "user_id": [ObjectId(user_id)],
            }

            dataset_information_collection.insert_one(dataset_info_doc)

            return {
                "id": str(dataset_id),
                "inserted": True,
                "inserted_at": current_time,
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "record_count": len(dataset_records),
                "created_at": dataset_info_doc["created_at"],
            }


def sanitize_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    def sanitize_value(value: Any) -> Any:
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        if isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [sanitize_value(v) for v in value]
        return value

    doc["_id"] = str(doc["_id"])
    return {k: sanitize_value(v) for k, v in doc.items()}


def get_data_from_collection(
    dataset_id: Optional[str] = None, user_id: Optional[str] = None
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    try:
        if dataset_id:
            info_doc = dataset_information_collection.find_one(
                {"dataset_id": ObjectId(dataset_id)})
            if not info_doc:
                return {}

            if user_id and user_id not in info_doc.get("user_id", []):
                return {}

            data_doc = datasets_collection.find_one(
                {"_id": info_doc["dataset_id"]})
            data_rows: List[Dict[str, Any]] = []

            if data_doc and "data" in data_doc:
                rows = data_doc["data"][:10]
                if rows:
                    selected_columns = list(rows[0].keys())[:10]
                    for row in rows:
                        data_rows.append({col: row.get(col)
                                         for col in selected_columns})

            # Get user information from user_ids
            user_ids = info_doc.get("user_id", [])
            user_names = []
            user_emails = []

            for user_id in user_ids:
                user_info = get_user_info(user_id)
                if user_info.get("user_name"):
                    user_names.append(user_info["user_name"])
                if user_info.get("user_email"):
                    user_emails.append(user_info["user_email"])

            return {
                "dataset_name": info_doc.get("dataset_name", ""),
                "dataset_id": str(info_doc.get("dataset_id")),
                "file_id": str(info_doc.get("file_id", "")),
                "description": info_doc.get("description", ""),
                "tags": info_doc.get("tags", []),
                "dataset_type": info_doc.get("dataset_type", ""),
                "permissions": info_doc.get("permissions", ""),
                "is_spatial": info_doc.get("is_spatial", False),
                "is_temporal": info_doc.get("is_temporial", False),
                "temporal_granularities": info_doc.get("temporal_granularities", []),
                "spatial_granularities": info_doc.get("spatial_granularities", []),
                "location_columns": info_doc.get("location_columns", []),
                "time_columns": info_doc.get("time_columns", []),
                "pulled_from_pipeline": info_doc.get("pulled_from_pipeline", False),
                "created_at": info_doc.get("created_at"),
                "updated_at": info_doc.get("updated_at"),
                "user_names": user_names,
                "user_emails": user_emails,
                "rows": data_rows,
            }

        else:
            query = {}
            if user_id:
                query["user_id"] = user_id
                query["pulled_from_pipeline"] = False

            cursor = dataset_information_collection.find(query)
            info_documents = [sanitize_document(doc) for doc in cursor]

            results = []
            for doc in info_documents:
                data_doc = datasets_collection.find_one(
                    {"_id": doc["dataset_id"]})
                data_rows: List[Dict[str, Any]] = []

                if data_doc and "data" in data_doc:
                    rows = data_doc["data"][:10]
                    if rows:
                        selected_columns = list(rows[0].keys())[:10]
                        for row in rows:
                            data_rows.append({col: row.get(col)
                                             for col in selected_columns})

                # Get user information from user_ids
                user_ids = doc.get("user_id", [])
                user_names = []
                user_emails = []

                for user_id in user_ids:
                    user_info = get_user_info(user_id)
                    if user_info.get("user_name"):
                        user_names.append(user_info["user_name"])
                    if user_info.get("user_email"):
                        user_emails.append(user_info["user_email"])

                results.append(
                    {
                        "dataset_name": doc.get("dataset_name", ""),
                        "dataset_id": str(doc.get("dataset_id")),
                        "file_id": str(doc.get("file_id", "")),
                        "description": doc.get("description", ""),
                        "tags": doc.get("tags", []),
                        "dataset_type": doc.get("dataset_type", ""),
                        "permissions": doc.get("permissions", ""),
                        "is_spatial": doc.get("is_spatial", False),
                        "is_temporal": doc.get("is_temporial", False),
                        "temporal_granularities": doc.get("temporal_granularities", []),
                        "spatial_granularities": doc.get("spatial_granularities", []),
                        "location_columns": doc.get("location_columns", []),
                        "time_columns": doc.get("time_columns", []),
                        "pulled_from_pipeline": doc.get("pulled_from_pipeline", False),
                        "created_at": doc.get("created_at"),
                        "updated_at": doc.get("updated_at"),
                        "user_names": user_names,
                        "user_emails": user_emails,
                    }
                )
            print(results)
            return results

    except Exception as e:
        raise RuntimeError(f"Error fetching documents: {e}")


def get_dataset_card_info(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get dataset information optimized for dataset cards.
    Returns only the fields needed for DatasetCard component.

    Args:
        user_id: Optional user ID to filter datasets for specific user

    Returns:
        List of dictionaries containing only the fields needed for dataset cards
    """
    try:
        query = {}

        # Filter by user if user_id is provided
        if user_id:
            query["user_id"] = ObjectId(user_id)

        # Show both manual and pipeline datasets
        # query["pulled_from_pipeline"] = False  # Removed to show all datasets

        cursor = dataset_information_collection.find(query)
        info_documents = [sanitize_document(doc) for doc in cursor]

        results = []
        for doc in info_documents:
            # Get user details from user_id array
            user_ids = doc.get("user_id", [])
            user_emails = []
            user_names = []

            for user_id in user_ids:
                try:
                    user = users_collection.find_one(
                        {"_id": ObjectId(user_id)})
                    if user:
                        user_emails.append(user.get("email", ""))
                        first_name = user.get("first_name", "")
                        last_name = user.get("last_name", "")
                        full_name = f"{first_name} {last_name}".strip()
                        user_names.append(full_name)
                except Exception:
                    # Skip invalid user IDs
                    continue

            results.append({
                "dataset_id": str(doc.get("dataset_id", "")),
                "dataset_name": doc.get("dataset_name", ""),
                "description": doc.get("description", ""),
                "pulled_from_pipeline": doc.get("pulled_from_pipeline", False),
                "updated_at": doc.get("updated_at"),
                "user_emails": user_emails,
                "user_names": user_names,
            })

        return results

    except Exception as e:
        raise RuntimeError(f"Error fetching dataset card information: {e}")


def create_manual_dataset(request: CreateDatasetInformationRequest) -> Dict[str, Any]:
    try:
        current_time = datetime.now(timezone.utc).isoformat()

        # Create empty dataset data document first
        data_doc_id = ObjectId()
        dataset_doc = {
            "_id": data_doc_id,
            "data": [],
            "columns": [],
            "record_count": 0,
            "created_at": current_time,
            "updated_at": current_time
        }

        datasets_collection.insert_one(dataset_doc)

        # Create dataset information document
        info_doc_id = ObjectId()
        dataset_info_doc = {
            "_id": info_doc_id,
            "dataset_name": request.dataset_name,
            "dataset_id": ObjectId(data_doc_id),
            # ObjectId for manual datasets
            "file_id": ObjectId(request.file_id) if request.file_id else None,
            "description": request.description,
            "tags": request.tags,
            "dataset_type": request.dataset_type,
            "permissions": request.permission,
            "is_spatial": request.is_spatial,
            "is_temporal": request.is_temporal,
            "pulled_from_pipeline": False,
            "pipeline_id": None,  # null for manual datasets
            "created_at": current_time,
            "updated_at": current_time,
            "user_id": [ObjectId(request.user_id)],
        }

        # Insert the information document
        dataset_information_collection.insert_one(dataset_info_doc)

        return {
            "success": True,
            "dataset_doc_id": data_doc_id,
            "dataset_id": data_doc_id,
            "message": "Dataset information created successfully",
            "created_at": current_time,
            "updated_at": current_time,
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to create dataset information: {str(e)}"}


def get_pipelines() -> List[Dict[str, Any]]:
    """
    Get all pipelines with simplified fields for frontend consumption.
    Returns pipelines with id, pipeline_name, is_enabled, and pipeline_status.

    Returns:
        List of dictionaries containing pipeline information
    """
    try:
        existing_pipelines = pipelines_collection.find({})
        pipelines = []

        for doc in existing_pipelines:
            # Get the latest execution status from history
            history_array = doc.get("history", [])
            pipeline_status = PipelineStatus.NULL

            if history_array:
                # Get the most recent history entry
                latest_history = pipelines_history_collection.find_one(
                    {"_id": history_array[-1]}
                )
                if latest_history:
                    status = latest_history.get("status")
                    # Map database status to frontend status
                    if status == "running":
                        pipeline_status = PipelineStatus.RUNNING
                    elif status in ["completed", "success"]:
                        pipeline_status = PipelineStatus.COMPLETED
                    elif status == "failed":
                        pipeline_status = PipelineStatus.ERROR
                    else:
                        pipeline_status = PipelineStatus.NULL

            pipelines.append({
                "_id": str(doc.get("_id")),
                "pipeline_name": doc.get("pipeline_name"),
                "is_enabled": bool(doc.get("is_enabled", True)),
                "pipeline_status": pipeline_status
            })

        return pipelines

    except Exception as e:
        raise RuntimeError(f"Error fetching pipelines: {e}")
