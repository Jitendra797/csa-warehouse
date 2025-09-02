import math 
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
from pymongo.collection import Collection
from app.schemas.models import CreateDatasetInformationRequest
from app.db.database import datasets_collection, dataset_information_collection

def store_to_mongodb(dataset_id: str, dataset_name: str, user_id: str, username: str, user_email: str, dataset_records: List[Dict[str, Any]]) -> Dict[str, Any]: 
    current_time = datetime.now(timezone.utc).isoformat()

    # First check if dataset_id already exists in datasets_collection
    existing_data_doc = datasets_collection.find_one({"_id": dataset_id})
    
    if existing_data_doc:
        # Update existing dataset data
        columns = list(dataset_records[0].keys()) if dataset_records else []
        
        datasets_collection.update_one(
            {"_id": dataset_id},
            {
                "$set": {
                    "data": dataset_records,
                    "columns": columns,
                    "record_count": len(dataset_records)
                }
            }
        )
        
        # Check if dataset information exists for this dataset_id
        existing_info = dataset_information_collection.find_one({"dataset_id": dataset_id})
        
        if existing_info:
            # Update dataset information 
            dataset_information_collection.update_one(
                {"_id": existing_info["_id"]},
                {
                    "$set": {
                        "updated_at": current_time,
                        "pulled_from_pipeline": True
                    }
                }
            )
            
            # Add user_id, username, and email to arrays (using separate addToSet operations)
            if user_id not in existing_info.get("user_id", []):
                dataset_information_collection.update_one(
                    {"_id": existing_info["_id"]},
                    {"$addToSet": {"user_id": user_id}}
                )
            if username not in existing_info.get("username", []):
                dataset_information_collection.update_one(
                    {"_id": existing_info["_id"]},
                    {"$addToSet": {"username": username}}
                )
            if user_email and user_email not in existing_info.get("user_email", []):
                dataset_information_collection.update_one(
                    {"_id": existing_info["_id"]},
                    {"$addToSet": {"user_email": user_email}}
                )
        else:
            # Create new dataset information document for existing data
            info_doc_id = uuid4().hex
            dataset_info_doc = {
                "_id": info_doc_id,
                "dataset_name": dataset_name,
                "dataset_id": dataset_id,  # Reference to existing datasets_collection doc
                "file_id": "",
                "description": "",
                "tags": [],
                "dataset_type": "",
                "permissions": "public",
                "is_spatial": False,
                "is_temporal": False,
                "pulled_from_pipeline": True,
                "created_at": current_time,
                "updated_at": current_time,
                "user_id": [user_id],
                "user_name": [username],
                "user_email": [user_email] if user_email else []
            }
            dataset_information_collection.insert_one(dataset_info_doc)
        
        return {
            "id": str(dataset_id),
            "user_id": [user_id],
            "updated": True,
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "record_count": len(dataset_records),
            "created_at": existing_info["created_at"] if existing_info else current_time
        }

    else:
        # Check if dataset information exists by name (in case dataset_id is new but name exists)
        existing_info = dataset_information_collection.find_one({"dataset_name": dataset_name})
        
        if existing_info and existing_info["dataset_id"] != dataset_id:
            # Dataset name exists but with different ID - update the existing data document
            columns = list(dataset_records[0].keys()) if dataset_records else []
            
            datasets_collection.update_one(
                {"_id": existing_info["dataset_id"]},
                {
                    "$set": {
                        "data": dataset_records,
                        "columns": columns,
                        "record_count": len(dataset_records)
                    }
                }
            )
            
            # Update information document
            dataset_information_collection.update_one(
                {"_id": existing_info["_id"]},
                {
                    "$set": {
                        "updated_at": current_time,
                        "pulled_from_pipeline": True
                    }
                }
            )
            
            # Add user info using separate addToSet operations
            if user_id not in existing_info.get("user_id", []):
                dataset_information_collection.update_one(
                    {"_id": existing_info["_id"]},
                    {"$addToSet": {"user_id": user_id}}
                )
            if username not in existing_info.get("username", []):
                dataset_information_collection.update_one(
                    {"_id": existing_info["_id"]},
                    {"$addToSet": {"username": username}}
                )
            if user_email and user_email not in existing_info.get("user_email", []):
                dataset_information_collection.update_one(
                    {"_id": existing_info["_id"]},
                    {"$addToSet": {"user_email": user_email}}
                )
            
            return {
                "id": str(existing_info["dataset_id"]),
                "user_id": user_id,
                "updated": True,
                "dataset_id": existing_info["dataset_id"],
                "dataset_name": dataset_name,
                "record_count": len(dataset_records),
                "created_at": existing_info["created_at"]
            }
        else:
            # Create completely new dataset (both data and information)
            columns = list(dataset_records[0].keys()) if dataset_records else []
            
            dataset_doc = {
                "_id": dataset_id,  # Use the provided dataset_id
                "data": dataset_records,
                "columns": columns,
                "record_count": len(dataset_records)
            }
            
            datasets_collection.insert_one(dataset_doc)

            # Create new dataset information document
            info_doc_id = uuid4().hex
            
            dataset_info_doc = {
                "_id": info_doc_id,
                "dataset_name": dataset_name,
                "dataset_id": dataset_id,
                "file_id": "",
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
                "created_at": current_time,
                "updated_at": current_time,
                "user_id": [user_id],
                "user_name": [username],
                "user_email": [user_email] if user_email else []
            }

            dataset_information_collection.insert_one(dataset_info_doc)

            return {
                "id": str(dataset_id),
                "inserted": True,
                "inserted_at": current_time,
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "record_count": len(dataset_records),
                "created_at": dataset_info_doc["created_at"] 
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

def get_data_from_collection(dataset_id: Optional[str] = None, user_id: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    try:
        if dataset_id:
            info_doc = dataset_information_collection.find_one({"dataset_id": dataset_id})
            if not info_doc:
                return {}

            if user_id and user_id not in info_doc.get("user_id", []):
                return {}

            data_doc = datasets_collection.find_one({"_id": info_doc["dataset_id"]})
            data_rows: List[Dict[str, Any]] = []

            if data_doc and "data" in data_doc:
                rows = data_doc["data"][:10]
                if rows:
                    selected_columns = list(rows[0].keys())[:10]
                    for row in rows:
                        data_rows.append({col: row.get(col) for col in selected_columns})

            return {
                "dataset_name": info_doc.get("dataset_name", ""),
                "dataset_id": info_doc.get("dataset_id"),
                "file_id": info_doc.get("file_id", ""),
                "description": info_doc.get("description", ""),
                "tags": info_doc.get("tags", []),
                "dataset_type": info_doc.get("dataset_type", ""),
                "permissions": info_doc.get("permissions", ""),
                "is_spatial": info_doc.get("is_spatial", False),
                "is_temporial": info_doc.get("is_temporial", False),
                "temporal_granularities": info_doc.get("temporal_granularities", []), 
                "spatial_granularities": info_doc.get("spatial_granularities", []),
                "location_columns": info_doc.get("location_columns", []), 
                "time_columns": info_doc.get("time_columns", []),
                "pulled_from_pipeline": info_doc.get("pulled_from_pipeline", False),
                "created_at": info_doc.get("created_at"),
                "updated_at": info_doc.get("updated_at"),
                "user_id": info_doc.get("user_id") or [],
                "user_name": info_doc.get("user_name") or [],
                "user_email": info_doc.get("user_email") or [],
                "rows": data_rows
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
                data_doc = datasets_collection.find_one({"_id": doc["dataset_id"]})
                data_rows: List[Dict[str, Any]] = []

                if data_doc and "data" in data_doc:
                    rows = data_doc["data"][:10]
                    if rows:
                        selected_columns = list(rows[0].keys())[:10]
                        for row in rows:
                            data_rows.append({col: row.get(col) for col in selected_columns})

                results.append({
                    "dataset_name": doc.get("dataset_name", ""),
                    "dataset_id": doc.get("dataset_id"),
                    "file_id": doc.get("file_id", ""),
                    "description": doc.get("description", ""),
                    "tags": doc.get("tags", []),
                    "dataset_type": doc.get("dataset_type", ""),
                    "permissions": doc.get("permissions", ""),
                    "is_spatial": doc.get("is_spatial", False),
                    "is_temporial": doc.get("is_temporial", False),
                    "pulled_from_pipeline": doc.get("pulled_from_pipeline", False),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at"),
                    "user_id": doc.get("user_id") or [],
                    "user_name": doc.get("user_name") or [],
                    "user_email": doc.get("user_email") or [],
                    # "rows": data_rows
                })
            print(results) 
            return results

    except Exception as e:
        raise RuntimeError(f"Error fetching documents: {e}")
    
def create_manual_dataset(request: CreateDatasetInformationRequest) -> Dict[str, Any]:
    try:
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Create empty dataset data document first
        data_doc_id = uuid4().hex
        dataset_doc = {
            "_id": data_doc_id,
            "data": [],
            "columns": [],
            "record_count": 0
        }
        
        datasets_collection.insert_one(dataset_doc)
        
        # Create dataset information document
        info_doc_id = uuid4().hex
        dataset_info_doc = {
            "_id": info_doc_id,
            "dataset_name": request.dataset_name,
            "dataset_id": data_doc_id,
            "file_id": request.file_id,
            "description": request.description,
            "tags": request.tags,
            "dataset_type": request.dataset_type,
            "permissions": request.permission,
            "is_spatial": request.is_spatial,
            "is_temporal": request.is_temporal,
            "pulled_from_pipeline": False,
            "created_at": current_time,
            "updated_at": current_time,
            "user_id": [request.user_id],
            "user_name": [request.user_name],
            "user_email": [request.user_email]
        }

        # Insert the information document
        dataset_information_collection.insert_one(dataset_info_doc)

        return {
            "success": True,
            "dataset_doc_id": data_doc_id,
            "dataset_id": data_doc_id,
            "message": "Dataset information created successfully",
            "created_at": current_time,
            "updated_at": current_time
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create dataset information: {str(e)}"
        }