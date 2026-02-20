# utils.py — Video preprocessing utilities
# Carries over face detection + frame extraction from the original project,
# adapted for the new EfficientNet-B4 + LSTM pipeline.

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms

IMG_SIZE = 224
MAX_FRAMES = 20  # Max frames to sample from video

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


def crop_face(frame: np.ndarray) -> np.ndarray | None:
    """Detect and crop the first face in a frame using Haar Cascades."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    return frame[y : y + h, x : x + w]


def extract_frames(video_path: str, max_frames: int = MAX_FRAMES) -> list[np.ndarray]:
    """
    Read a video file, detect faces per frame, and return up to `max_frames`
    evenly-sampled face crops resized to IMG_SIZE × IMG_SIZE.

    Falls back to the full frame (center-cropped) if no face is found.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        raise ValueError("Video has no readable frames")

    # Determine which frame indices to sample
    if total_frames <= max_frames:
        sample_indices = list(range(total_frames))
    else:
        sample_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int).tolist()

    frames: list[np.ndarray] = []
    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, frame = cap.read()
        if not success:
            continue

        face = crop_face(frame)
        if face is not None:
            face_resized = cv2.resize(face, (IMG_SIZE, IMG_SIZE))
            frames.append(face_resized)
        else:
            # No face detected — use center crop of full frame as fallback
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
    Convert a list of BGR numpy frames into a batched tensor suitable
    for the DeepfakeDetector model.

    Returns:
        Tensor of shape (1, seq_len, 3, IMG_SIZE, IMG_SIZE)
    """
    tensors = []
    for frame in frames:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensors.append(frame_transform(rgb))

    # Stack: (seq_len, 3, H, W) → unsqueeze batch dim → (1, seq_len, 3, H, W)
    return torch.stack(tensors).unsqueeze(0)
