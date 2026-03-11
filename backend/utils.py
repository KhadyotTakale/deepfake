# utils.py — Video preprocessing utilities
import cv2
import numpy as np
import torch
import torchvision.transforms as transforms

IMG_SIZE = 224
MAX_FRAMES = 32  # Increased for better temporal resolution

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
