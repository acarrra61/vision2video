import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse

# Importing the generator function to link it with the API
from generate import generate_video_from_image

# Create uploads and outputs directories if they dont exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app = FastAPI(title="Vision 2 Video API")

# A dictionary to keep track of job statuses similar to a database
job_status: dict[str, dict] = {}


def run_generation_in_background(
    job_id: str, temp_image_path: str, output_video_path: str
):
    """
    A wrapper function to run the AI task in the background.
    It updates the job_status dict before and after the running task.
    """
    print(f"Job {job_id}: Starting video generation from {temp_image_path}")
    job_status[job_id] = {"status": "processing"}
    try:
        # Calling the video generation function from generate.py
        generate_video_from_image(
            image_path=temp_image_path, output_path=output_video_path
        )
        job_status[job_id] = {"status": "completed", "video_path": output_video_path}
    except Exception as e:
        print(f"Job {job_id}: Video generation failed with error: {e}")
        job_status[job_id] = {"status": "failed", "error": str(e)}
    finally:
        # Cleaning up the uploaded image file after it is done being processed
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
