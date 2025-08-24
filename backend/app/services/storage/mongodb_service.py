import math 
from uuid import uuid4
from datetime import datetime, timezone
import pandas as pd
from typing import List
from app.schemas.models import CreateDatasetInformationRequest
from app.db.database import datasets_collection

def store_to_mongodb(dataset_id: str, dataset_name: str, user_id: str, username: str, dataset_df: List[dict]) -> dict: 
    current_time = datetime.now(timezone.utc).isoformat()

    # Check if dataset already exists using dataset_id (not user-specific anymore)
    existing_doc = datasets_collection.find_one({"dataset_id": dataset_id})

    if existing_doc:
        # Prepare update operations
        update_ops = {
            "$set": {
                "record_count": len(dataset_df),
                "data": dataset_df,
                "updated_at": current_time,
                "pulled_from_pipeline": True
            }
        }
        
        # Add user_id and username to lists if they don't already exist
        if user_id not in existing_doc.get("user_id", []):
            update_ops["$addToSet"] = {
                "user_id": user_id,
                "username": username
            }
        
        # Update the document
        datasets_collection.update_one(
            {"_id": existing_doc["_id"]},
            update_ops
        )
        
        return {
            "id": str(existing_doc["_id"]),
            "user_id": user_id,
            "updated": True,
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "record_count": len(dataset_df),
            "created_at": existing_doc["created_at"] 
        }

    else:
        # Generate new document ID but use passed dataset_id
        new_doc_id = uuid4().hex
        
        # Insert as a new dataset with the updated schema
        wrapper_doc = {
            "_id": new_doc_id,
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "user_id": [user_id],
            "username": [username],
            "created_at": current_time,
            "updated_at": current_time,
            "record_count": len(dataset_df),
            "description": "",
            "tags": [],
            "permissions": "public",
            "dataset_type": "",
            "is_spatial": False,
            "is_temporal": False,
            "pulled_from_pipeline": False,
            "data": dataset_df,
        }

        datasets_collection.insert_one(wrapper_doc)

        return {
            "id": str(wrapper_doc["_id"]),
            "inserted": True,
            "inserted_at": current_time,
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "record_count": len(dataset_df),
            "created_at": wrapper_doc["created_at"] 
        }

def sanitize_document(doc):
    def sanitize_value(value):
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return None  # or use 0.0, depending on your use case
        elif isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(v) for v in value]
        return value

    doc["_id"] = str(doc["_id"])
    return {k: sanitize_value(v) for k, v in doc.items()}

def get_data_from_collection(collection = datasets_collection, dataset_id: str = None):
    try:
        if dataset_id:
            # Fetch the single dataset document
            doc = collection.find_one({"dataset_id": dataset_id})
            if not doc:
                return []

            doc = sanitize_document(doc)

            # Get first 10 rows from the data
            data_rows = doc.get("data", [])[:10]
            
            # Get first 10 columns from each row (if rows exist)
            limited_rows = []
            if data_rows:
                # Get all column names from first row
                all_columns = list(data_rows[0].keys()) if data_rows else []
                # Take only first 10 columns
                selected_columns = all_columns[:10]
                
                # Filter each row to only include selected columns
                for row in data_rows:
                    limited_row = {col: row.get(col) for col in selected_columns}
                    limited_rows.append(limited_row)

            return {
                "_id": doc["_id"],
                "dataset_id": doc.get("dataset_id"),
                "dataset_name": doc.get("dataset_name"),
                "user_id": doc.get("user_id"),
                "username": doc.get("username"),
                "description": doc.get("description", ""),
                "rows": limited_rows
            }

        else:
            # Get all dataset documents
            cursor = collection.find()
            documents = [sanitize_document(doc) for doc in cursor]

            return [
                {
                    "_id": doc["_id"],
                    "dataset_id": doc.get("dataset_id"),
                    "dataset_name": doc.get("dataset_name"),
                    "user_id": doc.get("user_id"),
                    "username": doc.get("username"),
                    "description": doc.get("description", ""),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at"),
                
                }
                for doc in documents
            ]

    except Exception as e:
        raise RuntimeError(f"Error fetching documents: {e}")
    
def create_manual_dataset(request: CreateDatasetInformationRequest, dataset_id: str) -> dict:
    """
    Create a new manual dataset using the unified storage system
    """
    try:
        current_time = datetime.now(timezone.utc).isoformat()
        new_doc_id = uuid4().hex
        
        # Create dataset document with manual creation flag
        dataset_doc = {
            "_id": new_doc_id,
            "dataset_id": dataset_id,
            "dataset_name": request.dataset_name,
            "user_id": [request.user_id],
            "username": [request.user_name],
            "user_email": [request.user_email],
            "created_at": current_time,
            "updated_at": current_time,
            "record_count": 0,
            "description": request.description,
            "tags": request.tags,
            "permissions": request.permission,
            "dataset_type": request.dataset_type,
            "is_spatial": request.is_spatial,
            "is_temporal": request.is_temporal,
            "pulled_from_pipeline": False,
            "file_id": request.file_id,
            "pipeline_id": request.pipeline_id,
            "data": [],
        }

        # Insert the document
        datasets_collection.insert_one(dataset_doc)

        return {
            "success": True,
            "dataset_doc_id": new_doc_id,
            "dataset_id": dataset_id,
            "message": "Dataset information created successfully",
            "created_at": current_time,
            "updated_at": current_time
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create dataset information: {str(e)}"
        }