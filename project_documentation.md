# Deepfake Detection Project Documentation

## 1. Project Overview

### What is this project?
This is a state-of-the-art **Deepfake Detection System** designed to identify artificially manipulated or synthetic videos. It analyzes video inputs and determines the probability of a video being a "Deepfake" (fake) versus "Real" (authentic).

### Goal and Motivation
As deepfake technology becomes increasingly sophisticated, distinguishing between real and fabricated media grows more challenging. Deepfakes can undermine confidence in news sources, violate individual privacy, manipulate democratic processes, and compromise financial security (e.g., identity verification fraud).
The goal of this project is to provide a reliable tool to help maintain trust in digital content and protect individuals and systems from manipulation by accurately detecting deepfakes.

---

## 2. Technology Stack

This project is built using a modern AI/Machine Learning stack, primarily powered by Python and PyTorch.

### Core Machine Learning & AI
*   **PyTorch (`torch`)**: The foundational deep learning framework used for building, training, and running the neural network models.
*   **Torchvision (`torchvision`)**: Used for computer vision utilities and pre-trained models (like ResNeXt-50).
*   **Transformers (`transformers`)**: A library by Hugging Face used to implement the Vision Transformer (ViT) architecture.

### Video & Image Processing
*   **OpenCV (`opencv-python`)**: Essential for reading video files, splitting videos into individual frames, and calculating Optical Flow to analyze motion.
*   **Pillow (`Pillow`)**: Used for image manipulation and integration with PyTorch transformations.
*   **NumPy (`numpy`)**: Fundamental package for scientific computing in Python, used for handling multi-dimensional arrays and mathematical operations on image data.

### User Interface (Frontend)
*   **Gradio (`gradio`)**: The web framework used to build the interactive user interface. It provides an intuitive, easy-to-use web app where users can upload videos and immediately see the detection results and analysis.

### Visualization (Optional/Development)
*   **Matplotlib (`matplotlib`)**: Available for plotting metrics or visualizing analysis results, though primarily the frontend handles immediate results presentation.

---

## 3. System Architecture & Workflow

The system utilizes a **Hybrid Multi-Stream Architecture** (Ensemble Learning) to detect deepfakes, combining three specialized analysis methods to achieve high accuracy.

### 3.1 Workflow Steps
1.  **Video Input**: User uploads an MP4 video via the Gradio web interface.
2.  **Preprocessing (`utils.py`)**:
    *   The video is split into individual frames using OpenCV.
    *   An OpenCV face detector (`haarcascade_frontalface_default.xml`) locates and crops the subject's face from the frames.
    *   The cropped faces are resized to a standard resolution (224x224) and converted to PyTorch tensors with specific normalizations.
3.  **Optical Flow Calculation**: The system computes the motion (Optical Flow) between consecutive frames to detect temporal anomalies or unnatural movements often present in deepfakes.
4.  **Neural Network Analysis (`model.py`)**: The processed frames and optical flow data are passed through three distinct networks.
5.  **Ensemble Prediction**: The outputs from all three streams are combined (concatenated) and passed through a final set of fully connected layers to produce a final "Fake" or "Real" probability score.

### 3.2 The Three Analysis Streams (The Hybrid Model)
1.  **ResNeXt-50 (Spatial Feature Analysis)**: A powerful convolutional neural network (CNN) that scrutinizes individual frames for spatial artifacts—tiny blurring, mismatched lighting, or unnatural textures introduced by deepfake generation algorithms.
2.  **Vision Transformer / ViT (Advanced Pattern Recognition)**: A transformer-based model that analyzes images by breaking them into patches. It excels at understanding the global context of the image and finding complex, high-level structural anomalies across the face.
3.  **Optical Flow CNN (Motion Analysis)**: A custom small Convolutional Neural Network that analyzes the optical flow data. It looks for temporal inconsistencies, such as unnatural blinking, robotic head movements, or mismatched lip-syncing that occur between frames over time.

---

## 4. Key Files and Their Roles

*   **`app.py`**: The main entry point. It sets up the Gradio web application (Home, About, Credits tabs), loads the pre-trained neural network weights (`deepfake_model_weights.pth`), handles the user interface styling, and defines the `detect_deepfake` function that bridges the UI and the model.
*   **`model.py`**: Contains the PyTorch definition of the `HybridDeepfakeDetector` architecture, explicitly setting up the ResNeXt, ViT, Optical Flow CNN, and the final classification layers.
*   **`utils.py`**: Contains the critical video processing logic. It handles video reading, face detection and cropping using Haar Cascades, calculating Optical Flow (`cv2.calcOpticalFlowFarneback`), and applying PyTorch transformations (resizing, normalizing) to prepare the data for the model.
*   **`deepfake_model_weights.pth`**: A massive (~443 MB) file containing the trained weights (learned parameters) for the model. The model loads these weights to make predictions without needing to be retrained from scratch.
*   **`requirements.txt`**: Lists all the Python dependencies required to run the project.

---

## 5. Team & Academic Details

This system was developed as a final year BE Computer Engineering project by:
*   **Team**: Manasi Khaire, Pavitra Desai, Sai Nagane, Siddhi Algude
*   **Project Guide**: Prof. Kiran Yesugade
*   **Institution**: Bharati Vidyapeeth's College of Engineering for Women, Department of Computer Engineering

*Note: The application includes important Disclaimers that no detection system is perfect (risk of false positives/negatives) and results should be verified by experts in high-stakes situations.*
