# reasoning_engine.py — LLM Authenticity Reasoning via GPT-4o-mini
# Takes CNN outputs + forensic features + graph context and produces
# a structured reasoning output with deepfake probability and reasons.

import json
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

FASTROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
FASTROUTER_URL = "https://go.fastrouter.ai/api/v1/chat/completions"

# ─────────────────────────────────────────────────────────────────────
# LLM Prompts for Forensic Reasoning
# ─────────────────────────────────────────────────────────────────────

REASONING_SYSTEM_PROMPT = (
    "You are a rigorous AI forensic scientist specializing in deepfake video detection. "
    "Your job is to evaluate video frames and forensic signals to determine authenticity.\n\n"
    "IMPORTANT GUIDELINES:\n"
    "- Natural artifacts (motion blur, compression noise, low resolution, natural shadows) are NOT deepfake indicators.\n"
    "- Be decisive: avoid UNCERTAIN unless genuinely split between REAL and FAKE.\n"
    "- Assign a score based on cumulative evidence. Corroborating signals are additive — multiple weak signals together constitute strong evidence.\n"
    "- Face-swap and voice-sync deepfakes have SPECIFIC artifacts: blending halos at jawline/hairline, skin tone mismatches, temporal flickering, and unnatural eye reflections.\n\n"
    "Always respond in valid JSON only."
)

REASONING_USER_PROMPT = """Analyze the attached video frames and forensic pipeline data. You have {frame_count} frames from the suspected video.

### PIPELINE DATA:
1. CNN MODEL OUTPUT (Deepfake probability 0.0=REAL to 1.0=FAKE): {cnn_score:.4f}

2. FORENSIC SIGNAL SCORES (0.0=clean, 1.0=strong fake signal):
{features_json}

3. FORENSIC KNOWLEDGE CONTEXT:
{graph_context}

---
### PHASE 1 — PER-FRAME ANALYSIS
For EACH frame provided, examine these 7 dimensions:

**A. IDENTITY CONSISTENCY**: Is the face the same person across all frames? Any identity flickering?
**B. FACE BLENDING BOUNDARY**: Look at jawline, hairline, ears, neck junction. Any gradient anomalies, halos, or color mismatches?
**C. LIGHTING PHYSICS**: Do face shadows match the background light direction? Check specular highlights on nose/forehead vs. background objects.
**D. EYE REGION**: Are both eyes showing the same environmental reflections (catchlights)? Are pupils dilated equally? Eyelashes uniform/perfect = AI artifact.
**E. SKIN TEXTURE**: Real skin has visible pores, asymmetric micro-textures, and imperfections. AI skin is too uniform. Check cheeks and forehead.
**F. BACKGROUND WARPING**: Does the background distort or warp near the face boundary? First Order Motion and similar methods warp the background.
**G. COMPRESSION ARTIFACTS**: AI-generated faces often have different JPEG compression patterns than the background (inconsistent block sizes).
**H. EDGE & BOUNDARY HALOS (COMPOSITING)**: Do subject edges show a "halo" or color bleed from a different background?
**I. SENSOR NOISE & GRAIN**: Is the camera noise uniform? Or is the face flawlessly smooth while the background is grainy?

### PHASE 2 — TEMPORAL CROSS-FRAME ANALYSIS
Compare frames ACROSS each other:
- Does the face identity remain perfectly stable (too stable = AI loop) or flicker between frames?
- Does background lighting/color remain consistent frame-to-frame while the face changes?
- Do any GAN checkerboard patterns repeat at the same pixel positions across frames?
- Is mouth motion physically plausible given the head angle and surrounding frames?

### SCORING ANCHORS (use these to calibrate your llm_score):
- 0.0-0.15: Definitively REAL — all checks pass, organic textures, natural physics everywhere.
- 0.15-0.35: Probably REAL — only natural compression/quality artifacts, no AI-specific signals found.
- 0.35-0.55: Uncertain — some suspicious signals but not conclusive on their own.
- 0.55-0.75: Probably FAKE — visible AI manipulation artifacts (face blending halos, rigid skin texture, unnatural boundaries).
- 0.75-1.0: Definitively FAKE — undeniable face-swap, synthetic generation, or multiple corroborating deepfake signals.

### IMPORTANT:
- Start from a baseline score of 0.15. Adjust UP when you find real deepfake artifacts; adjust DOWN when signals are clearly natural.
- Corroborating signals add up: two moderate signals together are stronger evidence than one strong signal alone.
- Standard compression, motion blur, and natural lighting variations are NOT deepfake indicators.
- When the CNN pipeline data shows 2+ forensic features above 0.4, treat this as supporting evidence.

Respond with ONLY valid JSON:
{{
  "llm_score": <deepfake probability 0.0 to 1.0>,
  "confidence_level": "HIGH" or "MEDIUM" or "LOW",
  "frame_observations": ["Frame N: specific observation", ...],
  "temporal_findings": ["Cross-frame consistency observation", ...],
  "reasons": ["Specific forensic finding 1", "Specific forensic finding 2", ...],
  "corroborating_signals": ["How visual evidence matches/contradicts signal data"],
  "analysis": "Decisive forensic conclusion citing the top 2-3 specific evidences."
}}"""


# ─────────────────────────────────────────────────────────────────────
# Main Reasoning Function
# ─────────────────────────────────────────────────────────────────────

async def reason_about_authenticity(
    cnn_score: float,
    features: dict,
    graph_context: str,
    b64_frames: list[str] | None = None,
) -> dict:
    """
    Send combined CNN + features + graph context + optional images to GPT-4o
    for visual-enhanced forensic reasoning.
    """
    if not FASTROUTER_API_KEY:
        return _fallback_reasoning(cnn_score, features)

    # Format features as readable JSON
    features_json = json.dumps(features, indent=2)
    user_content = []

    # Add images if available (Vision support)
    # Include frame labels so GPT-4o can reference specific frames in observations
    if b64_frames:
        for i, b64 in enumerate(b64_frames, 1):
            # Add a label before each frame for easier reference
            user_content.append({
                "type": "text",
                "text": f"[FRAME {i} of {len(b64_frames)}]",
            })
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            })
    
    # Add the text prompt
    user_content.append({
        "type": "text",
        "text": REASONING_USER_PROMPT.format(
            cnn_score=cnn_score,
            features_json=features_json,
            graph_context=graph_context,
            frame_count=len(b64_frames) if b64_frames else 0,
        )
    })

    messages = [
        {"role": "system", "content": REASONING_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            model_name = "openai/gpt-4o"
            
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.05,  # Even lower for more deterministic forensic analysis
                "max_tokens": 2000,   # Increased for richer per-frame analysis
            }

            response = await client.post(
                FASTROUTER_URL,
                headers={
                    "Authorization": f"Bearer {FASTROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        if response.status_code != 200:
            print(f"⚠️  LLM reasoning API error: {response.status_code} - {response.text}")
            return _fallback_reasoning(cnn_score, features)

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Strip markdown code fences
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            content = "\n".join(lines)

        result = json.loads(content)

        return {
            "llm_score": float(result.get("llm_score", 0.5)),
            "confidence_level": result.get("confidence_level", "MEDIUM"),
            "reasons": result.get("reasons", []),
            "corroborating_signals": result.get("corroborating_signals", []),
            "analysis": result.get("analysis", "Analysis completed."),
        }

    except json.JSONDecodeError as e:
        print(f"⚠️  LLM returned invalid JSON: {e}")
        return _fallback_reasoning(cnn_score, features)
    except Exception as e:
        print(f"⚠️  LLM reasoning failed: {e}")
        return _fallback_reasoning(cnn_score, features)


def _fallback_reasoning(cnn_score: float, features: dict) -> dict:
    """
    Rule-based fallback when the LLM is unavailable.
    Uses feature scores directly to produce a structured output.
    """
    reasons = []
    high_features = []

    feature_labels = {
        "gan_noise": "GAN fingerprint pattern detected",
        "face_blending": "Face boundary blending artifact",
        "temporal_jump": "Temporal frame inconsistency",
        "lip_sync_error": "Lip sync mismatch with facial movement",
        "eye_blink_anomaly": "Abnormal eye blink pattern",
        "lighting_inconsistency": "Lighting inconsistency between face and background",
        "background_coherence": "Background warping or motion artifact",
        "spectral_artifact": "AI-specific frequency artifact",
        "texture_perfection": "Unnatural skin texture regularity",
    }

    for name, score in features.items():
        if score >= 0.35:
            label = feature_labels.get(name, f"Suspicious {name}")
            reasons.append(f"{label} (score: {score:.2f})")
            high_features.append(name)

    # Compute fallback LLM score — weight the strongest signal heavily
    feature_values = list(features.values())
    avg_features = sum(feature_values) / max(len(feature_values), 1)
    max_feature = max(feature_values) if feature_values else 0.0
    # Key discriminative features get extra weight
    key_names = ["face_blending", "gan_noise", "texture_perfection", "spectral_artifact", "temporal_jump", "lip_sync_error"]
    key_vals = [features.get(k, 0.0) for k in key_names]
    max_key = max(key_vals) if key_vals else 0.0
    llm_score = 0.25 * cnn_score + 0.45 * max_key + 0.30 * avg_features

    if not reasons:
        if cnn_score > 0.5:
            reasons.append(f"CNN model flags high deepfake probability ({cnn_score:.2f})")
        else:
            reasons.append("No strong forensic indicators detected")

    # Determine confidence
    if len(high_features) >= 3:
        confidence = "HIGH"
    elif len(high_features) >= 1:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "llm_score": round(min(max(llm_score, 0.0), 1.0), 4),
        "confidence_level": confidence,
        "reasons": reasons,
        "corroborating_signals": [],
        "analysis": (
            f"Fallback analysis: CNN score={cnn_score:.2f}, "
            f"average feature score={avg_features:.2f}. "
            f"{len(high_features)} features flagged above threshold."
        ),
    }
