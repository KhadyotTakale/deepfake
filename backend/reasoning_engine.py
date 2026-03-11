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

REASONING_USER_PROMPT = """Analyze the following forensic data from our AI deepfake detection pipeline.

### PIPELINE DATA:
1. CNN MODEL OUTPUT (EfficientNet-B4 + Attention-GRU)
   CNN score (deepfake probability): {cnn_score:.4f}
   
2. EXTRACTED FORENSIC SIGNALS (Signal Processing Analysis)
{features_json}

3. KNOWLEDGE CONTEXT (Retrieved Forensic Patterns)
{graph_context}

### EXPERT INSTRUCTIONS:
- You must synthesize a final 'llm_score'. 
- NOTE: If the CNN score is around 0.1000 or exactly 0.5000, it may indicate it is running in a conservative or untrained mode. In these cases, you MUST give more weight (70%+) to the individual forensic signals.
- Evaluate the 'corroborating_signals'. Examples: High GAN noise + Face Blending = Strong evidence of face-swap. Temporal Jumps + Lip Sync Error = Strong evidence of temporal manipulation.
- Be extremely precise. If a video has perfect lip-sync but high GAN noise, look for a 'GAN-generated' verdict rather than 'Face-swap'.

Respond with ONLY valid JSON in this exact format:
{{
  "llm_score": <calculated deepfake probability 0.0 to 1.0>,
  "confidence_level": "HIGH" or "MEDIUM" or "LOW",
  "reasons": ["Specific evidence observation 1", "Specific evidence observation 2", ...],
  "corroborating_signals": ["Detailed description of how Signal A verifies Signal B"],
  "analysis": "A concise (2-sentence) professional forensic conclusion."
}}"""


# ─────────────────────────────────────────────────────────────────────
# Main Reasoning Function
# ─────────────────────────────────────────────────────────────────────

async def reason_about_authenticity(
    cnn_score: float,
    features: dict,
    graph_context: str,
) -> dict:
    """
    Send combined CNN + features + graph context to GPT-4o-mini
    for structured forensic reasoning.

    Args:
        cnn_score: The deepfake probability from the CNN model (0.0–1.0).
        features: Dict of forensic feature scores from feature_extractor.
        graph_context: Formatted context string from graphrag_engine.

    Returns:
        Dict with keys: llm_score, confidence_level, reasons,
        corroborating_signals, analysis.
    """
    if not FASTROUTER_API_KEY:
        return _fallback_reasoning(cnn_score, features)

    # Format features as readable JSON
    features_json = json.dumps(features, indent=2)

    messages = [
        {"role": "system", "content": REASONING_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": REASONING_USER_PROMPT.format(
                cnn_score=cnn_score,
                features_json=features_json,
                graph_context=graph_context,
            ),
        },
    ]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                FASTROUTER_URL,
                headers={
                    "Authorization": f"Bearer {FASTROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "openai/o3-mini",
                    "messages": messages,
                },
            )

        if response.status_code != 200:
            print(f"⚠️  LLM reasoning API error: {response.status_code}")
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
