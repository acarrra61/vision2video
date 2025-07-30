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
            "stabilityai/stable-video-diffusion-img2vid",  # Faster non-XT version, the other version was img2vid-x
            torch_dtype=dtype,
            variant="fp16",  # Use "fp16" variant for float16 precision on GPU
        )
        pipe.to(device)

        # Enable memory efficient attention for faster processing
        if device == "cuda":
            pipe.enable_attention_slicing()
            pipe.enable_model_cpu_offload()  # Offload unused parts to CPU to save VRAM

        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    print(f"Step 3: Loading and preparing the input image from: {image_path}...")
    try:
        image = load_image(image_path)
        # Resizing the image to the required dimensions (change if needed)
        image = image.resize((1024, 576), Image.Resampling.LANCZOS)
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    print("Step 4: Generating video frames.. (This can take several minutes!)")
    # The model works best with a seed for reproducibility (change if needed)
    generator = torch.manual_seed(42)

    frames = pipe(
        image,
        decode_chunk_size=4,  # Increased for better speed with RTX 4070
        generator=generator,
        motion_bucket_id=127,  # Controls the amount of motion in the video
        noise_aug_strength=0.1,  # Adds a bit of noise for more motion
        num_frames=14,  # Reduce from default 25 frames for faster generation
        num_inference_steps=20,  # Reduce from default 25 steps for speed
    ).frames[0]
    print("Frame generaton completed.")

    print(f"Step 5: Exporting frames to video file: {output_path}...")
    try:
        export_to_video(
            frames, output_path, fps=7
        )  # Exporting with 7 frames per second
        print(f"Success! Video saved to: {output_path}")
    except Exception as e:
        print(f"Error exporting video: {e}")


if __name__ == "__main__":
    # Using argparse to handle command line arguments in order to pass information to the script
    parser = argparse.ArgumentParser(
        description="Generate a video from an image using Stable Video Diffusion Model."
    )
    parser.add_argument(
        "--image_path",
        type=str,
        default="test_image.png",
        help="Path to the input image file",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="generated_video.mp4",
        help="Path to save the output video",
    )
    args = parser.parse_args()

    generate_video_from_image(args.image_path, args.output_path)
