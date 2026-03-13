# feature_extractor.py — Forensic Feature Extraction from Video Frames
import cv2
import numpy as np
from scipy.fft import dctn, fft2, fftshift
from scipy.stats import kurtosis
from skimage.metrics import structural_similarity as ssim
from skimage.feature import local_binary_pattern
from concurrent.futures import ThreadPoolExecutor

IMG_SIZE = 224

# ── Cascades ────────────────────────────────────────────────────────
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")


def _compute_gan_noise_score(frames: list[np.ndarray]) -> float:
    """
    GAN noise detection using DCT high-frequency analysis.
    Relaxed thresholds to avoid false positives on high-res real videos.
    """
    hf_ratios = []
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
        # Gentle sharpening
        sharpen_kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
        gray_sharp = cv2.filter2D(gray, -1, sharpen_kernel)
        
        dct = dctn(gray_sharp, norm="ortho")
        h, w = dct.shape

        # Measure energy in the highest frequency quadrant
        hf_energy = np.sum(np.abs(dct[int(h*0.5):, int(w*0.5):])) + 1e-8
        total_energy = np.sum(np.abs(dct)) + 1e-8
        hf_ratios.append(hf_energy / total_energy)

    avg_ratio = float(np.mean(hf_ratios))
    # Thresholds: Real high-res can hit 0.1-0.15; GANs hit 0.25-0.4
    score = np.clip((avg_ratio - 0.18) / 0.2, 0.0, 1.0)
    return round(float(score), 3)


def _compute_face_blending_score(frames: list[np.ndarray]) -> float:
    """Detect boundary artifacts. Relaxed to handle shadows/beards/glasses."""
    boundary_scores = []
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)
        if len(faces) == 0: continue

        x, y, w, h = faces[0]
        mask = np.zeros_like(gray)
        cv2.ellipse(mask, (x + w // 2, y + h // 2), (int(w*0.45), int(h*0.45)), 0, 0, 360, 255, -1)

        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)

        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(mask, kernel, iterations=1)
        boundary = cv2.bitwise_xor(dilated, mask)

        boundary_grad = np.mean(grad_mag[boundary > 0]) if np.any(boundary > 0) else 0
        interior_grad = np.mean(grad_mag[mask > 0]) if np.any(mask > 0) else 1e-8

        # Ratio must be high for a fake (~2.5-4.0). Real is ~1.0-1.8.
        ratio = boundary_grad / (interior_grad + 1e-8)
        boundary_scores.append(ratio)

    if not boundary_scores: return 0.0
    avg = float(np.mean(boundary_scores))
    score = np.clip((avg - 2.2) / 1.8, 0.0, 1.0)
    return round(float(score), 3)


def _compute_temporal_jump_score(frames: list[np.ndarray]) -> float:
    """Measure temporal discontinuities. Handle camera shake/motion better."""
    if len(frames) < 5: return 0.0
    ssim_values = []
    for i in range(len(frames) - 1):
        gray_a = cv2.resize(cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY), (128, 128))
        gray_b = cv2.resize(cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY), (128, 128))
        ssim_values.append(ssim(gray_a, gray_b))

    ssim_arr = np.array(ssim_values)
    # Use median-based jump detection (more robust than mean)
    med_ssim = np.median(ssim_arr)
    # Significant drops below median
    jumps = np.sum(ssim_arr < (med_ssim * 0.75))
    jump_ratio = jumps / len(ssim_values)
    
    score = np.clip(jump_ratio * 3.0 + np.var(ssim_arr) * 15, 0.0, 1.0)
    return round(float(score), 3)


def _compute_lip_sync_error(frames: list[np.ndarray]) -> float:
    """Optical flow inconsistency in mouth. Lowered sensitivity."""
    if len(frames) < 5: return 0.0
    flow_ratios = []
    for i in range(len(frames) - 1):
        gray_a = cv2.resize(cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY), (128, 128))
        gray_b = cv2.resize(cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY), (128, 128))
        flow = cv2.calcOpticalFlowFarneback(gray_a, gray_b, None, 0.5, 3, 10, 3, 5, 1.2, 0)
        mag = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        upper = np.mean(mag[:64, :]) + 1e-8
        lower = np.mean(mag[90:, :]) + 1e-8
        flow_ratios.append(lower/upper)

    # Real people have high variance in mouth motion. 
    # Only extreme variance or total zero variance should trigger.
    variance = float(np.var(flow_ratios))
    score = np.clip((variance - 0.15) * 4.0, 0.0, 1.0) if variance > 0.15 else 0.0
    return round(float(score), 3)


def _compute_eye_blink_anomaly(frames: list[np.ndarray]) -> float:
    """Fixed eye blink logic to avoid false positives on short clips."""
    eyes_per_frame = []
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyes = eye_cascade.detectMultiScale(gray, 1.1, 5)
        eyes_per_frame.append(len(eyes))

    # For short clips (32 frames ~1s), NO blinks is NORMAL.
    # Only flag as anomalous if it's a long video (>5s) with zero blinks.
    if len(frames) < 60: return 0.0 
    
    arr = np.array(eyes_per_frame)
    if np.all(arr >= 1): # Constant open eyes on long clip
        return 0.4
    return 0.0


def _compute_lighting_inconsistency(frames: list[np.ndarray]) -> float:
    """Substantially relaxed to handle natural uneven lighting."""
    diffs = []
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0: continue
        x, y, w, h = faces[0]
        face_mean = np.mean(gray[y:y+h, x:x+w])
        bg_mean = np.mean(gray[gray > 0]) # Crude global mean
        diffs.append(abs(face_mean - bg_mean) / 255.0)

    if not diffs: return 0.0
    # Higher threshold (0.25) to account for natural exposure diffs
    score = np.clip((np.mean(diffs) - 0.25) * 1.5, 0.0, 1.0)
    return round(float(score), 3)


def _compute_background_coherence(frames: list[np.ndarray]) -> float:
    """Check for background warping. Relaxed for handheld camera shake."""
    if len(frames) < 5: return 0.0
    bg_motions = []
    for i in range(len(frames) - 1):
        gray_a = cv2.resize(cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY), (128, 128))
        gray_b = cv2.resize(cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY), (128, 128))
        flow = cv2.calcOpticalFlowFarneback(gray_a, gray_b, None, 0.5, 3, 10, 3, 5, 1.2, 0)
        bg_motions.append(np.mean(np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)))

    avg_motion = float(np.mean(bg_motions))
    # Handheld shake can easily hit 1.0-2.0. Fake warping is higher or glitchy.
    score = np.clip((avg_motion - 2.5) / 5.0, 0.0, 1.0)
    return round(float(score), 3)


def _compute_spectral_centroid_score(frames: list[np.ndarray]) -> float:
    """
    Detects 'checkerboard' artifacts common in GANs by analyzing 2D FFT 
    energy distribution. Real videos have a smooth decay of energy.
    """
    centroids = []
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        f_transform = fft2(gray)
        f_shift = fftshift(f_transform)
        magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1)
        
        # Calculate centroid of the magnitude spectrum
        h, w = magnitude_spectrum.shape
        y, x = np.ogrid[:h, :w]
        total_mag = np.sum(magnitude_spectrum) + 1e-8
        
        # In natural images, energy is centered at DC (middle). 
        # AI often has high-freq spikes far from center.
        cx = np.sum(x * magnitude_spectrum) / total_mag
        cy = np.sum(y * magnitude_spectrum) / total_mag
        
        # Distance from center
        dist = np.sqrt((cx - w/2)**2 + (cy - h/2)**2)
        centroids.append(dist)
    
    avg_dist = float(np.mean(centroids))
    # Threshold: AI tends to have dispersed spectral energy
    score = np.clip((avg_dist - 5.0) / 15.0, 0.0, 1.0)
    return round(score, 3)


def _compute_texture_regularity_score(frames: list[np.ndarray]) -> float:
    """
    Uses Local Binary Patterns (LBP) to measure skin texture 'perfection'.
    AI skin is often too uniform or lacks the micro-variations of real skin.
    """
    regularity_vals = []
    # LBP parameters
    P = 8 # points
    R = 1 # radius
    
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply LBP
        lbp = local_binary_pattern(gray, P, R, method="uniform")
        
        # Calculate histogram: uniform LBP produces P+2 bins
        (hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, P + 3), range=(0, P + 2))
        hist = hist.astype("float")
        hist /= (hist.sum() + 1e-8)
        
        # 'Too uniform' skin has a very high peak in one bin
        regularity_vals.append(np.max(hist))
        
    avg_reg = float(np.mean(regularity_vals))
    # AI skin hits ~0.6-0.8; Real skin with pores/imperfections is ~0.3-0.5
    score = np.clip((avg_reg - 0.55) * 2.5, 0.0, 1.0)
    return round(score, 3)


def extract_forensic_features(frames: list[np.ndarray], model_probability: float, media_type: str = "video") -> dict:
    feature_funcs = {
        "gan_noise": _compute_gan_noise_score,
        "face_blending": _compute_face_blending_score,
        "temporal_jump": _compute_temporal_jump_score,
        "lip_sync_error": _compute_lip_sync_error,
        "eye_blink_anomaly": _compute_eye_blink_anomaly,
        "lighting_inconsistency": _compute_lighting_inconsistency,
        "background_coherence": _compute_background_coherence,
        "spectral_artifact": _compute_spectral_centroid_score,
        "texture_perfection": _compute_texture_regularity_score,
    }

    # Run features in parallel for massive speedup
    features = {}
    with ThreadPoolExecutor(max_workers=len(feature_funcs)) as executor:
        future_to_name = {executor.submit(func, frames): name for name, func in feature_funcs.items()}
        for future in future_to_name:
            name = future_to_name[future]
            try:
                features[name] = future.result()
            except Exception as e:
                print(f"⚠️  Feature '{name}' failed: {e}")
                features[name] = 0.0

    return {
        "media_type": media_type,
        "model_probability": round(model_probability, 4),
        "features": features,
    }
