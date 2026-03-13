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
    "You are an expert AI forensic analyst specializing in deepfake detection "
    "and synthetic media analysis. You receive structured forensic signals from "
    "a CNN-based detection pipeline, a knowledge graph analysis, and a forensic "
    "knowledge base. Your job is to synthesize all of these into a final expert "
    "assessment.\n\n"
    "You are extremely critical and skeptical. You err on the side of flagging "
    "content as suspicious rather than assuming it is authentic.\n\n"
    "Always respond in valid JSON only."
)

REASONING_USER_PROMPT = """Analyze the following forensic data and attached sequence of frames from our AI deepfake detection pipeline.

### PIPELINE DATA:
1. CNN MODEL OUTPUT (EfficientNet-B4 + Multi-Head Attention)
   CNN score (deepfake probability): {cnn_score:.4f}
   
2. EXTRACTED FORENSIC SIGNALS (Signal Processing Analysis)
{features_json}

3. KNOWLEDGE CONTEXT (Retrieved Forensic Patterns)
{graph_context}

### EXPERT INSTRUCTIONS:
- You must produce a 'llm_score' (0.0 to 1.0).
- Be an OBJECTIVE forensic expert. Your goal is accuracy, not just finding faults.
- TEMPORAL CHECK: Analyze the relationship between frames. Look for consistent identity and natural motion. Flag identity flickering or background warping.
- SIGNAL VERIFICATION: If forensic signals are high (e.g., GAN noise), search the high-res frames for visual artifacts that confirm these signals. If signals are low and visuals are clean, the video is likely authentic.
- ANALYZE: Eyes (reflections/sync), Hair (blending), Edges (neckline), and Texture.

Respond with ONLY valid JSON in this exact format:
{{
  "llm_score": <calculated deepfake probability 0.0 to 1.0>,
  "confidence_level": "HIGH" or "MEDIUM" or "LOW",
  "reasons": ["Observation 1", "Observation 2", ...],
  "corroborating_signals": ["How visual artifacts verify or contradict the signal data"],
  "analysis": "A balanced professional forensic conclusion."
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
    if b64_frames:
        for b64 in b64_frames:
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
        )
    })

    messages = [
        {"role": "system", "content": REASONING_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            # Switch back to gpt-4o: Best balance of vision accuracy and speed with our current optimizations
            model_name = "openai/gpt-4o"
            
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 1000
            }
            # Deleted unnecessary reasoning_effort check as we moved back to gpt-4o

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
        if score >= 0.5:
            label = feature_labels.get(name, f"Suspicious {name}")
            reasons.append(f"{label} (score: {score:.2f})")
            high_features.append(name)

    # Compute fallback LLM score based on feature average
    feature_values = list(features.values())
    avg_features = sum(feature_values) / max(len(feature_values), 1)
    llm_score = 0.6 * cnn_score + 0.4 * avg_features

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
