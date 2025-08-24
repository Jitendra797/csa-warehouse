from typing import List, Optional, Union, Any
from uuid import UUID
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class Tag(BaseModel):
    """
    Tag object:
      - id: integer (int64)
      - name: string
    """
    id: int = Field(..., description="Unique identifier of the tag", example=123)
    name: str = Field(..., description="Name of the tag")


class PresignedURLRequest(BaseModel):
    """Request model for presigned URL generation"""
    filename: str = Field(..., description="Name of the file")
    user_id: str = Field(..., description="User ID")


class PresignedURLResponse(BaseModel):
    """Response model for presigned URL"""
    upload_url: str = Field(..., description="Presigned URL for upload")
    object_name: str = Field(..., description="Object name in storage")


class Browse(BaseModel):
    _id: str
    dataset_id: str
    dataset_name: str
    user_id: List[str]
    username: List[str]
    description: str
    created_at: datetime
    updated_at: datetime


class BrowseResponse(BaseModel):
    data: List[Browse]


class User(BaseModel):
    """
    User object.
    """
    id: UUID = Field(..., description="Unique user ID (UUID)")
    username: Optional[str] = Field(None, description="Username")
    firstName: Optional[str] = Field(None, description="First name of the user")
    lastName: Optional[str] = Field(None, description="Last name of the user")
    email: Optional[str] = Field(None, description="Email address", example="name@email.com")
    organisation: Optional[str] = Field(None, description="Organisation of the user")


class TemporalGranularity(str, Enum):
    YEAR = "year"
    MONTH = "month"
    DAY = "day"


class SpatialGranularity(str, Enum):
    COUNTRY = "country"
    STATE = "state"
    DISTRICT = "district"
    VILLAGE = "village"
    LAT_LONG = "lat_long"


class Dataset(BaseModel):
    """
    Dataset object.
    """
    id: Optional[int] = Field(..., description="Unique dataset ID (int)")
    title: str = Field(..., description="Title of the dataset", example="Soil Moisture Evolution in India")
    description: Optional[str] = Field(None, description="Text explaining what the dataset is about")
    uploader: User = Field(..., description="User who uploaded the dataset")
    uploadDate: datetime = Field(
        ...,
        description="The creation date and time in ISO 8601 format",
        example="2025-06-30T08:30:00Z"
    )
    tags: Optional[List[Tag]] = Field(None, description="List of tags associated with the dataset")
    isSpatial: bool = Field(..., description="Whether the dataset has any geospatial identifiers")
    isTemporal: bool = Field(..., description="Whether the dataset has any temporal identifiers")


class DatasetResponse(Dataset):
    document_id: str
    file_location: str


class DatasetInformation(BaseModel):
    """
    Complete dataset information object with all fields from datasets-information collection.
    """
    id: str = Field(..., description="Dataset information ID (UUID)")
    dataset_name: str = Field(..., description="Name of the dataset")
    description: Optional[str] = Field(None, description="Description of the dataset")
    permission: str = Field(..., description="Permission level of the dataset")
    dataset_type: str = Field(..., description="Type of the dataset")
    tags: List[str] = Field(default=[], description="Tags associated with the dataset")
    dataset_id: str = Field(..., description="Reference to the actual dataset UUID")
    file_id: Optional[str] = Field(None, description="File ID if applicable")
    is_temporal: bool = Field(..., description="Whether the dataset has temporal data")
    is_spatial: bool = Field(..., description="Whether the dataset has spatial data")
    pulled_from_pipeline: bool = Field(..., description="Whether the dataset was pulled from a pipeline")
    user_email: str = Field(..., description="Email of the user who owns the dataset")
    user_name: str = Field(..., description="Name of the user who owns the dataset")
    user_id: Optional[str] = Field(None, description="User ID (for backward compatibility)")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    pipeline_id: Optional[str] = Field(None, description="Pipeline ID that created this dataset")
    temporalGranularity: Optional[TemporalGranularity] = Field(None, description="Granularity of time data")
    spatialGranularity: Optional[SpatialGranularity] = Field(None, description="Granularity of spatial data")
    data: List 

class DatasetInformationResponse(BaseModel):
    """
    Response wrapper for dataset information.
    """
    status: str = Field(..., description="Response status")
    data: List[DatasetInformation] = Field(..., description="List of dataset information")


class Dataset(BaseModel):
    """
    Browse dataset response object with limited fields.
    """
    id: str = Field(..., description="Dataset ID")
    datasetname: str = Field(..., description="Name of the dataset")
    description: Optional[str] = Field(None, description="Description of the dataset")
    ingested_date: str = Field(..., description="Date when the dataset was ingested")
    user_name: str = Field(..., description="Name of the user who ingested the dataset")
    user_id: str = Field(..., description="ID of the user who ingested the dataset")


class GetDatasetsResponse(BaseModel):
    """
    Browse API response wrapper.
    """
    status: str = Field(..., description="Response status")
    data: List[Dataset] = Field(..., description="List of datasets")


class GetDatasetByIdRequest(BaseModel):
    """
    Request model for getting dataset rows with pagination.
    """
    dataset_id: str = Field(..., description="Dataset ID")
    page_number: int = Field(0, description="Page number (0-based)", ge=0)
    limit: int = Field(10, description="Number of rows to return", ge=1, le=1000)


class GetDatasetByIdResponse(BaseModel):
    """
    Response model for dataset rows with metadata.
    """
    status: str = Field(..., description="Response status")
    id: str = Field(..., description="Dataset ID")
    dataset_name: str = Field(..., description="Name of the dataset")
    description: Optional[str] = Field(None, description="Description of the dataset")
    ingested_time: str = Field(..., description="Time when the dataset was ingested")
    user_id: str = Field(..., description="ID of the user who ingested the dataset")
    user_name: str = Field(..., description="Name of the user who ingested the dataset")
    data_type: Optional[str] = Field(None, description="Type of the dataset")
    record_count: int = Field(..., description="Total number of records in the dataset")
    data: List[dict] = Field(..., description="Array of row objects")


class GetDatasetByIdDetailedResponse(BaseModel):
    """
    Detailed response model for dataset with complete information and paginated data.
    """
    status: str = Field(..., description="Response status")
    dataset_information: DatasetInformation = Field(..., description="Complete dataset information")
    record_count: int = Field(..., description="Total number of records in the dataset")
    data: List[dict] = Field(..., description="Array of row objects for current page")


class GetMyDatasetsRequest(BaseModel):
    """
    Request model for manage endpoint to get user's datasets.
    """
    user_email: str = Field(..., description="Email of the user whose datasets to retrieve")


class ManageDatasetResponse(BaseModel):
    """
    Manage dataset response object with limited fields.
    """
    id: str = Field(..., description="Dataset ID")
    datasetname: str = Field(..., description="Name of the dataset")
    description: Optional[str] = Field(None, description="Description of the dataset")
    ingested_date: str = Field(..., description="Date when the dataset was ingested")
    user_name: str = Field(..., description="Name of the user who ingested the dataset")
    user_id: str = Field(..., description="ID of the user who ingested the dataset")


class GetMyDatasetsResponse(BaseModel):
    """
    Manage API response wrapper.
    """
    status: str = Field(..., description="Response status")
    data: List[ManageDatasetResponse] = Field(..., description="List of datasets")


class CreateDatasetInformationRequest(BaseModel):
    dataset_name: str
    description: str
    permission: str
    dataset_type: str
    tags: Optional[List[str]] = None
    file_object: Optional[str]
    is_temporal: bool = False
    is_spatial: bool = False 
    pulled_from_pipeline: bool = False
    user_email: str
    user_name: str
    user_id: str
    pipeline_id: Optional[str] = None
    dataset_id: Optional[str] = None
    data: Optional[List] = None 


class CreateDatasetInformationResponse(BaseModel):
    """
    Response model for creating dataset information.
    """
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[DatasetInformation] = Field(None, description="Created dataset information")


class CreateFileRequest(BaseModel):
    """
    Request model for creating file information.
    """
    file_ext: str = Field(..., description="File extension")
    file_name: str = Field(..., description="Name of the file")
    file_size: int = Field(..., description="Size of the file in bytes")
    file_type: str = Field(..., description="MIME type of the file")
    file_url: str = Field(..., description="URL where the file is stored")


class FileInformation(BaseModel):
    """
    File information object with all fields from files collection.
    """
    id: str = Field(..., description="File ID (UUID)")
    file_ext: str = Field(..., description="File extension")
    file_name: str = Field(..., description="Name of the file")
    file_size: int = Field(..., description="Size of the file in bytes")
    file_type: str = Field(..., description="MIME type of the file")
    file_url: str = Field(..., description="URL where the file is stored")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class CreateFileResponse(BaseModel):
    """
    Response model for creating file information.
    """
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[FileInformation] = Field(None, description="Created file information")


class ExtractCsvDataResponse(BaseModel):
    """
    Response model for extract-csv-data endpoint.
    """
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Extraction result with dataset_id and columns")


class ApiResponse(BaseModel):
    """
    Generic API response.
    """
    code: Optional[int] = Field(None, description="Response code", example=200)
    type: Optional[str] = Field(None, description="Type of response")
    message: Optional[str] = Field(None, description="Message accompanying the response")


class Error(BaseModel):
    """
    Error response object.
    """
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class CloudFunctionRequest(BaseModel):
    func_name: str
    param_values: List[Any]


class RunPipelineRequest(BaseModel):
    pipeline_id: str
    pipeline_name: str
    username: str
    user_email: str


class PipelineStatusRequest(BaseModel):
    dataset_id: str
    exec_id: str


class RunPipelineResponse(BaseModel):
    """
    Response model for /run-pipeline endpoint
    """
    status: str = Field(..., description="The current status of the pipeline", enum=["running", "success", "failed"])
    executed_at: str
    user: str = Field(None, description="Username of the user who executed the pipeline", example="john_doe")


class HistoryItem(BaseModel):
    exec_id: str
    status: str
    executed_at: str
    user: str


class PipelineStatusResponse(BaseModel):
    """
    Response model for /pipeline-status endpoint
    """
    history: List[HistoryItem]


class PipelineRunResponse(BaseModel):
    """
    Response model for /run endpoint
    """
    status: str = Field(..., description="The current status of the pipeline", enum=["running", "completed", "error"])


class RequestGetPipelines(BaseModel):
    """
    Request model for getting pipelines.
    """
    pipeline: Optional[str] = Field(None, description="Pipeline name to filter by", example="Soil Collection Data")
    date: Optional[str] = Field(None, description="Date to filter by", example="2025-06-30")


class ResponseGetPipelines(BaseModel):
    """
    Response model for getting pipelines.
    """
    data: List[dict] = Field(..., description="List of pipelines with their details")