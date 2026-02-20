# app.py
import gradio as gr
import torch
from model import HybridDeepfakeDetector
from utils import preprocess_video
import cv2
import numpy as np
import os
import warnings
import tempfile
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Load model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = HybridDeepfakeDetector().to(device)
model.load_state_dict(torch.load("deepfake_model_weights.pth", map_location=device))
model.eval()

print(f"Model loaded successfully. Using device: {device}")


# Custom CSS for aesthetics
custom_css = """
:root {
    --main-bg-color: #0f172a;
    --card-bg-color: #1e293b;
    --accent-color: #3b82f6;
    --text-color: #f1f5f9;
    --border-radius: 12px;
}

body {
    background-color: var(--main-bg-color);
    color: var(--text-color);
    font-family: 'Poppins', sans-serif;
}

.container {
    border-radius: var(--border-radius);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    background-color: var(--card-bg-color);
    margin-bottom: 20px;
    padding: 20px;
    transition: transform 0.3s ease;
}

.container:hover {
    transform: translateY(-5px);
}

h1, h2, h3 {
    color: var(--accent-color);
    font-weight: 700;
}

.text-center {
    text-align: center;
}

.warning-box {
    background-color: rgba(250, 204, 21, 0.1);
    border-left: 4px solid #facc15;
    padding: 12px;
    margin: 16px 0;
    border-radius: 4px;
    font-size: 0.9em;
}

.tech-card {
    background-color: rgba(59, 130, 246, 0.1);
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0;
    border-left: 4px solid var(--accent-color);
}

.precaution-card {
    background-color: rgba(239, 68, 68, 0.05);
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    border-left: 4px solid #ef4444;
}

.animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: .7;
    }
}

.credit-card {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    padding: 12px;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

.credit-card img {
    margin-right: 12px;
    border-radius: 50%;
}

.results-box {
    border: 2px solid var(--accent-color);
    border-radius: var(--border-radius);
    padding: 15px;
}

.workflow-diagram {
    background-color: rgba(59, 130, 246, 0.05);
    border-radius: var(--border-radius);
    padding: 20px;
    margin: 20px 0;
    text-align: center;
}
"""

def detect_deepfake(video):
    """Process the video and detect if it's a deepfake"""
    try:
        if video is None:
            return {"Error": 1.0, "No video uploaded": 0.0}
            
        video_path = video
        print(f"Processing video: {video_path}")
        
        # Process the video for model prediction
        img_tensor, flow_tensor = preprocess_video(video_path)
        img_tensor, flow_tensor = img_tensor.to(device), flow_tensor.to(device)
        
        with torch.no_grad():
            output = model(img_tensor, flow_tensor)
        prob = output.item()
        
        return {"Fake": prob, "Real": 1 - prob}
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return {"Error": 1.0, "Could not process video": 0.0}

# Home page content
def home_page():
    with gr.Column(elem_classes="container") as home:
        gr.Markdown("""
        # <div class="text-center"><span style="background: linear-gradient(90deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Deepfake Detector</span></div>
        <div class="text-center">Advanced AI-powered tool for detecting manipulated videos with high accuracy. Upload your video to analyze if it's authentic or artificially generated.</div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                video_input = gr.Video(
                    label="Upload Video for Analysis", 
                    format="mp4"
                )
                gr.Markdown("""
                <div class="warning-box">
                    ⚠️ <strong>Warning:</strong> While our system provides high accuracy detection, results should be verified 
                    by experts when dealing with high-stakes situations or legal matters. Only MP4 format videos are supported.
                </div>
                """)
                
            with gr.Column(scale=1):
                with gr.Column(elem_classes="results-box"):
                    gr.Markdown("""<div class="text-center"><span style='color: #3b82f6'>Analysis Results</span></div>""")
                    output = gr.Label(num_top_classes=2)
        
        with gr.Row():
            analyze_btn = gr.Button("🔍 Analyze Video", elem_id="analyze_btn", variant="primary")
            clear_btn = gr.Button("🔄 Clear", elem_id="clear_btn")
        
                
        # Clear all components
        def clear_components():
            return None, {"": 1.0}
            
        # Set up event handlers
        analyze_btn.click(
            fn=detect_deepfake, 
            inputs=video_input, 
            outputs=output
        )
        
        clear_btn.click(
            fn=clear_components, 
            inputs=None, 
            outputs=[video_input, output]
        )
    
    return home

# About page content
def about_page():
    with gr.Column(elem_classes="container") as about:
        gr.Markdown("""
        # <div class="text-center"><span style="background: linear-gradient(90deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">About Our Project</span></div>
        
        ### <div class="text-center">Why Deepfake Detection is Crucial</div>
        """)
        
        # Vertical card layout for the "Why Deepfake Detection is Crucial" section
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("""
                <div class="precaution-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 1.5em; margin-bottom: 10px; text-align: center;">🗞️</div>
                    <strong style="text-align: center; display: block;">Public Trust in Media</strong>
                    <p style="text-align: center;">Deepfakes undermine confidence in news sources and visual evidence</p>
                </div>
                """)
            
            with gr.Column(scale=1):
                gr.Markdown("""
                <div class="precaution-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 1.5em; margin-bottom: 10px; text-align: center;">👤</div>
                    <strong style="text-align: center; display: block;">Individual Privacy</strong>
                    <p style="text-align: center;">Protects individuals from having their likeness misused in fabricated content</p>
                </div>
                """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("""
                <div class="precaution-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 1.5em; margin-bottom: 10px; text-align: center;">🗳️</div>
                    <strong style="text-align: center; display: block;">Democratic Processes</strong>
                    <p style="text-align: center;">Prevents election manipulation through fake videos of politicians</p>
                </div>
                """)
            
            with gr.Column(scale=1):
                gr.Markdown("""
                <div class="precaution-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 1.5em; margin-bottom: 10px; text-align: center;">🔒</div>
                    <strong style="text-align: center; display: block;">Financial Security</strong>
                    <p style="text-align: center;">Helps prevent fraud through manipulated identity verification systems</p>
                </div>
                """)
        
        gr.Markdown("""
        <div class="animate-pulse tech-card">
        <h3>Our Motivation</h3>
        <p>As deepfake technology becomes increasingly sophisticated, distinguishing between real and fabricated media grows more challenging. 
        Our team is committed to developing reliable tools that can help maintain trust in digital content and protect individuals from manipulation.</p>
        </div>
        
        ### <div class="text-center">Our Technology & Workflow</div>
        
        <div class="workflow-diagram">
            <p><strong>Video Input</strong> → <strong>Preprocessing</strong> → <strong>Frame Splitting</strong></p>
            <p>↓</p>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 150px; padding: 10px;">
                    <strong>ResNext-50</strong><br>
                    <small>Spatial Feature Analysis</small>
                </div>
                <div style="flex: 1; min-width: 150px; padding: 10px;">
                    <strong>Vision Transformer (ViT)</strong><br>
                    <small>Advanced Pattern Recognition</small>
                </div>
                <div style="flex: 1; min-width: 150px; padding: 10px;">
                    <strong>Optical Flow</strong><br>
                    <small>Motion Analysis</small>
                </div>
            </div>
            <p>↓</p>
            <p><strong>Combined Output Analysis</strong> → <strong>Final Prediction</strong></p>
        </div>
        
        <div class="tech-card">
        <h4>Hybrid Detection Approach</h4>
        <p>Our system uses a multi-stream architecture that combines three powerful analysis methods: ResNext-50 for spatial features, Vision Transformer (ViT) for advanced pattern recognition, and Optical Flow analysis for temporal inconsistencies between frames.</p>
        </div>
        
        <div class="tech-card">
        <h4>Advanced Neural Networks</h4>
        <p>We utilize the power of ResNext-50 and Vision Transformer architectures to detect visual anomalies in individual frames, while simultaneously analyzing the temporal coherence using optical flow techniques.</p>
        </div>
        
        <div class="tech-card">
        <h4>Ensemble Prediction</h4>
        <p>By combining the outputs from all three analysis streams, our model achieves higher accuracy than any single approach. This ensemble technique helps identify deepfakes even when they might fool individual detection methods.</p>
        </div>
        
        ### <div class="text-center">Precautions When Using This Tool</div>
        """)
        
        # New vertical card layout for the "Precautions When Using This Tool" section
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("""
                <div class="precaution-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 1.5em; margin-bottom: 10px; text-align: center;">⚠️</div>
                    <strong style="text-align: center; display: block;">Verification Required</strong>
                    <p style="text-align: center;">Always seek expert verification for critical situations or legal matters</p>
                </div>
                """)
            
            with gr.Column(scale=1):
                gr.Markdown("""
                <div class="precaution-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 1.5em; margin-bottom: 10px; text-align: center;">🔍</div>
                    <strong style="text-align: center; display: block;">Context Matters</strong>
                    <p style="text-align: center;">Consider the source, purpose, and distribution channel of the video</p>
                </div>
                """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("""
                <div class="precaution-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 1.5em; margin-bottom: 10px; text-align: center;">🔄</div>
                    <strong style="text-align: center; display: block;">Stay Updated</strong>
                    <p style="text-align: center;">Deepfake technology evolves rapidly, requiring continuous improvement of detection tools</p>
                </div>
                """)
            
            with gr.Column(scale=1):
                gr.Markdown("""
                <div class="precaution-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 1.5em; margin-bottom: 10px; text-align: center;">⚖️</div>
                    <strong style="text-align: center; display: block;">False Positives</strong>
                    <p style="text-align: center;">No detection system is perfect; some legitimate videos may be incorrectly flagged</p>
                </div>
                """)
        
        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("""
                <div class="precaution-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 1.5em; margin-bottom: 10px; text-align: center;">📢</div>
                    <strong style="text-align: center; display: block;">Report Responsibly</strong>
                    <p style="text-align: center;">If you identify malicious deepfakes, report them to appropriate authorities</p>
                </div>
                """)

    return about

# Credits page content
def credits_page():
    with gr.Column(elem_classes="container") as credits:
        gr.Markdown("""
        # <div class="text-center"><span style="background: linear-gradient(90deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Project Credits</span></div>
        
        ### <div class="text-center">Our Team</div>
        """)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                <div class="credit-card">
                    <div style="font-size: 2em; margin-right: 12px;">👩‍🎓</div>
                    <div>
                        <h4>Manasi Khaire</h4>
                        <p>BE Computer</p>
                    </div>
                </div>
                
                <div class="credit-card">
                    <div style="font-size: 2em; margin-right: 12px;">👩‍🎓</div>
                    <div>
                        <h4>Pavitra Desai</h4>
                        <p>BE Computer</p>
                    </div>
                </div>
                """)
                
            with gr.Column():
                gr.Markdown("""
                <div class="credit-card">
                    <div style="font-size: 2em; margin-right: 12px;">👩‍🎓</div>
                    <div>
                        <h4>Sai Nagane</h4>
                        <p>BE Computer</p>
                    </div>
                </div>
                
                <div class="credit-card">
                    <div style="font-size: 2em; margin-right: 12px;">👩‍🎓</div>
                    <div>
                        <h4>Siddhi Algude</h4>
                        <p>BE Computer</p>
                    </div>
                </div>
                """)
        
        gr.Markdown("""
        <div class="credit-card">
            <div style="font-size: 2em; margin-right: 12px;">👨‍🏫</div>
            <div>
                <h4>Prof. Kiran Yesugade</h4>
                <p>Project Guide</p>
            </div>
        </div>
        
        <div class="credit-card">
            <div style="font-size: 2em; margin-right: 12px;">🏛️</div>
            <div>
                <h4>Bharati Vidyapeeth's College of Engineering for Women</h4>
                <p>Department of Computer Engineering</p>
            </div>
        </div>
        
        ### <div class="text-center">Technologies Used</div>
        
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin: 20px 0;">
            <div style="text-align: center; margin: 10px;">
                <div style="font-size: 2em; margin-bottom: 5px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="#EE4C2C" viewBox="0 0 24 24">
                        <path d="M12.005 0L4.952 7.053l14.1 14.1 7.053-7.053-14.1-14.1zM4.952 7.053l7.053 7.053-7.053 7.053L0 16.005l4.952-8.952z"/>
                    </svg>
                </div>
                <div>PyTorch</div>
            </div>
            <div style="text-align: center; margin: 10px;">
                <div style="font-size: 2em; margin-bottom: 5px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 11.08V8l-6-6H6a2 2 0 0 0-2 2v16c0 1.1.9 2 2 2h12a2 2 0 0 0 2-2v-3.08"></path>
                        <path d="M18 14h-5l1-2h4"></path>
                        <rect x="12" y="14" width="6" height="4" rx="1"></rect>
                    </svg>
                </div>
                <div>ResNext-50</div>
            </div>
            <div style="text-align: center; margin: 10px;">
                <div style="font-size: 2em; margin-bottom: 5px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2 L2 7 L12 12 L22 7 L12 2"/>
                        <path d="M2 17 L12 22 L22 17"/>
                        <path d="M2 12 L12 17 L22 12"/>
                    </svg>
                </div>
                <div>Vision Transformer</div>
            </div>
            <div style="text-align: center; margin: 10px;">
                <div style="font-size: 2em; margin-bottom: 5px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                </div>
                <div>Optical Flow</div>
            </div>
            <div style="text-align: center; margin: 10px;">
                <div style="font-size: 2em; margin-bottom: 5px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ff6b6b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="9" y1="3" x2="9" y2="21"></line>
                        <line x1="15" y1="3" x2="15" y2="21"></line>
                        <line x1="3" y1="9" x2="21" y2="9"></line>
                        <line x1="3" y1="15" x2="21" y2="15"></line>
                    </svg>
                </div>
                <div>Gradio</div>
            </div>
            <div style="text-align: center; margin: 10px;">
                <div style="font-size: 2em; margin-bottom: 5px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 6 9 17l-5-5"></path>
                    </svg>
                </div>
                <div>Ensemble Learning</div>
            </div>
        </div>
        """)
    
    return credits

# Create the Gradio interface with tabs
with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    with gr.Tabs():
        with gr.TabItem("🏠 Home", id=0):
            home_page()
        
        with gr.TabItem("ℹ️ About", id=1):
            about_page()
            
        with gr.TabItem("👥 Credits", id=2):
            credits_page()

# Launch the app
if __name__ == "__main__":
    demo.launch()

