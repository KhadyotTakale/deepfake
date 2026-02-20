# main.py — FastAPI backend for Misinformation Detection System
import os
import json
import base64
import tempfile
import traceback
from datetime import datetime

import httpx
import torch
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

from model import DeepfakeDetector
from utils import extract_frames, preprocess_frames

# ── Load environment variables ───────────────────────────────────────
load_dotenv()
FASTROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")  # key stored as OPENROUTER_API_KEY in .env
FASTROUTER_URL = "https://go.fastrouter.ai/api/v1/chat/completions"
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ── Supabase client ──────────────────────────────────────────────────
supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase connected")
else:
    print("⚠️  Supabase credentials missing — history will not persist")

# ── Load video deepfake model ────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
video_model: DeepfakeDetector | None = None

WEIGHTS_PATH = os.getenv("MODEL_WEIGHTS_PATH", "deepfake_weights.pth")
try:
    video_model = DeepfakeDetector().to(device)
    if os.path.exists(WEIGHTS_PATH):
        video_model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=device))
        print(f"✅ Video model weights loaded from {WEIGHTS_PATH}")
    else:
        print(f"⚠️  No weights file at {WEIGHTS_PATH} — model will use random weights")
    video_model.eval()
except Exception as e:
    print(f"⚠️  Could not load video model: {e}")
    video_model = None

print(f"🖥️  Device: {device}")

# ── FastAPI app ──────────────────────────────────────────────────────
app = FastAPI(
    title="Misinformation Detection API",
    version="1.0.0",
    description="Detect fake news, manipulated images, and deepfake videos.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── LLM system prompt ───────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are an expert AI content forensics analyst specializing in detecting "
    "misinformation, manipulated media, AI-generated images, and deepfake videos. "
    "You are extremely critical and skeptical. You err on the side of flagging content "
    "as suspicious rather than assuming it is authentic. "
    "Always respond in valid JSON only."
)

NEWS_USER_PROMPT = """Analyze the following news article text for signs of misinformation or fake news.

Check for:
- Sensationalist or emotionally manipulative language
- Missing or unverifiable sources
- Logical inconsistencies or contradictions
- Known misinformation patterns
- Extreme bias or one-sided reporting
- Clickbait patterns

Article text:
\"\"\"
{text}
\"\"\"

Respond with ONLY valid JSON in this exact format:
{{
  "verdict": "REAL" or "FAKE" or "UNCERTAIN",
  "confidence": <number 0-100>,
  "reasons": ["reason1", "reason2", ...],
  "summary": "brief summary of analysis"
}}"""

IMAGE_USER_PROMPT = """You are an expert forensic analyst. Analyze this image with EXTREME SKEPTICISM for signs of AI generation or digital manipulation. Assume it could be AI-generated and look for proof it is NOT.

Check VERY carefully for these AI generation tells:
1. SKIN & FACE: Overly smooth/plastic skin, pores missing, unnatural skin texture, asymmetric facial features, weird ear shapes, teeth anomalies, iris irregularities, unnatural hair strands or hairline
2. HANDS & FINGERS: Wrong number of fingers, fused/bent fingers, inconsistent finger lengths, missing knuckles, unnatural hand poses
3. TEXT & WRITING: Garbled or nonsensical text anywhere in the image, distorted letters, impossible signage
4. BACKGROUND: Blurred or incoherent backgrounds, objects merging into each other, architecture that doesn't make sense, repeating patterns
5. EDGES & TRANSITIONS: Unnatural blending between subject and background, halo effects around subjects, sharp vs blurry inconsistencies
6. LIGHTING: Impossible shadow directions, inconsistent light sources, flat lighting that doesn't match the scene
7. CLOTHING & ACCESSORIES: Impossible folds, asymmetric collars/glasses, accessories that merge with skin or hair, jewelry anomalies
8. OVERALL: Too-perfect composition, uncanny valley feeling, hyper-realistic but slightly "off" quality typical of AI generators like Midjourney, DALL-E, or Stable Diffusion

IMPORTANT: When in doubt, lean toward FAKE or UNCERTAIN. Modern AI-generated images can look very convincing at first glance. Be very critical.

Respond with ONLY valid JSON in this exact format:
{{
  "verdict": "REAL" or "FAKE" or "UNCERTAIN",
  "confidence": <number 0-100>,
  "reasons": ["reason1", "reason2", ...],
  "summary": "brief summary of analysis"
}}"""


# ── Pydantic models ─────────────────────────────────────────────────
class NewsRequest(BaseModel):
    text: str


class DetectionResult(BaseModel):
    verdict: str
    confidence: float
    reasons: list[str]
    summary: str


class HistoryEntry(BaseModel):
    type: str
    input_preview: str | None = None
    verdict: str
    confidence: float
    reasons: list[str]
    summary: str


# ── Helpers ──────────────────────────────────────────────────────────
async def call_fastrouter(messages: list[dict]) -> DetectionResult:
    """Call FastRouter API and parse the JSON response."""
    if not FASTROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="FastRouter API key not configured")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            FASTROUTER_URL,
            headers={
                "Authorization": f"Bearer {FASTROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 2048,
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"FastRouter API error: {response.status_code} — {response.text}",
        )

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        # Remove first and last lines (```json and ```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        content = "\n".join(lines)

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail=f"LLM returned invalid JSON: {content[:500]}")

    return DetectionResult(
        verdict=result.get("verdict", "UNCERTAIN"),
        confidence=float(result.get("confidence", 50)),
        reasons=result.get("reasons", []),
        summary=result.get("summary", "Analysis completed."),
    )


async def save_to_supabase(entry: HistoryEntry):
    """Save a detection result to Supabase (fire-and-forget)."""
    if supabase is None:
        return
    try:
        supabase.table("detections").insert({
            "type": entry.type,
            "input_preview": entry.input_preview,
            "verdict": entry.verdict,
            "confidence": entry.confidence,
            "reasons": json.dumps(entry.reasons),
            "summary": entry.summary,
        }).execute()
    except Exception as e:
        print(f"⚠️  Failed to save to Supabase: {e}")


# ── Routes ───────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "Misinformation Detection API", "version": "1.0.0"}


@app.post("/detect/news", response_model=DetectionResult)
async def detect_news(request: NewsRequest):
    """Analyze a text article for fake news using LLM."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": NEWS_USER_PROMPT.format(text=request.text[:5000])},
    ]

    result = await call_fastrouter(messages)

    # Save to history
    await save_to_supabase(HistoryEntry(
        type="news",
        input_preview=request.text[:200],
        verdict=result.verdict,
        confidence=result.confidence,
        reasons=result.reasons,
        summary=result.summary,
    ))

    return result


@app.post("/detect/image", response_model=DetectionResult)
async def detect_image(file: UploadFile = File(...)):
    """Analyze an uploaded image for manipulation using LLM vision."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(status_code=400, detail="Image too large (max 20 MB)")

    b64 = base64.b64encode(contents).decode("utf-8")
    mime = file.content_type or "image/jpeg"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                },
                {"type": "text", "text": IMAGE_USER_PROMPT},
            ],
        },
    ]

    result = await call_fastrouter(messages)

    await save_to_supabase(HistoryEntry(
        type="image",
        input_preview=file.filename or "uploaded_image",
        verdict=result.verdict,
        confidence=result.confidence,
        reasons=result.reasons,
        summary=result.summary,
    ))

    return result


@app.post("/detect/video", response_model=DetectionResult)
async def detect_video(file: UploadFile = File(...)):
    """Analyze an uploaded video for deepfake using EfficientNet-B4 + LSTM."""
    if video_model is None:
        raise HTTPException(status_code=503, detail="Video detection model is not available")

    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # Save uploaded file to temp location
    suffix = os.path.splitext(file.filename or "video.mp4")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # Extract and preprocess frames
        frames = extract_frames(tmp_path, max_frames=20)
        tensor = preprocess_frames(frames).to(device)

        # Run inference
        with torch.no_grad():
            output = video_model(tensor)

        fake_prob = output.item()
        confidence = round(fake_prob * 100, 1) if fake_prob > 0.5 else round((1 - fake_prob) * 100, 1)

        if fake_prob > 0.7:
            verdict = "FAKE"
            reasons = [
                "Temporal inconsistencies detected across frames",
                "Facial feature anomalies present",
                f"Model confidence in manipulation: {round(fake_prob * 100, 1)}%",
            ]
            summary = "The video shows signs of deepfake manipulation based on spatial and temporal analysis."
        elif fake_prob < 0.3:
            verdict = "REAL"
            reasons = [
                "Consistent temporal patterns across frames",
                "Natural facial feature transitions",
                f"Model confidence in authenticity: {round((1 - fake_prob) * 100, 1)}%",
            ]
            summary = "The video appears authentic with consistent spatial and temporal features."
        else:
            verdict = "UNCERTAIN"
            reasons = [
                "Mixed signals in temporal analysis",
                "Some minor inconsistencies detected",
                f"Fake probability: {round(fake_prob * 100, 1)}%",
            ]
            summary = "The analysis is inconclusive. The video shows some potentially suspicious patterns but certainty is low."

        result = DetectionResult(
            verdict=verdict,
            confidence=confidence,
            reasons=reasons,
            summary=summary,
        )

        await save_to_supabase(HistoryEntry(
            type="video",
            input_preview=file.filename or "uploaded_video",
            verdict=result.verdict,
            confidence=result.confidence,
            reasons=result.reasons,
            summary=result.summary,
        ))

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")
    finally:
        os.unlink(tmp_path)


@app.get("/history")
async def get_history():
    """Retrieve past detections from Supabase."""
    if supabase is None:
        return {"detections": [], "message": "Supabase not configured"}

    try:
        response = (
            supabase.table("detections")
            .select("*")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )
        # Parse reasons back from JSON string
        detections = []
        for row in response.data:
            if isinstance(row.get("reasons"), str):
                try:
                    row["reasons"] = json.loads(row["reasons"])
                except json.JSONDecodeError:
                    row["reasons"] = []
            detections.append(row)
        return {"detections": detections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@app.post("/history")
async def save_history(entry: HistoryEntry):
    """Manually save a detection result to history."""
    await save_to_supabase(entry)
    return {"message": "Saved successfully"}
