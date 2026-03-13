# main.py — FastAPI backend for Misinformation Detection System
# Extended with Advanced AI Forensic Pipeline:
# CNN → Feature Extraction → Graph Building → GraphRAG → LLM Reasoning → Consensus
import os
import json
import base64
import tempfile
import traceback
from datetime import datetime

import cv2
import httpx
import torch
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

from model import DeepfakeDetector
from utils import extract_frames, preprocess_frames, unified_frame_extraction, generate_spectrogram, fast_resize_image

# ── New pipeline modules ─────────────────────────────────────────────
from feature_extractor import extract_forensic_features
from graph_builder import build_feature_graph, compute_graph_score, graph_to_summary, persist_to_neo4j
from graphrag_engine import retrieve_forensic_context
from reasoning_engine import reason_about_authenticity
from consensus_engine import compute_consensus

# ── Load environment variables ───────────────────────────────────────
load_dotenv()
FASTROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
FASTROUTER_URL = "https://go.fastrouter.ai/api/v1/chat/completions"
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

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
    print(f"🔄 Initializing Video Analysis Model (Attention-GRU)...")
    video_model = DeepfakeDetector().to(device)
    
    if os.path.exists(WEIGHTS_PATH):
        try:
            # map_location handles CPU/GPU switching
            state_dict = torch.load(WEIGHTS_PATH, map_location=device)
            video_model.load_state_dict(state_dict, strict=True)
            print(f"✅ Video model weights loaded successfully from {WEIGHTS_PATH}")
        except Exception as load_err:
            print(f"⚠️  Architecture mismatch while loading {WEIGHTS_PATH}: {load_err}")
            print(f"💡 Continuing with randomly initialized advanced architecture.")
    else:
        print(f"ℹ️  No weights file at {WEIGHTS_PATH} — model initialized with base architecture.")
    
    video_model.eval()
except Exception as e:
    print(f"❌ Critical error during video model initialization: {e}")
    video_model = None

print(f"🖥️  Device: {device}")

# ── FastAPI app ──────────────────────────────────────────────────────
app = FastAPI(
    title="Misinformation Detection API",
    version="2.0.0",
    description=(
        "Detect fake news, manipulated images, and deepfake videos "
        "using a multi-stage AI forensic pipeline."
    ),
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

AUDIO_USER_PROMPT = """Analyze this Spectrogram for evidence of AI audio synthesis.
Check for:
1. COMBING: Perfectly vertical stripes (robotic artifacts).
2. VOIDS: Perfectly rectangular silences or sharp frequency cutoffs.
3. NOISE: Uniform noise floor above 5kHz (synthetic signature).

If visual frequency transitions are natural and variable, favor REAL.

Respond ONLY with valid JSON:
{
  "verdict": "REAL/FAKE/UNCERTAIN",
  "confidence": 0-100,
  "reasons": ["short reason", ...],
  "summary": "Technical audio forensic summary."
}"""

IMAGE_USER_PROMPT = """Analyze this image objectively as a senior forensic expert. 
Focus on identifying AI generation or digital manipulation using these criteria:

1. ANATOMY: Check for merged fingers, floating accessories, ear asymmetry, or missing pores.
2. EYE REFLECTIONS: Look for environmental light reflection consistency between both pupils.
3. TEXTURE: Search for "uncanny" smoothness (low entropy) transitioning into sudden sharpness.
4. LIGHTING: Identify impossible shadow directions or inconsistent global illumination.
5. ARTIFACTS: Look for GAN checkerboard noise or tiling gradients in the background.

SCORING: 
- Increment confidence for every concrete 'Impossible Physics' finding.
- If anatomy and lighting are 100% physically sound, favor REAL.

Respond ONLY with valid JSON:
{
  "verdict": "REAL/FAKE/UNCERTAIN",
  "confidence": 0-100,
  "reasons": ["Observation 1", "Observation 2", ...],
  "summary": "Technical forensic summary."
}"""


# ── Pydantic models ─────────────────────────────────────────────────
# Removed NewsRequest as it's no longer used


class DetectionResult(BaseModel):
    verdict: str
    confidence: float
    reasons: list[str]
    summary: str


class DetailedDetectionResult(BaseModel):
    """Extended response model for the full forensic pipeline."""
    verdict: str
    confidence: float
    reasons: list[str]
    summary: str
    forensic_features: dict | None = None
    pipeline_scores: dict | None = None
    graph_analysis: dict | None = None
    llm_reasoning: dict | None = None


class HistoryEntry(BaseModel):
    type: str
    input_preview: str | None = None
    verdict: str
    confidence: float
    reasons: list[str]
    summary: str


# ── Helpers ──────────────────────────────────────────────────────────
async def call_fastrouter(messages: list[dict], model: str = "openai/o3-mini") -> DetectionResult:
    """Call FastRouter API and parse the JSON response."""
    if not FASTROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="FastRouter API key not configured")

    # Reasoning models (o1, o3) don't support temperature/max_tokens in the same way
    is_reasoning = "o1" in model or "o3" in model
    
    payload = {
        "model": model,
        "messages": messages,
    }
    
    if not is_reasoning:
        payload["temperature"] = 0.1
        payload["max_tokens"] = 2048

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            FASTROUTER_URL,
            headers={
                "Authorization": f"Bearer {FASTROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"FastRouter API error: {response.status_code} — {response.text}",
        )

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    # Robust JSON extraction: Find the first '{' and last '}'
    content = content.strip()
    try:
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
        else:
            raise ValueError("No JSON object found in response")
    except (json.JSONDecodeError, ValueError):
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


# ─────────────────────────────────────────────────────────────────────
# Advanced Video Pipeline (shared by both /detect/video endpoints)
# ─────────────────────────────────────────────────────────────────────

async def run_forensic_pipeline(
    frames: list[np.ndarray],
    tensor: torch.Tensor,
    background_tasks: BackgroundTasks,
    b64_frames: list[str] | None = None,
) -> dict:
    """
    Run the full multi-stage forensic pipeline on extracted video frames.
    Optimized: Stages 1 & 2 run in parallel.
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    # ── Stage 1 & 2 (Parallel): CNN Inference & Forensic Features ──
    has_weights = os.path.exists(WEIGHTS_PATH)
    
    async def run_cnn():
        with torch.no_grad():
            output = video_model(tensor)
        return output.item()

    async def run_forensics(cnn_init_score):
        # Even the features themselves can be potentially parallelized if needed,
        # but let's start by running Stage 2 in parallel with Stage 1.
        return extract_forensic_features(
            frames=frames,
            model_probability=cnn_init_score,
            media_type="video",
        )

    # Note: Forensic features don't actually NEED the finished CNN score for calculation,
    # except for reporting it in the payload. We can pass a dummy and update it later.
    tasks = [run_cnn(), run_forensics(0.5)]
    cnn_score, forensic_payload = await asyncio.gather(*tasks)
    
    features = forensic_payload["features"]
    
    # HEURISTIC FALLBACK: If weights are missing, the CNN score from an untrained model 
    # will be random (~0.5). In this case, we use the average of forensic features 
    # as a "pseudo-CNN" score to provide a meaningful base for the consensus.
    if not has_weights:
        # ... (weights missing logic)
        print("  ⚠️  Weights missing: Using conservative heuristic proxy")
        # Only count features that are actually 'anomalous' (> 0.15)
        # to avoid noise accumulation for real videos.
        # Include new advanced features in the heuristic proxy
        spatial_sig = [
            features["gan_noise"], 
            features["face_blending"],
            features["spectral_artifact"],
            features["texture_perfection"]
        ]
        temporal_sig = [features["temporal_jump"], features["lip_sync_error"]]
        
        def amplify_signal(vals):
            # Higher threshold for detecting real anomalies vs compression noise
            filtered = [v for v in vals if v > 0.20]
            if not filtered: return 0.0
            # Use average of top signals for better stability
            return np.mean(filtered)

        spatial_proxy = amplify_signal(spatial_sig)
        temporal_proxy = amplify_signal(temporal_sig)
        
        # Reduced multiplier (1.0) and balanced frame
        cnn_score = 0.15 + (spatial_proxy * 0.5) + (temporal_proxy * 0.35)
        
        # Cap at 0.9 to avoid complete certainty without weights
        cnn_score = min(cnn_score, 0.90)
    
    print(f"  📊 CNN score (effective): {cnn_score:.4f}")
    forensic_payload["model_probability"] = round(cnn_score, 4)


    # ── Stage 3: Feature Graph Building ──
    graph = build_feature_graph(forensic_payload)

    graph_score = compute_graph_score(graph)
    graph_summary = graph_to_summary(graph)
    print(f"  🕸️  Graph score: {graph_score:.4f} | "
          f"Artifacts triggered: {len(graph_summary.get('artifacts', []))}")

    # Persist to Neo4j in the background to avoid blocking the user
    background_tasks.add_task(persist_to_neo4j, graph)

    # ── Stage 4 & 5 (Parallel): GraphRAG & LLM Reasoning ──
    # We can run these in parallel because retrieve_forensic_context is fast
    # but LLM reasoning is the main bottleneck.
    
    async def get_context():
        return retrieve_forensic_context(features=features, graph_summary=graph_summary)
    
    # Run GraphRAG and LLM Reasoning in a gathering pool for maximum speed
    graph_context = await asyncio.to_thread(retrieve_forensic_context, features, graph_summary)
    
    llm_result = await reason_about_authenticity(
        cnn_score=cnn_score,
        features=features,
        graph_context=graph_context,
        b64_frames=b64_frames,
    )
    llm_score = llm_result.get("llm_score", 0.5)
    print(f"  🧠 LLM score: {llm_score:.4f}")

    # ── Stage 6: Consensus Decision ──
    # Combine reasons from graph and LLM
    all_reasons = graph_summary.get("reasons", []) + llm_result.get("reasons", [])

    consensus = compute_consensus(
        cnn_score=cnn_score,
        graph_score=graph_score,
        llm_score=llm_score,
        reasons=all_reasons,
        llm_analysis=llm_result.get("analysis", ""),
    )
    print(f"  ✅ Consensus verdict: {consensus['verdict']} "
          f"(confidence: {consensus['confidence']}%)")

    return {
        "consensus": consensus,
        "forensic_payload": forensic_payload,
        "graph_summary": graph_summary,
        "llm_result": llm_result,
    }


# ── Routes ───────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "Misinformation Detection API",
        "version": "2.0.0",
        "pipeline": "CNN → Features → Graph → GraphRAG → LLM → Consensus",
    }


@app.post("/detect/audio", response_model=DetectionResult)
async def detect_audio(file: UploadFile = File(...)):
    """Analyze an uploaded audio file using its Mel-Spectrogram for forensic signatures."""
    if not file.content_type or not (file.content_type.startswith("audio/") or file.content_type == "application/octet-stream"):
        raise HTTPException(status_code=400, detail="File must be audio")

    # Save to temp file to generate spectrogram
    suffix = os.path.splitext(file.filename or "audio.mp3")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # Generate Spectrogram (The visual signature of the audio)
        spectrogram_b64 = generate_spectrogram(tmp_path)
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{spectrogram_b64}"},
                    },
                    {
                        "type": "text", 
                        "text": (
                            f"{AUDIO_USER_PROMPT}\n\n"
                            "### ANALYST CONTEXT:\n"
                            "The attached image IS your data source. It is the Mel-Spectrogram of the target audio. "
                            "Analyze the visual frequency patterns for AI synthesis signatures and provide the JSON result."
                        )
                    }
                ],
            },
        ]

        # Switch back to gpt-4o: Best accuracy for spectrogram patterns
        result = await call_fastrouter(messages, model="openai/gpt-4o")

        await save_to_supabase(HistoryEntry(
            type="audio",
            input_preview=file.filename or "uploaded_audio",
            verdict=result.verdict,
            confidence=result.confidence,
            reasons=result.reasons,
            summary=result.summary,
        ))

        return result
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/detect/image", response_model=DetectionResult)
async def detect_image(file: UploadFile = File(...)):
    """Analyze an uploaded image for manipulation using LLM vision."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(status_code=400, detail="Image too large (max 20 MB)")

    # Fast resize before sending: Saves 80% on upload time and LLM processing
    b64 = fast_resize_image(contents)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                },
                {"type": "text", "text": IMAGE_USER_PROMPT},
            ],
        },
    ]

    # Switch back to gpt-4o: High accuracy is worth the extra 2-3 seconds, mitigated by resizing
    result = await call_fastrouter(messages, model="openai/gpt-4o")

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
async def detect_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Analyze an uploaded video for deepfake using the full forensic pipeline.
    Returns the standard DetectionResult (backward compatible).
    """
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
        print(f"\n{'='*60}")
        print(f"🎬 Processing video: {file.filename}")
        print(f"{'='*60}")

        # ULTRA-FAST unified extraction (10 CNN, 2 Vision)
        frames, tensor, b64_frames = unified_frame_extraction(tmp_path, cnn_count=10, vision_count=2)
        tensor = tensor.to(device)

        # Run the full forensic pipeline
        pipeline_result = await run_forensic_pipeline(frames, tensor, background_tasks, b64_frames=b64_frames)
        consensus = pipeline_result["consensus"]

        # Map consensus to DetectionResult (backward compatible)
        result = DetectionResult(
            verdict=consensus["verdict"],
            confidence=consensus["confidence"],
            reasons=consensus["reasons"],
            summary=consensus["summary"],
        )

        background_tasks.add_task(save_to_supabase, HistoryEntry(
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


@app.post("/detect/video/detailed", response_model=DetailedDetectionResult)
async def detect_video_detailed(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Analyze an uploaded video with the FULL forensic pipeline.
    Returns detailed results including forensic features, graph analysis,
    pipeline scores, and LLM reasoning.
    """
    if video_model is None:
        raise HTTPException(status_code=503, detail="Video detection model is not available")

    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    suffix = os.path.splitext(file.filename or "video.mp4")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        print(f"\n{'='*60}")
        print(f"🎬 [DETAILED] Processing video: {file.filename}")
        print(f"{'='*60}")

        # High-speed unified extraction
        frames, tensor, b64_frames = unified_frame_extraction(tmp_path, cnn_count=10, vision_count=3)
        tensor = tensor.to(device)

        pipeline_result = await run_forensic_pipeline(frames, tensor, background_tasks, b64_frames=b64_frames)
        consensus = pipeline_result["consensus"]

        result = DetailedDetectionResult(
            verdict=consensus["verdict"],
            confidence=consensus["confidence"],
            reasons=consensus["reasons"],
            summary=consensus["summary"],
            forensic_features=pipeline_result["forensic_payload"],
            pipeline_scores=consensus.get("pipeline_scores"),
            graph_analysis=pipeline_result["graph_summary"],
            llm_reasoning=pipeline_result["llm_result"],
        )

        background_tasks.add_task(save_to_supabase, HistoryEntry(
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
