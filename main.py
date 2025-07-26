import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse

# Create uploads and outputs directories if they dont exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app = FastAPI(title="Vision 2 Video API")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Vision 2 Video API!"}
