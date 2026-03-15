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
from utils import extract_frames, preprocess_frames, unified_frame_extraction, generate_spectrogram, fast_resize_image, extract_audio_features

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
    "You are an OBJECTIVE, rigorous scientist. "
    "CRITICAL INSTRUCTION: You must DEFAULT to assuming content is REAL. Real-world media has noise, "
    "compression artifacts, motion blur, and natural imperfections. "
    "DO NOT hallucinate deepfake artifacts. "
    "ONLY flag content as FAKE if you see UNDENIABLE evidence of AI generation or face-swapping.\n\n"
    "Always respond in valid JSON only."
)

AUDIO_USER_PROMPT = """Analyze this Mel-Spectrogram as a senior forensic scientist. You must determine if this audio is a human recording (REAL) or an AI-generated clone (FAKE).

Modern AI audio (like ElevenLabs) is highly realistic but leaves microscopic signatures from neural vocoders (like HiFi-GAN/MelGAN). Actively hunt for these specific artifacts visually, AND use the extracted acoustic DSP features below to guide your verdict.

### EXTRACTED ACOUSTIC DSP FEATURES (librosa):
{audio_features}

- 'high_freq_ratio': Measures energy > 10kHz. Real voices > 0.05. Compressed MP3 = 0.0. Fake voices = 0.01-0.03.
- 'spectral_flux': Measures dynamic changes. Low values = smooth, robotic. High values = natural, chaotic.
- 'centroid_variance': Proxy for pitch stability. Low variance (<200k) = synthetic robot. High = natural human jitter.

### EXPERT FORENSIC SIGNATURES (Neural Vocoder Flaws):
1. **High-Frequency Shelf/Cutoff**: Modern AI often struggles to generate true frequencies above 12kHz or 16kHz. Does the spectrogram show a sudden, unnatural horizontal blank black area at the very top, while the lower registers are dense? 
    *CRITICAL NOTE ON CUTOFFS: Standard MP3 compression and web streaming ALSO create a hard cutoff at 16kHz. Do NOT fail an audio file solely for having a 16kHz shelf. A shelf is only suspicious if accompanied by other synthetic artifacts.*
2. **Blurred Fricatives & Sibilance**: "S", "Sh", and "F" sounds should look like a sharp, chaotic burst of high-frequency white noise (a bright vertical column). AI vocoders often "smudge" or blur these transients, making them look pillowy or unnaturally smooth.
3. **Harmonic Overtone Rigidity**: Look closely at the upper horizontal harmonic lines during sustained vowels. Human overtones have micro-vibrations and slight wiggles. AI overtones at high frequencies often become unnaturally straight and rigid.
4. **Synthetic Noise Floor**: Look at the dark background spaces between words. Does the background noise look identical and "painted on" or perfectly silent? Real room tone has subtle, chaotic variations.

### DECISIVE VERDICT LOGIC:
- We expect a binary result (REAL or FAKE).
- If you see a hard high-frequency cutoff (shelf) combined with blurred/smudged sibilance: FAKE.
- If you see rigid, perfectly straight high-frequency overtones: FAKE.
- If the high frequencies show natural chaotic decay and fricatives are distinct, sharp vertical bursts: REAL.
- CRITICAL: Do NOT classify as FAKE simply because there is a black shelf at the very top. If the speech patterns inside the visible frequencies look chaotic and natural, it is REAL (just compressed).

Respond ONLY with valid JSON:
{{
  "verdict": "REAL" or "FAKE",
  "confidence": 0-100,
  "reasons": ["Technical finding 1 (e.g. Phase gating detected)", "Technical finding 2 (e.g. Natural harmonic jitter)", ...],
  "summary": "Deep forensic summary of the vocal physics citing the DSP math.",
  "ai_patterns": {{
    "frequency_consistency": "PASS" or "FAIL" or "UNCERTAIN",
    "phase_discontinuity": "PASS" or "FAIL" or "UNCERTAIN"
  }}
}}"""

# ── Two-Pass Image Forensics Prompts ──────────────────────────────────────────

IMAGE_DESCRIPTION_PROMPT = """You are a meticulous visual analyst. Describe this image with extreme precision.

Extract ALL of the following — be exhaustive and specific. Your output will be used as a forensic document:

1. SCENE: What is the overall setting, environment, and context? Indoor/outdoor, time of day, weather if visible?
2. SUBJECTS: Who/what is in the image? Describe each person/object: age (estimated), gender, ethnicity, hair color/style, skin tone, facial structure (jaw, cheekbones, nose shape, lip shape), eyebrow density, presence or absence of facial hair, visible pores/blemishes/freckles.
3. ANATOMY & PROPORTIONS: Describe hand finger count and shape, ear shape and symmetry, eye shape, pupil size, iris color and pattern, eyelash detail, neck thickness relative to shoulders.
4. LIGHTING: Identify all visible light sources (position, color temperature, intensity). Describe where shadows fall, shadow softness/hardness, specular highlights on skin and objects.
5. EYE REFLECTIONS: Describe what is visible in the eye reflections (catchlights). Are they consistent between left and right eye?
6. BACKGROUND: What is behind the subjects? Is there depth of field blur? Describe the background textures, colors, any objects.
7. TEXTURES: Describe skin texture quality (smooth, pores visible, even, imperfections). Describe hair strand detail (individual strands visible?). Describe fabric/material textures.
8. COLORS: Dominant color palette, any color banding or inconsistencies.
9. EDGES & COMPOSITING: Are object boundaries sharply cut out, naturally blurred by depth of field, or showing "halo" artifacts (color bleed from another background)?
10. SENSOR NOISE & FILM GRAIN: Is the noise/grain uniform across the entire image? Or are some areas suspiciously smooth while others are noisy?
11. COMPOSITION & STYLE: Is this a photo, painting, illustration, or render? Photographic style (portrait, candid, studio)?
12. SEMANTICS & CONTEXT: Are there objects interacting? Is there text visible on signs/clothing? Do the physical interactions and scene logic make structural sense?

Be specific. Write in numbered lists per section. Do NOT draw any conclusions about authenticity yet — only describe."""

IMAGE_FORENSIC_ANALYSIS_PROMPT = """You are an advanced AI forensics analyst. You have been given:
1. An IMAGE to analyze visually
2. A SCENE DESCRIPTION of that image extracted by another analyst

Your task: Use the scene description as a ground-truth reference, then actively HUNT for generative AI flaws, structural hallucinations, and physics violations. Modern AI often masters texture and lighting, but fails at complex physical logic and background details.

### FORENSIC CHECKLIST (check each against the image):

**A. LIGHTING vs. SHADOWS:**
  - The description says the light source is at position X. Do shadows fall in the correct direction?
  - If multiple light sources described, are shadow edges consistent with all of them?
  - Are skin specular highlights (glossy spots) aligned with the described light source direction?

**B. EYE PHYSICS:**
  - The description notes eye reflection content. Do BOTH eyes show the SAME reflection? (AI often gets this wrong)
  - Iris pattern: Is it symmetrical? Real irises have complex, asymmetric fibers.
  - Eyelash rendering: Too uniform/perfect = AI artifact.

**C. SKIN TEXTURE vs. DESCRIPTION:**
  - Description may say 'pores visible' or 'smooth skin'. Does the actual image match? AI skin often claims texture but shows airbrushed smoothness.
  - Look for 'texture perfection' — unnaturally even skin with zero imperfections across the entire face is a strong FAKE signal.
  - Hair-to-skin boundary: Does hair emerge naturally from scalp, or does it look painted on?

**D. BACKGROUND COHERENCE & DETAILS:**
  - Background "blobbing": Do people or objects in the background look like shapeless, melted blobs or abstract brushstrokes upon close inspection? (Classic Midjourney/Stable Diffusion flaw).
  - Depth of field: Does the blur look like a real camera lens, or does it irregularly mask mistakes?
  - Structural geometry: Do background lines, fences, or architecture align correctly behind foreground subjects?

**E. ANATOMY PHYSICS & OBJECT FUSION:**
  - The "Fusion" Check: Do limbs or fingers physically merge or melt into the objects they are holding? (e.g., hand blending directly into a dog's fur, or a person's shoulder).
  - Straps & Clothing logic: Do bag straps, jacket zippers, or life-jacket buckles actually connect logically, or do they disappear into nowhere?
  - Count fingers. Look at joints. Look for ghost limbs or missing limbs.
  - Ears and Teeth: Unnatural, simplified shapes or blending.

**F. DIFFUSION MODEL SIGNATURES:**
  - Over-smooth areas adjacent to high-detail areas (classic diffusion artifact)
  - Accessories (glasses, earrings, jewelry): Do they interact with light realistically? Glasses should show refraction.
  - Hair: Does it get progressively thinner toward tips, or does it just blur out?

**G. GAN SIGNATURES:**
  - Checkerboard periodic noise: Zoom mentally to background/fabric areas. Any regular grid-like noise pattern?
  - Spectral artifacts: Do printed text in the image look garbled or impossibly readable?

**H. SEMANTIC & LOGICAL COHERENCE:**
  - Text & Symbols: Is background text or clothing text readable and logically coherent, or is it "AI gibberish" (alien shapes/morphed letters)?
  - Physical Plausibility: Do floating elements or impossible structures exist? Does water/liquid interact naturally with objects?
  - Contextual Anomalies: Are there elements that fundamentally shouldn't exist in the described scene?

**I. EDGE & BOUNDARY HALOS (COMPOSITING CHECK):**
  - Edge Bleed: Do the edges of the subject show a "halo" or a thin line of background color that doesn't match the current setting?
  - Cut-out sharpness: Are edges razor-sharp when the camera physics imply they should be slightly blurred by motion or depth of focus?

**J. SENSOR NOISE & TEXTURAL HOMOGENEITY:**
  - Uneven Noise: Real photos have uniform ISO noise/grain. AI often outputs uneven noise (e.g., face is flawlessly smooth but clothing/background is grainy, or vice versa).
  - Compression consistency: Are JPEG blocking artifacts consistently sized across the subject and background?

### SCORING RULES:
- If you find ANY instance of fused anatomy (e.g., skin melting into an object) or severe structural nonsense (blob-people in background, straps leading nowhere), the image is AUTOMATICALLY FAKE (>80 confidence).
- Each confirmed AI hallucination/physics violation = +20-30 confidence points toward FAKE.
- If ALL anatomy, lighting, background details, and structural logic checks pass under extreme scrutiny: very likely REAL.
- Score UNCERTAIN only if image quality is extremely low (highly pixelated/blurry).

### SCENE DESCRIPTION (from Pass 1):
{description}

Respond ONLY with valid JSON:
{{
  "verdict": "REAL" or "FAKE" or "UNCERTAIN",
  "confidence": 0-100,
  "reasons": ["Specific contradiction or confirmation found (e.g., 'Shadow direction contradicts described top-left light source')", ...],
  "summary": "Technical forensic summary citing specific physics violations or confirmations.",
  "ai_patterns": {{
    "anatomy_score": "PASS" or "FAIL" or "UNCERTAIN",
    "lighting_score": "PASS" or "FAIL" or "UNCERTAIN",
    "texture_score": "PASS" or "FAIL" or "UNCERTAIN",
    "background_score": "PASS" or "FAIL" or "UNCERTAIN",
    "eye_physics_score": "PASS" or "FAIL" or "UNCERTAIN",
    "semantic_score": "PASS" or "FAIL" or "UNCERTAIN",
    "edge_boundary_score": "PASS" or "FAIL" or "UNCERTAIN",
    "noise_analysis_score": "PASS" or "FAIL" or "UNCERTAIN"
  }}
}}"""


# ── Pydantic models ─────────────────────────────────────────────────
# Removed NewsRequest as it's no longer used


class DetectionResult(BaseModel):
    verdict: str
    confidence: float
    reasons: list[str]
    summary: str
    ai_patterns: dict | None = None


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
async def _call_llm_raw(
    messages: list[dict],
    model: str = "openai/gpt-4o",
    max_tokens: int = 1500,
) -> str:
    """
    Call FastRouter and return the raw text content (no JSON parsing).
    Used for Pass 1 (image description extraction) where the output is free-form text.
    """
    if not FASTROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="FastRouter API key not configured")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
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
    return data["choices"][0]["message"]["content"].strip()


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

    async with httpx.AsyncClient(timeout=90.0) as client:
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
        ai_patterns=result.get("ai_patterns"),  # Preserve for image forensics pass
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
        print("  ⚠️  Weights missing: Using neutral heuristic proxy")
        # Without trained weights the CNN has zero discriminative power.
        # Start at 0.45 (neutral/slightly-real-leaning) and boost only when
        # the strongest forensic signals are clearly anomalous.
        key_spatial = max(
            features["gan_noise"],
            features["face_blending"],
            features["spectral_artifact"],
            features["texture_perfection"],
        )
        key_temporal = max(
            features["temporal_jump"],
            features["lip_sync_error"],
        )
        cnn_score = 0.45 + key_spatial * 0.22 + key_temporal * 0.18
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
        # Programmatically Extract Audio Features
        audio_features = extract_audio_features(tmp_path)
        features_str = json.dumps(audio_features, indent=2)

        # Generate Spectrogram (The visual signature of the audio)
        spectrogram_b64 = generate_spectrogram(tmp_path)
        
        custom_prompt = AUDIO_USER_PROMPT.format(audio_features=features_str)
        
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
                            f"{custom_prompt}\n\n"
                            "### ANALYST CONTEXT:\n"
                            "The attached image IS your data source. It is the Mel-Spectrogram of the target audio. "
                            "Analyze the visual frequency patterns COMBINED with the DSP features above and provide the JSON result."
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
    """
    Analyze an uploaded image for AI generation / manipulation using a two-pass LLM forensics pipeline.

    Pass 1 — Image Description Extraction:
        Send the full-resolution image to GPT-4o and extract a comprehensive structured
        description (lighting, anatomy, textures, eye reflections, background, etc.).
        This description is a "regeneration brief" — detailed enough to recreate the image.

    Pass 2 — Forensic Analysis Using Description:
        Send BOTH the image AND the extracted description to GPT-4o.
        The LLM looks for contradictions between the described physics and what's visually present.
        Contradictions (e.g. wrong shadow direction, missing pores, uniform iris) are key FAKE signals.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(status_code=400, detail="Image too large (max 20 MB)")

    # Get two resolutions: full (1024px) for description, resized (768px) for forensics
    full_b64, resized_b64 = fast_resize_image(contents)

    print(f"\n{'='*60}")
    print(f"🖼️  Two-Pass Image Forensics: {file.filename}")
    print(f"{'='*60}")

    # ── Pass 1: Image Description Extraction ────────────────────────────────
    print("  🔍 Pass 1: Extracting comprehensive image description...")
    desc_messages = [
        {
            "role": "system",
            "content": (
                "You are a precise visual analyst. Extract detailed, factual descriptions "
                "of everything visible. Be specific and technical. No interpretation — only observation."
            ),
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{full_b64}"},
                },
                {"type": "text", "text": IMAGE_DESCRIPTION_PROMPT},
            ],
        },
    ]

    image_description = await _call_llm_raw(desc_messages, model="openai/gpt-4o", max_tokens=1800)
    print(f"  ✅ Pass 1 complete — extracted {len(image_description)} chars of description")

    # ── Pass 2: Forensic Analysis using the Description ──────────────────────
    print("  🧠 Pass 2: Forensic contradiction analysis...")
    forensic_prompt = IMAGE_FORENSIC_ANALYSIS_PROMPT.format(description=image_description)

    forensic_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{resized_b64}"},
                },
                {"type": "text", "text": forensic_prompt},
            ],
        },
    ]

    raw_result = await call_fastrouter(forensic_messages, model="openai/gpt-4o")

    # ── Enrich result with ai_patterns from the raw JSON if available ────────
    print(f"  ✅ Pass 2 complete — verdict: {raw_result.verdict} ({raw_result.confidence}%)")

    result = DetectionResult(
        verdict=raw_result.verdict,
        confidence=raw_result.confidence,
        reasons=raw_result.reasons,
        summary=raw_result.summary,
        ai_patterns=raw_result.ai_patterns,  # Pass through per-category forensic scores
    )

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

        # Unified extraction (10 CNN frames for model, 5 Vision frames for LLM forensics)
        frames, tensor, b64_frames = unified_frame_extraction(tmp_path, cnn_count=10, vision_count=5)
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

        # High-speed unified extraction (10 CNN, 5 Vision for thorough forensic analysis)
        frames, tensor, b64_frames = unified_frame_extraction(tmp_path, cnn_count=10, vision_count=5)
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
