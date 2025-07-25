import argparse
import torch
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video
from PIL import Image


def generate_video_from_image(
    image_path: str, output_path: str = "generated_video.mp4"
):
    """
    Generates a video from a single image using Stable Video Diffusion.
    Args:
        image_path (str): The path to the input image file.
        output_path (str): The path where the output video will be saved.
    """
    print("Step 1: Checking for available hardware (GPU/CPU)...")
    # Use GPU if available (CUDA for NVIDIA, MPS for Apple Silicon), otherwise fall back to CPU
    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available() else "cpu"
    )
    # Use float16 precision for GPU, float32 for CPU
    dtype = torch.float16 if device != "cpu" else torch.float32
    print(f"Using device: {device} with dtype: {dtype}")

    print("Step 2: Loading the Stable Video Diffusion model...")
    try:
        # This will download the model the first time it is ran (it's a few GB).
        # It will be cached for subsequent runs.
        pipe = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt",
            torch_dtype=dtype,
            variant="fp16",  # Use "fp16" variant for float16 precision on GPU
        )
        pipe.to(device)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    print(f"Step 3: Loading and preparing the input image from: {image_path}...")
    try:
        image = load_image(image_path)
        # Resizing the image to the required dimensions (change if needed)
        image = image.resize(1024, 576)
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return
    except Exception as e:
        print(f"Error loading image: {e}")
        return
