import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Upload, Play, Download, Sparkles, Zap, Shield, Clock, ImageIcon, Video } from "lucide-react"

export default function App() {
  const [uploadedImage, setUploadedImage] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [generatedVideo, setGeneratedVideo] = useState(null)
  const [originalFile, setOriginalFile] = useState(null); 
  const [prompt, setPrompt] = useState("");

const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
        setOriginalFile(file); // Store the file object
        const reader = new FileReader();
        reader.onload = (e) => {
            setUploadedImage(e.target.result); // This is for the preview
        };
        reader.readAsDataURL(file);
    }
};

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith("image/")) {
      setOriginalFile(file); // Store the file object
      const reader = new FileReader()
      reader.onload = (e) => {
        setUploadedImage(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  // To call the Python backend
const generateVideo = async () => {
    if (!uploadedImage) return;

    setIsProcessing(true);
    setProgress(0);
    setGeneratedVideo(null); // Clear previous video

    // Create FormData object
    const formData = new FormData();
    formData.append('image', originalFile);
    formData.append('prompt', prompt);

    try {
        // --- 1. Start the generation job ---
        const startResponse = await fetch("http://127.0.0.1:8000/generate_video", {
            method: 'POST',
            body: formData,
        });

        if (!startResponse.ok) {
            throw new Error('Failed to start video generation.');
        }

        const { job_id } = await startResponse.json();
        
        // --- 2. Poll for the result ---
        const pollInterval = setInterval(async () => {
            const statusResponse = await fetch(`http://127.0.0.1:8000/status/${job_id}`);
            if (!statusResponse.ok) {
                // To not stop polling on 404, it might just not be ready
                return; 
            }

            const data = await statusResponse.json();
            setProgress(prev => Math.min(prev + 15, 90)); // Show some progress

            if (data.status === 'completed') {
                clearInterval(pollInterval);
                setProgress(100);
                // Construct the full URL for the video
                setGeneratedVideo(`http://127.0.0.1:8000/outputs/${job_id}.mp4`);
                setIsProcessing(false);
            } else if (data.status === 'failed') {
                clearInterval(pollInterval);
                console.error("Generation failed:", data.error);
                setIsProcessing(false);
            }
            // If status is 'processing', keep polling
        }, 3000); // Check every 3 seconds

    } catch (error) {
        console.error("Error submitting job:", error);
        setIsProcessing(false);
    }
};

  // Function to handle video download
  const downloadVideo = async () => {
    if (generatedVideo) {
      try {
        // Fetch the video as a blob to avoid CORS issues
        const response = await fetch(generatedVideo);
        if (!response.ok) {
          throw new Error('Failed to fetch video');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'generated_video.mp4';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up the blob URL
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Download failed:', error);
        alert('Failed to download video. Please try again.');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Vision2Video
              </span>
            </div>
            <nav className="hidden md:flex items-center space-x-6">
              <a href="#" className="text-sm font-medium text-gray-600 hover:text-gray-900">
                Features
              </a>
              <a href="#" className="text-sm font-medium text-gray-600 hover:text-gray-900">
                Pricing
              </a>
              <a href="#" className="text-sm font-medium text-gray-600 hover:text-gray-900">
                API
              </a>
              <Button variant="outline" size="sm">
                Sign In
              </Button>
              <Button size="sm">Get Started</Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <Badge variant="secondary" className="mb-4">
          <Sparkles className="w-3 h-3 mr-1" />
          AI-Powered Video Generation
        </Badge>
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          Transform Images into
          <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent block">
            Dynamic Videos
          </span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Upload any image and watch the AI bring it to life with smooth, realistic motion. Perfect for social media,
          marketing, and creative projects.
        </p>
      </section>

      {/* Main Content */}
      <section className="container mx-auto px-4 pb-16">
         <div className="max-w-4xl mx-auto"> 
          <div className="grid md:grid-cols-2 gap-8">
            {/* Upload Section */}
            <Card className="border-2 border-dashed border-gray-200 hover:border-purple-300 transition-colors">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <ImageIcon className="w-5 h-5 mr-2" />
                  Upload Image
                </CardTitle>
                <CardDescription>Drag and drop your image or click to browse</CardDescription>
              </CardHeader>
              <CardContent>
                {!uploadedImage ? (
                  <div
                    className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-purple-400 transition-colors cursor-pointer"
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById("file-upload").click()}
                  >
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-2">Drop your image here</p>
                    <p className="text-sm text-gray-400">PNG, JPG, WEBP up to 10MB</p>
                    <input
                      id="file-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                    />
                  </div>
                ) : (
                  <div className="space-y-4">
                    <img
                      src={uploadedImage || "/placeholder.svg"}
                      alt="Uploaded"
                      className="w-full h-48 object-cover rounded-lg"
                    />
                    <div className="flex justify-between items-center">
                      <Badge variant="outline">Ready to process</Badge>
                      <Button onClick={() => setUploadedImage(null)} variant="outline" size="sm">
                        Remove
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Generation Section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Video className="w-5 h-5 mr-2" />
                  Generated Video
                </CardTitle>
                <CardDescription>Your AI-generated video will appear here</CardDescription>
              </CardHeader>
              <CardContent>
                {!generatedVideo && !isProcessing ? (
                  <div className="border-2 border-gray-200 rounded-lg p-8 text-center">
                    <Play className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">Upload an image to get started</p>
                    {uploadedImage && (
                      <Button onClick={generateVideo} className="w-full">
                        <Sparkles className="w-4 h-4 mr-2" />
                        Generate Video
                      </Button>
                    )}
                  </div>
                ) : isProcessing ? (
                  <div className="space-y-4">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Sparkles className="w-8 h-8 text-white animate-pulse" />
                      </div>
                      <h3 className="font-semibold mb-2">Generating your video...</h3>
                      <p className="text-sm text-gray-600 mb-4">This may take a few minutes</p>
                    </div>
                    <Progress value={progress} className="w-full" />
                    <p className="text-center text-sm text-gray-500">{progress}% complete</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="relative">
                      <video
                        src={generatedVideo}
                        className="w-full h-64 md:h-80 lg:h-96 object-contain rounded-lg bg-black"
                        controls
                        poster={uploadedImage} // Use the original image as poster
                      >
                        Your browser does not support the video tag.
                      </video>
                    </div>
                    <div className="flex space-x-2">
                      <Button onClick={downloadVideo} className="flex-1">
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => {
                          setGeneratedVideo(null)
                          setUploadedImage(null)
                          setOriginalFile(null)
                          setProgress(0)
                        }}
                      >
                        New Video
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

           {/* --- NEW: Prompt Section --- */}
          <Card className="mt-6 mb-8">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Sparkles className="w-5 h-5 mr-2" />
                2. Enter Your Prompt
              </CardTitle>
              <CardDescription>Describe the motion or scene you want to see.</CardDescription>
            </CardHeader>
            <CardContent>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g., a person waving, cinematic, photorealistic..."
                className="w-full h-24 p-2 bg-slate-100 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:outline-none resize-none"
                rows={4}
                disabled={false}
              />
            </CardContent>
          </Card>
          {/* ------------------------- */}

          {/* Process Steps */}
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-center mb-8">How it works</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Upload className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="font-semibold mb-2">1. Upload Image</h3>
                <p className="text-gray-600 text-sm">Upload any image in PNG, JPG, or WEBP format</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="font-semibold mb-2">2. AI Processing</h3>
                <p className="text-gray-600 text-sm">AI analyzes and adds realistic motion to your image</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Download className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="font-semibold mb-2">3. Download Video</h3>
                <p className="text-gray-600 text-sm">Get your high-quality video ready for sharing</p>
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-center mb-8">Why choose Vision2Video?</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6 text-center">
                  <Zap className="w-8 h-8 text-yellow-500 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Lightning Fast</h3>
                  <p className="text-sm text-gray-600">Generate videos in seconds, not hours</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6 text-center">
                  <Shield className="w-8 h-8 text-green-500 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Secure & Private</h3>
                  <p className="text-sm text-gray-600">Your images are processed securely and deleted after use</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6 text-center">
                  <Sparkles className="w-8 h-8 text-purple-500 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">AI-Powered</h3>
                  <p className="text-sm text-gray-600">Advanced AI creates realistic and smooth motion</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6 text-center">
                  <Clock className="w-8 h-8 text-blue-500 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">24/7 Available</h3>
                  <p className="text-sm text-gray-600">Generate videos anytime, anywhere</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-6 h-6 bg-gradient-to-r from-purple-600 to-blue-600 rounded flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="font-semibold">Vision2Video</span>
            </div>
            <div className="flex space-x-6 text-sm text-gray-600">
              <a href="#" className="hover:text-gray-900">
                Privacy Policy
              </a>
              <a href="#" className="hover:text-gray-900">
                Terms of Service
              </a>
              <a href="#" className="hover:text-gray-900">
                Support
              </a>
            </div>
          </div>
          <Separator className="my-4" />
          <p className="text-center text-sm text-gray-500">© 2024 Vision2Video. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}