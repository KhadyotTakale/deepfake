# main.py — FastAPI backend for Misinformation Detection System
# Extended with Advanced AI Forensic Pipeline:
# CNN → Feature Extraction → Graph Building → GraphRAG → LLM Reasoning → Consensus
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

NEWS_USER_PROMPT = """Analyze the following news article text for signs of misinformation or fake news.

### SCORING GUIDELINES (Use these to calculate the 'confidence' field):
- Start at 50% confidence.
- Increment or decrement based on evidence strength:
  * Slight bias/sensationalism: +/- 10%
  * Multiple unverified claims/logical gaps: +/- 25%
  * Blatant fabrication/known fake news pattern: +/- 40%
- If the article is highly professional, well-sourced, and neutral: 'REAL' confidence should be 90%+.
- DYNAMIC SCORE: Do NOT return a generic number. Calculate it based on your analysis.

### FORENSIC CHECKLIST:
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
  "confidence": <dynamically calculated number 0-100 based on findings>,
  "reasons": ["specific observation 1", "specific observation 2", ...],
  "summary": "expert analysis summary"
}}"""

IMAGE_USER_PROMPT = """You are an expert forensic analyst. Analyze this image with EXTREME SKEPTICISM for signs of AI generation or digital manipulation. 

### SCORING GUIDELINES (Use these to calculate the 'confidence' field):
- Start at 50% confidence.
- Increment or decrement based on evidence strength:
  * Minor anomaly (e.g., slight smooth skin): +/- 5%
  * Moderate anomaly (e.g., repeating background patterns, eye asymmetry): +/- 15%
  * Major anomaly (e.g., extra fingers, garbled text, impossible anatomy): +/- 30%
- If no anomalies are found after deep inspection, 'REAL' confidence should also be high (e.g., 90%+).
- DYNAMIC SCORE: Do NOT default to 85%. Calculate a specific score based on your findings.

### FORENSIC CHECKLIST:
1. SKIN & FACE: Overly smooth/plastic skin, pores missing, unnatural skin texture, asymmetric facial features, weird ear shapes, teeth anomalies, iris irregularities, unnatural hair strands or hairline
2. HANDS & FINGERS: Wrong number of fingers, fused/bent fingers, inconsistent finger lengths, missing knuckles, unnatural hand poses
3. TEXT & WRITING: Garbled or nonsensical text anywhere in the image, distorted letters, impossible signage
4. BACKGROUND: Blurred or incoherent backgrounds, objects merging into each other, architecture that doesn't make sense, repeating patterns
5. EDGES & TRANSITIONS: Unnatural blending between subject and background, halo effects around subjects, sharp vs blurry inconsistencies
6. LIGHTING: Impossible shadow directions, inconsistent light sources, flat lighting that doesn't match the scene
7. CLOTHING & ACCESSORIES: Impossible folds, asymmetric collars/glasses, accessories that merge with skin or hair, jewelry anomalies
8. OVERALL: Too-perfect composition, uncanny valley feeling, hyper-realistic but slightly "off" quality.

IMPORTANT: When in doubt, lean toward FAKE or UNCERTAIN. Be very critical.

Respond with ONLY valid JSON in this exact format:
{{
  "verdict": "REAL" or "FAKE" or "UNCERTAIN",
  "confidence": <dynamically calculated number 0-100 based on findings>,
  "reasons": ["specific observation 1", "specific observation 2", ...],
  "summary": "expert forensic summary"
}}"""


# ── Pydantic models ─────────────────────────────────────────────────
class NewsRequest(BaseModel):
    text: str


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


# ─────────────────────────────────────────────────────────────────────
# Advanced Video Pipeline (shared by both /detect/video endpoints)
# ─────────────────────────────────────────────────────────────────────

async def run_forensic_pipeline(
    frames: list[np.ndarray],
    tensor: torch.Tensor,
) -> dict:
    """
    Run the full multi-stage forensic pipeline on extracted video frames.
    """
    # ── Stage 1: CNN Inference ──
    # Check if weights are loaded (heuristic check for random initialization)
    has_weights = os.path.exists(WEIGHTS_PATH)
    
    with torch.no_grad():
        output = video_model(tensor)
    
    cnn_score = output.item()
    
    # ── Stage 2: Forensic Feature Extraction ──
    # We call this early because we need it for the heuristic fallback if weights are missing
    forensic_payload = extract_forensic_features(
        frames=frames,
        model_probability=cnn_score,
        media_type="video",
    )
    features = forensic_payload["features"]
    
    # HEURISTIC FALLBACK: If weights are missing, the CNN score from an untrained model 
    # will be random (~0.5). In this case, we use the average of forensic features 
    # as a "pseudo-CNN" score to provide a meaningful base for the consensus.
    if not has_weights:
        print("  ⚠️  Weights missing: Using conservative heuristic proxy")
        # Only count features that are actually 'anomalous' (> 0.15)
        # to avoid noise accumulation for real videos.
        spatial_sig = [features["gan_noise"], features["face_blending"]]
        temporal_sig = [features["temporal_jump"], features["lip_sync_error"]]
        
        def filter_noise(vals):
            # Only return values > 0.15, otherwise return 0 (noise suppression)
            return [v if v > 0.15 else 0.0 for v in vals]

        spatial_proxy = np.mean(filter_noise(spatial_sig))
        temporal_proxy = np.mean(filter_noise(temporal_sig))
        
        # Base floor is low (0.1) for real videos
        cnn_score = 0.1 + (spatial_proxy * 0.5) + (temporal_proxy * 0.4)
    
    print(f"  📊 CNN score (effective): {cnn_score:.4f}")
    forensic_payload["model_probability"] = round(cnn_score, 4)


    # ── Stage 3: Feature Graph Building ──
    graph = build_feature_graph(forensic_payload)

    graph_score = compute_graph_score(graph)
    graph_summary = graph_to_summary(graph)
    print(f"  🕸️  Graph score: {graph_score:.4f} | "
          f"Artifacts triggered: {len(graph_summary.get('artifacts', []))}")

    # Persist to Neo4j (non-blocking, best-effort)
    try:
        persist_to_neo4j(graph)
    except Exception as e:
        print(f"  ⚠️  Neo4j persistence skipped: {e}")

    # ── Stage 4: GraphRAG Context Retrieval ──
    graph_context = retrieve_forensic_context(
        features=features,
        graph_summary=graph_summary,
    )
    print(f"  📚 GraphRAG context: {len(graph_context)} chars")

    # ── Stage 5: LLM Authenticity Reasoning ──
    llm_result = await reason_about_authenticity(
        cnn_score=cnn_score,
        features=features,
        graph_context=graph_context,
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


@app.post("/detect/news", response_model=DetectionResult)
async def detect_news(request: NewsRequest):
    """Analyze a text article for fake news using LLM."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": NEWS_USER_PROMPT.format(text=request.text[:5000])},
    ]

    result = await call_fastrouter(messages, model="openai/o3-mini")

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
async def detect_video(file: UploadFile = File(...)):
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

        # Extract and preprocess frames
        frames = extract_frames(tmp_path, max_frames=20)
        tensor = preprocess_frames(frames).to(device)

        # Run the full forensic pipeline
        pipeline_result = await run_forensic_pipeline(frames, tensor)
        consensus = pipeline_result["consensus"]

        # Map consensus to DetectionResult (backward compatible)
        result = DetectionResult(
            verdict=consensus["verdict"],
            confidence=consensus["confidence"],
            reasons=consensus["reasons"],
            summary=consensus["summary"],
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


@app.post("/detect/video/detailed", response_model=DetailedDetectionResult)
async def detect_video_detailed(file: UploadFile = File(...)):
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

        frames = extract_frames(tmp_path, max_frames=20)
        tensor = preprocess_frames(frames).to(device)

        pipeline_result = await run_forensic_pipeline(frames, tensor)
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
