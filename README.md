# Vision 2 Video (ComfyUI Edition) ✨

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![ComfyUI](https://img.shields.io/badge/ComfyUI-ec5824?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xOC43ODQgOS44MTRhMy42ODMgMy42ODMgMCAwIDAtLjIwOC0xLjE4NmwxLjMyOC0uNzY3YTMuNzg1IDMuNzg1IDAgMCAwLTEuODYtMy4yMjFsLTEuMzI4Ljc2N2EzLjY1OCAzLjY1OCAwIDAgMC0yLjA2OC0uNDI0di0xLjUzNGEzLjc4NSAzLjc4NSAwIDAgMC0zLjY4OS0zLjc0MmgtLjA1MmEzLjc4NSAzLjc4NSAwIDAgMC0zLjc0MiAzLjc0MnYxLjUzNGEzLjY1OCAzLjY1OCAwIDAgMC0yLjA2OC40MjRMNCA1LjE4MmEzLjc4NSAzLjc4NSAwIDAgMC0xLjg2IDMuMjIxbDEuMzI4Ljc2N2EzLjY4MyAzLjY4MyAwIDAgMC0uMjA4IDEuMTg2SDJWMTQuOGg1LjIzMmEzLjY4MyAzLjY4MyAwIDAgMCAuMjA4IDEuMTg2bC0xLjMyOC43NjdhMy43ODUgMy43ODUgMCAwIDAgMS44NiAzLjIyMWwxLjMyOC0uNzY3YTMuNjU4IDMuNjU4IDAgMCAwIDIuMDY4LjQyNHYxLjUzNGEzLjc4NSAzLjc4NSAwIDAgMCAzLjc0MiAzLjc0MmgwLjA1MmEzLjc4NSAzLjc4NSAwIDAgMCAzLjc0Mi0zLjc0MnYtMS41MzRhMy42NTggMy42NTggMCAwIDAgMi4wNjgtLjQyNGwxLjMyOC43NjdhMy43ODUgMy43ODUgMCAwIDAgMS44Ni0zLjIyMWwtMS4zMjgtLjc2N2EzLjY4MyAzLjY4MyAwIDAgMCAuMjA4LTEuMTg2SDIyVjkuODE0aC0zLjIxNlpNNy45MTIgMTIuMzRhMS42NTIgMS42NTIgMCAxIDEgMS42NTItMS42NTIgMS42NTIgMS42NTIgMCAwIDEgLTEuNjUyIDEuNjUyWm04LjE3NiAwYTEuNjUyIDEuNjUyIDAgMSAxIDEuNjUyLTEuNjUyIDEuNjUyIDEuNjUyIDAgMCAxIC0xLjY1MgMS42NTJaIi8+PC9zdmc+)

An advanced full-stack application that transforms a static image and a text prompt into a dynamic, AI-generated video using a powerful ComfyUI backend.

---

### 📸 App Demo

**This is a huge upgrade from the last AI model being used!**

![Vision 2 Video ComfyUI Demo](assets/Vision2Video.gif)

---

### 💡 Architecture & Technology

This project utilizes a sophisticated two-server architecture to separate concerns and leverage the best tools for each job.

#### Frontend (The User Interface)
The UI is a sleek, modern single-page application designed for an intuitive user experience.
*   **Built with React & Vite:** Providing a fast, responsive, and interactive UI.
*   **Styled with Tailwind CSS & shadcn/ui:** A professional and fully responsive design built with industry-standard tools.
*   **Key Feature:** Users can provide both an image and a **text prompt**, giving them creative control over the final video output.

#### Backend (The Orchestrator & AI Engine)
The backend is composed of two distinct services that work in harmony:

1.  **FastAPI Orchestrator (This Project):**
    *   This server acts as the "brain" of the operation. It receives user requests (image + prompt) from the React frontend.
    *   It dynamically constructs a workflow JSON for the ComfyUI engine, injecting the user's prompt and unique filenames.
    *   It sends the job to ComfyUI, then intelligently polls for the output file, providing real-time status updates back to the user.

2.  **ComfyUI Engine (The AI Powerhouse):**
    *   This runs as a separate, dedicated server, handling the heavy AI computation.
    *   The node-based workflow uses the state-of-the-art **Wan 2.2** model with for high-quality, prompt-guided video generation.
    *   **New Dependencies:** This powerful setup relies on specialized libraries like **Triton** and **SageAttention** for optimized performance.

---

### 🔧 Running the Project Locally

This project requires running two separate servers. Please follow these instructions carefully.

#### Prerequisites
*   Git
*   Python 3.10+ and Pip
*   Node.js and npm

#### 1. Set Up the Project Folders
First, clone this repository which contains the FastAPI orchestrator and the React frontend.
```bash
git clone https://github.com/your-username/vision2video.git
cd vision2video
```

#### 2. Set Up the ComfyUI Backend
This project requires a specific ComfyUI setup.
```bash
# From your main projects directory (not inside vision2video)
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install ComfyUI's Python dependencies
pip install -r requirements.txt

# IMPORTANT: Install custom dependencies for the Wan 2.2 workflow
# Please follow the specific installation instructions for Triton and SageAttention
# This may involve commands like:
# pip install triton
# pip install ... (for SageAttention)
```

**Model Downloads Required:**

You need to download and place the following models in their respective ComfyUI directories:

*   **🔧 Workflow Models (UNet):**
    *   Download high or low VRAM versions suitable for your GPU
    *   **Path:** `ComfyUI/models/unet/`
    *   **Source:** [Wan2.2-I2V-A14B-GGUF](https://huggingface.co/bullerwins/Wan2.2-I2V-A14B-GGUF/tree/main)

*   **✨ Lightx2v LoRA:**
    *   **Path:** `ComfyUI/models/loras/`
    *   **Source:** [WanVideo Lightx2v](https://huggingface.co/Kijai/WanVideo_comfy/tree/main/Lightx2v)

*   **📝 Text Encoder:**
    *   **Path:** `ComfyUI/models/text_encoders/`
    *   **Source:** [ComfyUI Wan22 Examples](https://comfyanonymous.github.io/ComfyUI_examples/wan22/)

*   **🎬 VAE (Video Autoencoder):**
    *   **Path:** `ComfyUI/models/vae/`
    *   **Source:** [ComfyUI Wan22 Examples](https://comfyanonymous.github.io/ComfyUI_examples/wan22/)

#### 3. Set Up the FastAPI Backend
```bash
# Go back to the vision2video project directory
cd ../vision2video

# Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies for this server
pip install -r requirements.txt
```

#### 4. Set Up the React Frontend
```bash
# In a new terminal, navigate to the frontend directory
cd vision2video/frontend

# Install Node.js dependencies
npm install
```

#### 5. Run the Full System!
You need to run **three terminals** simultaneously.

*   **Terminal 1 (ComfyUI Engine):**
    ```bash
    cd ComfyUI
    python main.py
    ```

*   **Terminal 2 (FastAPI Orchestrator):**
    ```bash
    cd vision2video
    uvicorn main:app --reload

*   **Terminal 3 (React Frontend):**
    ```bash
    cd frontend
    npm run dev