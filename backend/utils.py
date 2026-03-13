# utils.py — Video preprocessing utilities
import cv2
import numpy as np
import torch
import base64
import torchvision.transforms as transforms
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

IMG_SIZE = 224
MAX_FRAMES = 24  # Balanced for speed and temporal resolution
VISION_RESIZE = 768 # Standardize vision input for speed/accuracy balance

# ImageNet normalization (standard for EfficientNet)
frame_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# OpenCV Haar Cascade face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def crop_face(frame: np.ndarray, padding: float = 0.2) -> np.ndarray | None:
    """
    Detect and crop the first face in a frame using Haar Cascades.
    Adds padding around the detected face for better forensic visibility.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))
    if len(faces) == 0:
        return None
    
    x, y, w, h = faces[0]
    
    # Add padding
    pad_h = int(h * padding)
    pad_w = int(w * padding)
    
    y1 = max(0, y - pad_h)
    y2 = min(frame.shape[0], y + h + pad_h)
    x1 = max(0, x - pad_w)
    x2 = min(frame.shape[1], x + w + pad_w)
    
    return frame[y1:y2, x1:x2]


def extract_frames(video_path: str, max_frames: int = MAX_FRAMES) -> list[np.ndarray]:
    """
    Read a video file, detect faces per frame, and return up to `max_frames`
    evenly-sampled face crops resized to IMG_SIZE × IMG_SIZE.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        raise ValueError("Video has no readable frames")

    # Sample more frames initially to find the ones with faces
    initial_sample_count = min(total_frames, max_frames * 2)
    sample_indices = np.linspace(0, total_frames - 1, initial_sample_count, dtype=int).tolist()

    frames: list[np.ndarray] = []
    faces_detected = 0
    
    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, frame = cap.read()
        if not success:
            continue

        face = crop_face(frame)
        if face is not None:
            face_resized = cv2.resize(face, (IMG_SIZE, IMG_SIZE))
            frames.append(face_resized)
            faces_detected += 1
            if len(frames) >= max_frames:
                break

    print(f"  📸 Frame extraction complete: {len(frames)} frames ({faces_detected} faces found)")

    # Final fallback if too few faces detected: fill with center crops
    if len(frames) < max_frames // 2:
        print(f"  ⚠️  Low face detection rate ({faces_detected}/{len(sample_indices)}). Falling back to center crops.")
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        for _ in range(max_frames - len(frames)):
            success, frame = cap.read()
            if not success: break
            h, w = frame.shape[:2]
            min_dim = min(h, w)
            top = (h - min_dim) // 2
            left = (w - min_dim) // 2
            center_crop = frame[top : top + min_dim, left : left + min_dim]
            frames.append(cv2.resize(center_crop, (IMG_SIZE, IMG_SIZE)))

    cap.release()

    if len(frames) == 0:
        raise ValueError("No usable frames extracted from video")

    return frames


def preprocess_frames(frames: list[np.ndarray]) -> torch.Tensor:
    """
    Convert a list of BGR numpy frames into a batched tensor.
    """
    tensors = []
    for frame in frames:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensors.append(frame_transform(rgb))

    return torch.stack(tensors).unsqueeze(0)
def unified_frame_extraction(
    video_path: str, 
    cnn_count: int = 14, 
    vision_count: int = 6
) -> tuple[list[np.ndarray], torch.Tensor, list[str]]:
    """
    High-accuracy frame extraction for both CNN and LLM Vision.
    Sampling more frames improves detection of fleeting artifacts.
    """
    cap = cv2.VideoCapture(video_path)
    try:
        if not cap.isOpened():
            raise ValueError("Cannot open video")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample indices for CNN (robust temporal sequence)
        cnn_indices = np.linspace(0, total_frames - 1, cnn_count, dtype=int)
        # Sample indices for Vision (dense coverage for artifact hunting)
        vision_indices = np.linspace(0, total_frames - 1, vision_count, dtype=int)
        
        all_indices = sorted(list(set(cnn_indices) | set(vision_indices)))
        
        raw_frames = []
        cnn_frames = []
        vision_b64 = []
        
        for idx in all_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            success, frame = cap.read()
            if not success: continue

            # 1. Process for CNN/Forensics (All frames in all_indices get this)
            # Try to crop face for better focus, fallback to center crop
            face = crop_face(frame)
            if face is None:
                h, w = frame.shape[:2]
                size = min(h, w)
                face = frame[(h-size)//2:(h+size)//2, (w-size)//2:(w+size)//2]
            
            face_resized = cv2.resize(face, (IMG_SIZE, IMG_SIZE))
            
            if idx in cnn_indices:
                cnn_frames.append(face_resized)
                raw_frames.append(face_resized)

            # 2. Process for Vision (Only for vision_indices)
            if idx in vision_indices:
                # Use the face crop if available for vision too, as it's where the deepfake is
                vis_frame = cv2.resize(face, (512, 512)) # 512 is plenty for vision reasoning
                _, buffer = cv2.imencode(".jpg", vis_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                vision_b64.append(base64.b64encode(buffer).decode("utf-8"))
    finally:
        cap.release()
    
    # 3. Create tensor
    tensors = [frame_transform(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)) for f in cnn_frames]
    tensor = torch.stack(tensors).unsqueeze(0)
    
    return raw_frames, tensor, vision_b64


def generate_spectrogram(audio_path: str) -> str:
    """
    ULTRA-HIGH RESOLUTION Spectrogram generation for forensic analysis.
    Uses MAGMA colormap for better contrast in energy distribution.
    """
    # Use 44.1kHz sampling for full-spectrum forensic clarity
    y, sr = librosa.load(audio_path, sr=44100, duration=10)
    
    # Analyze up to 20kHz (top of human hearing) where many AI artifacts hide
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=256, n_fft=2048, hop_length=512, fmax=20000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    
    # Percentile-based normalization (Focus on 5th to 95th percentile)
    # This ensures quiet voices are amplified and loud ones don't wash out details
    vmin = np.percentile(S_dB, 5)
    vmax = np.percentile(S_dB, 98) # Catch the peaks
    img = np.clip((S_dB - vmin) / (vmax - vmin + 1e-8) * 255, 0, 255)
    img = img.astype(np.uint8)
    
    # Wide format (1200x600) for better temporal speech pattern inspection
    img = cv2.resize(img, (1200, 600))
    img = cv2.applyColorMap(img, cv2.COLORMAP_MAGMA)
    img = cv2.flip(img, 0)
    
    # Max quality JPG
    _, buffer = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    return base64.b64encode(buffer).decode("utf-8")


def fast_resize_image(image_bytes: bytes, max_dim: int = 768) -> str:
    """
    Resizes an image while preserving aspect ratio and returns base64 string.
    Massively reduces payload size and LLM processing time.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Invalid image data")

    h, w = image.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    success, encoded_image = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if not success:
        raise ValueError("Failed to encode image")
    
    return base64.b64encode(encoded_image).decode("utf-8")
