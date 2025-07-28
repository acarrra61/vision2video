import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Importing the generator function to link it with the API
from generate import generate_video_from_image

# Create uploads and outputs directories if they dont exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app = FastAPI(title="Vision 2 Video API")

# This allows React frontend (running on port 5173) to talk to the API (running on port 8000)
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

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
        # Calling the video generation function from generate.py!
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


@app.post("/generate_video")
async def create_video_generation_job(
    background_tasks: BackgroundTasks, image: UploadFile = File(...)
):
    """
    The main endpoint to handle video generation requests.
    It accepts an image file, saves it temporarily, and starts the video generation as a background task.
    """

    # Generate a unique job ID for this job for tracking
    job_id = str(uuid.uuid4())

    # Define paths for temporary image and output video
    temp_image_path = os.path.join("uploads", f"{job_id}_{image.filename}")
    output_video_path = os.path.join("outputs", f"{job_id}.mp4")

    # Save the uploaded file
    with open(temp_image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Start the background task
    background_tasks.add_task(
        run_generation_in_background, job_id, temp_image_path, output_video_path
    )

    # Immediately return the job ID to the client
    return JSONResponse(
        status_code=202,  # The request is accepted for processing
        content={"job_id": job_id},
    )


@app.get("/status/{job_id}")
def get_job_status(job_id: str):
    """
    The endpoint to check the status of a generation job.
    """
    status = job_status.get(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status


# To allow the front-end to access the generated videos,
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
