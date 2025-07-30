import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import uuid
import time

# Importing the generator function to link it with the API
from generate import generate_video_from_image
from fastapi import Form

# Create uploads and outputs directories if they dont exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app = FastAPI(title="Vision 2 Video API")

comfyUI_URL = "http://127.0.0.1:8188"


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


def run_generation_in_background(job_id: str, temp_image_path: str, prompt: str):
    """
    Sends a job to the ComfyUI API and polls for the output file.
    """
    print(f"Job {job_id}: Relaying generation request to ComfyUI with prompt: {prompt}")
    job_status[job_id] = {"status": "processing"}

    try:
        # 1. Load the API workflow template
        with open("workflow_api.json", "r", encoding="utf-8") as f:
            prompt_workflow = json.load(f)

        # 2. Modify the workflow with our specific inputs
        # find node IDs from your saved workflow_api.json file
        IMAGE_LOADER_NODE_ID = "52"  # <-- IMPORTANT: Change if your ID is different
        PROMPT_NODE_ID = "6"  # <-- IMPORTANT: Change if your ID is different
        VIDEO_SAVER_NODE_ID = "63"  # <-- IMPORTANT: Change if your ID is different

        # Tell the Loder node which image to use (must be in ComfyUI's input folder)
        prompt_workflow[IMAGE_LOADER_NODE_ID]["inputs"]["image"] = os.path.basename(
            temp_image_path
        )

        # Set the user's text prompt
        prompt_workflow[PROMPT_NODE_ID]["inputs"]["text"] = prompt

        # Tell the Saver node to name the output file with our unique job_id
        prompt_workflow[VIDEO_SAVER_NODE_ID]["inputs"]["filename_prefix"] = job_id

        # 3. Send the job to ComfyUI
        payload = {"prompt": prompt_workflow}
        comfyui_url = "http://127.0.0.1:8188/prompt"
        response = requests.post(comfyui_url, json=payload)
        response.raise_for_status()

        # 4. Poll for the output file
        print(f"Job {job_id}: ComfyUI accepted the job. Now waiting for output file...")
        output_dir = "../AIProjects/ComfyUI/output"
        expected_filename_part = f"{job_id}_"

        timeout_seconds = 300  # 5 minutes
        start_time = time.time()
        video_file_found = None

        while time.time() - start_time < timeout_seconds:
            for filename in os.listdir(output_dir):
                if filename.startswith(expected_filename_part):
                    print(f"Job {job_id}: Found output file: {filename}")
                    video_file_found = filename
                    break
            if video_file_found:
                break

            time.sleep(3)  # Wait 3 seconds before checking again

        if not video_file_found:
            raise TimeoutError("Video generation timed out.")

        # 5. Copy the video file to our outputs directory for serving
        source_video_path = os.path.join(output_dir, video_file_found)
        target_video_path = os.path.join("outputs", f"{job_id}.mp4")
        shutil.copy2(source_video_path, target_video_path)

        # 6. Job is complete! Update the status.
        job_status[job_id] = {"status": "completed", "video_path": target_video_path}
        print(
            f"Job {job_id}: Successfully completed. Video available at outputs/{job_id}.mp4"
        )

    except Exception as e:
        print(f"Job {job_id}: An error occurred. {e}")
        job_status[job_id] = {"status": "failed", "error": str(e)}
    finally:
        # Clean up the temporary image in ComfyUI's input folder
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)


@app.post("/generate_video")
async def create_video_generation_job(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    prompt: str = Form("a beautiful woman smiling"),
):
    """
    The main endpoint to handle video generation requests.
    It accepts an image file, saves it temporarily, and starts the video generation as a background task.
    """

    job_id = str(uuid.uuid4())

    # --- CHANGE THIS PATH ---
    # Save the uploaded file directly into ComfyUI's input directory
    comfy_input_dir = "../AIProjects/ComfyUI/input"
    os.makedirs(comfy_input_dir, exist_ok=True)
    temp_image_path = os.path.join(comfy_input_dir, f"{job_id}_{image.filename}")
    # -----------------------

    with open(temp_image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    background_tasks.add_task(
        run_generation_in_background, job_id, temp_image_path, prompt
    )

    return JSONResponse(status_code=202, content={"job_id": job_id})


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
