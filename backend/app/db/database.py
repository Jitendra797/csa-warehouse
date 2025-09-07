import uuid 
from pymongo import MongoClient
from ..config.settings import get_database_settings

settings = get_database_settings()

# ------------------ MongoDB Setup ------------------
MONGO_URI = str(settings.mongodb_uri)
client = MongoClient(MONGO_URI)
db = client["fastapi_db"]

users_collection = db["users"]

# Collection for data from ERP and user 
datasets_collection = db["datasets"]

# Collection for dataset information 
dataset_information_collection = db["datasets_information"]

# Collection for files
files = db["files"]

# Collection for pipelines
pipelines_collection = db["pipelines"] 

# Pipeline statu
pipeline_status = db["pipeline_status"]