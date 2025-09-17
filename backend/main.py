from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

# AWS Lambda handler
handler = Mangum(app)
