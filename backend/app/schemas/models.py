from typing import List, Optional, Dict, Any, Literal
from uuid import UUID
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

# --------------------------------- /datasets ---------------------------------


class DatasetInfo(BaseModel):
    """Schema representing a single dataset entry"""
    dataset_id: str = Field(...,
                            description="Unique identifier for the dataset")
    dataset_name: str = Field(..., description="Name of the dataset")
    file_id: str = Field(..., description="ID of the file in storage")
    description: str = Field(..., description="Description about the dataset")
    tags: List[str] = Field(...,
                            description="List of tags associated with the dataset")
    dataset_type: str = Field(..., description="Type of the dataset")
    permissions: str = Field(...,
                             description="Permissions associated with the dataset")
    is_spatial: bool = Field(...,
                             description="Whether the dataset has spatial data")
    is_temporial: bool = Field(...,
                               description="Whether the dataset has temporal data")
    pulled_from_pipeline: bool = Field(
        ..., description="Whether dataset is pulled from a pipeline")
    created_at: datetime = Field(...,
                                 description="Timestamp when the dataset is created")
    updated_at: datetime = Field(...,
                                 description="Timestamp when the dataset was updated")
    user_id: List[str] = Field(...,
                               description="List of user IDs associated with the dataset")
    user_name: List[str] = Field(...,
                                 description="List of usernames associated with the dataset")
    user_email: List[str] = Field(
        ..., description="List of user emails associated with the dataset")


class BrowseResponse(BaseModel):
    """Schema representing the response returned when browsing datasets"""
    data: List[DatasetInfo]


class ManageResponse(BaseModel):
    data: List[DatasetInfo]

# --------------------------------- /datasets/create ---------------------------------


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


class CreateDatasetInformationRequest(BaseModel):
    dataset_id: str = Field(..., description="Dataset ID from /datasets/store")
    file_id: str = Field(..., description="File ID from /datasets/extract")
    dataset_name: str = Field(..., description="Name of the dataset")
    description: Optional[str] = Field(
        None, description="Description of the dataset")
    tags: List[str] = Field(default_factory=list,
                            description="Tags for dataset")
    dataset_type: str = Field(..., description="Type of dataset")
    permission: str = Field(..., description="Access permission")
    is_spatial: bool = Field(False, description="Spatial dataset?")
    is_temporal: bool = Field(False, description="Temporal dataset?")
    temporal_granularities: Optional[List[TemporalGranularity]] = None
    spatial_granularities: Optional[List[SpatialGranularity]] = None
    location_columns: Optional[List[str]] = Field(
        None, description="location columns")
    time_columns: Optional[List[str]] = Field(None, description="time columns")
    user_id: str = Field(..., description="User ID")
    user_name: str = Field(..., description="User name")
    user_email: Optional[str] = Field(None, description="User email")


class CreateDatasetInformationResponse(BaseModel):
    status: str = Field(..., description="Response Status")
    id: str = Field(..., description="Unique identifier for the dataset")

# --------------------------------- /datasets/{dataset_id} ---------------------------------


class DatasetDetail(BaseModel):
    """Schema representing detailed dataset information."""
    dataset_id: str = Field(...,
                            description="Unique identifier for the dataset")
    dataset_name: str = Field(..., description="Name of the dataset")
    file_id: str = Field(..., description="ID of the file in storage")
    description: str = Field(...,
                             description="Optional description of the dataset")
    tags: List[str] = Field(...,
                            description="List of tags associated with the dataset")
    dataset_type: str = Field(..., description="Type of the dataset")
    permissions: str = Field(...,
                             description="Permissions associated with the dataset")
    is_spatial: bool = Field(...,
                             description="Whether the dataset contains spatial data")
    is_temporial: bool = Field(...,
                               description="Whether the dataset contains temporal data")
    temporal_granularities: Optional[List[TemporalGranularity]
                                     ] = Field(..., description="Temporal Granularities")
    spatial_granularities: Optional[List[SpatialGranularity]
                                    ] = Field(..., description="Spatial Granularities")
    location_columns: Optional[List[str]
                               ] = Field(..., description="location columns")
    time_columns: Optional[List[str]] = Field(..., description="time columns")
    pulled_from_pipeline: bool = Field(
        ..., description="Whether the dataset was pulled from a pipeline")
    created_at: datetime = Field(...,
                                 description="Timestamp when the dataset was created")
    updated_at: datetime = Field(...,
                                 description="Timestamp when the dataset was last updated")
    user_id: List[str] = Field(...,
                               description="List of user IDs associated with the dataset")
    user_name: List[str] = Field(...,
                                 description="List of usernames associated with the dataset")
    user_email: List[str] = Field(
        ..., description="List of user emails associated with the dataset")
    rows: List[Dict[str, Any]] = Field(
        ..., description="Preview of dataset records (top 10 rows & columns)")


class DatasetInfoResponse(BaseModel):
    """Response schema for fetching dataset details."""
    status: str = Field(..., description="Status of the request")
    data: DatasetDetail

# --------------------------------- /pipelines ---------------------------------


class PipelineHistoryItem(BaseModel):
    exec_id: str = Field(..., description="Execution ID of the pipeline run")
    status: str = Field(
        ..., description="Status of the execution (success, failed, running, completed)")
    user: str = Field(..., description="User who executed the pipeline")
    executed_at: datetime = Field(...,
                                  description="Timestamp when the pipeline was executed")


class PipelineItem(BaseModel):
    id: str = Field(..., alias="_id",
                    description="MongoDB unique identifier of the pipeline")
    pipeline_name: str = Field(..., description="Name of the pipeline")
    history: List[PipelineHistoryItem] = Field(
        ..., description="Execution history of the pipeline")


class ResponseGetPipelines(BaseModel):
    data: List[PipelineItem] = Field(
        ..., description="List of pipelines with their execution history")

# --------------------------------- /pipelines/run ---------------------------------


class RunPipelineRequest(BaseModel):
    pipeline_id: str = Field(...,
                             description="Unique identifier of the pipeline to run")
    pipeline_name: str = Field(..., description="Name of the pipeline")
    user_id: str = Field(
        "CSAAdmin", description="User ID of the user executing the pipeline")
    user_name: str = Field(...,
                           description="Username of the user executing the pipeline")
    user_email: str = Field(...,
                            description="Email of the user executing the pipeline")


class RunPipelineResponse(BaseModel):
    status: Literal["running", "success", "failed"] = Field(
        ...,
        description="The current status of the pipeline"
    )
    execution_id: str = Field(..., description="Execution ID for the pipeline")
    executed_at: str = Field(...,
                             description="Timestamp when the pipeline was executed")
    user: str = Field(...,
                      description="Username of the user who executed the pipeline")

# --------------------------------- /pipelines/status ---------------------------------


class HistoryItem(BaseModel):
    exec_id: str = Field(...,
                         description="Unique execution ID of the pipeline run")
    status: str = Field(
        ..., description="Status of the pipeline run (running, success, failed, error)")
    executed_at: str = Field(...,
                             description="ISO formatted timestamp of execution")
    user: str = Field(..., description="User who executed the pipeline")


class PipelineStatusResponse(BaseModel):
    # history: List[HistoryItem] = Field(..., description = "List of matching pipeline execution history items")
    status: str = Field(..., description="Status of the pipeline")

# --------------------------------- /presignedURL ---------------------------------


class PresignedURLResponse(BaseModel):
    upload_url: str = Field(...,
                            description="Presigned URL to upload the file")
    object_name: str = Field(..., description="Object name in storage")

# --------------------------------- /datasets/extract ---------------------------------


class ExtractCsvDataRequest(BaseModel):
    file_object: str = Field(...,
                             description="MinIO object name (path) of the file")
    user_id: str = Field(..., description="User ID")
    user_name: str = Field(..., description="User Name")


class ExtractAndStoreResponse(BaseModel):
    status: str = Field(..., description="Response Status")
    file_id: str = Field(..., description="File ID from files collection")
    dataset_id: str = Field(...,
                            description="Dataset ID from datasets collection")

# --------------------------------- /datasets/columns ---------------------------------


class DatasetColumnsRequest(BaseModel):
    dataset_id: str = Field(..., description="Dataset identifier")
    search: str | None = Field(
        None, description="Optional search string to filter columns")


class DatasetColumnsResponse(BaseModel):
    columns: List[str] = Field(...,
                               description="List of dataset column names (filtered)")


class Tag(BaseModel):
    id: int = Field(..., description="Unique identifier of the tag", example=123)
    name: str = Field(..., description="Name of the tag")


class Role(BaseModel):
    """
    Role object representing a user role.
    """
    role_name: str = Field(..., description="Name of the role")
    description: str | None = Field(
        None, description="Description of the role")
    is_active: bool = Field(
        default=True, description="Whether the role is active")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the role was created")
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the role was last updated")


class User(BaseModel):
    """
    User object.
    """
    first_name: Optional[str] = Field(
        None, description="First name of the user")
    last_name: Optional[str] = Field(None, description="Last name of the user")
    email: Optional[str] = Field(
        None, description="Email address", example="name@email.com")
    phone: Optional[str] = Field(None, description="Phone number")
    external_id: str = Field(...,
                             description="External ID from OAuth provider (e.g., Google sub)")
    role_id: Optional[str] = Field(
        None, description="Role ID from roles collection")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the user was created")
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the user was last updated")


class CreateUserFromOAuth(BaseModel):
    """
    Schema for creating user from OAuth provider data.
    """
    first_name: Optional[str] = Field(
        None, description="First name of the user")
    last_name: Optional[str] = Field(None, description="Last name of the user")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    external_id: str = Field(...,
                             description="External ID from OAuth provider (e.g., Google sub)")


class UserResponse(BaseModel):
    """
    User response object.
    """
    id: str = Field(..., description="Unique user ID (UUID)")
    first_name: Optional[str] = Field(
        None, description="First name of the user")
    last_name: Optional[str] = Field(None, description="Last name of the user")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    external_id: str = Field(...,
                             description="External ID from OAuth provider")
    role_id: Optional[str] = Field(
        None, description="Role ID assigned to the user")
    created_at: datetime = Field(...,
                                 description="Timestamp when the user was created")
    updated_at: datetime = Field(...,
                                 description="Timestamp when the user was last updated")


class ApiResponse(BaseModel):
    """
    Generic API response.
    """
    code: Optional[int] = Field(None, description="Response code", example=200)
    type: Optional[str] = Field(None, description="Type of response")
    message: Optional[str] = Field(
        None, description="Message accompanying the response")


class EndpointAccess(BaseModel):
    """
    Endpoint access control object.
    """
    role: str = Field(..., description="Role name")
    endpoint: str = Field(..., description="Endpoint path pattern")
    viewer: bool = Field(default=False, description="Viewer permission")
    contributor: bool = Field(
        default=False, description="Contributor permission")
    admin: bool = Field(default=False, description="Admin permission")
    created_time: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the access control was created")


class RoleCheckRequest(BaseModel):
    """
    Request schema for role checking.
    """
    path: str = Field(..., description="Path to check access for")


class RoleCheckResponse(BaseModel):
    """
    Response schema for role checking.
    """
    viewer: bool = Field(default=False, description="Viewer permission")
    contributor: bool = Field(
        default=False, description="Contributor permission")
    admin: bool = Field(default=False, description="Admin permission")
    role_name: Optional[str] = Field(None, description="User's role name")


class Error(BaseModel):
    """
    Error response object.
    """
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
