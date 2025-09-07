from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.pipelines.pipeline import run_router
from app.api.endpoints.datasets.datasets import datasets_router 
from app.api.endpoints.datasets.manage import manage_router
from app.api.endpoints.datasets.dataset_info import dataset_info_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run_router)
app.include_router(datasets_router) 
app.include_router(manage_router)
app.include_router(dataset_info_router)