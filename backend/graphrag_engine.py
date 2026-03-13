# graphrag_engine.py — Graph-Augmented Retrieval for Forensic Knowledge
# Uses the feature graph + Neo4j to retrieve contextual forensic knowledge
# for the LLM reasoning stage.
#
# When Neo4j is available, retrieves historical patterns from the graph DB.
# When Neo4j is unavailable, falls back to a rule-based knowledge base
# built from the current analysis graph.

import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────
# Built-in Forensic Knowledge Base (used as fallback when Neo4j is
# unavailable, and as the seed knowledge for GraphRAG)
# ─────────────────────────────────────────────────────────────────────

FORENSIC_KNOWLEDGE = {
    "gan_noise": {
        "description": "GAN (Generative Adversarial Network) generators leave detectable "
                       "spectral fingerprints in the high-frequency band of generated images. "
                       "This is caused by the upsampling layers in the generator network.",
        "indicators": [
            "High-frequency spectral energy ratio > 0.2",
            "Periodic patterns in DCT domain",
            "Checkerboard artifacts from transposed convolutions",
        ],
        "known_generators": ["StyleGAN", "ProGAN", "DALL-E", "Midjourney", "Stable Diffusion"],
        "deepfake_correlation": "strong",
    },
    "face_blending": {
        "description": "Face-swap algorithms (e.g., DeepFaceLab, FaceSwap) must blend the "
                       "generated face with the original frame. This blending creates gradient "
                       "discontinuities at the face boundary, especially around the jawline, "
                       "ears, and hairline.",
        "indicators": [
            "Sharp gradient transitions at face boundary",
            "Mismatch in skin tone between face and neck",
            "Visible halo effect around face edges",
        ],
        "known_generators": ["DeepFaceLab", "FaceSwap", "SimSwap"],
        "deepfake_correlation": "strong",
    },
    "temporal_jump": {
        "description": "Frame-level deepfake processing can introduce temporal inconsistencies "
                       "where the manipulated region (face) changes abruptly between frames while "
                       "the rest of the video remains smooth. This is especially noticeable during "
                       "rapid head movements.",
        "indicators": [
            "Sudden SSIM drops between consecutive frames",
            "Face region changes faster than background",
            "Flickering artifacts in face-swapped regions",
        ],
        "known_generators": ["DeepFaceLab", "Wav2Lip", "First Order Motion"],
        "deepfake_correlation": "moderate",
    },
    "lip_sync_error": {
        "description": "In lip-sync deepfakes (e.g., Wav2Lip), the mouth region is manipulated "
                       "independently of the rest of the face. This creates a discrepancy in "
                       "optical flow between the lip region and the upper face.",
        "indicators": [
            "Mouth motion does not correlate with upper face motion",
            "Lip boundary shows blending artifacts",
            "Audio-visual synchronization anomalies",
        ],
        "known_generators": ["Wav2Lip", "Audio2Head", "SadTalker"],
        "deepfake_correlation": "moderate",
    },
    "eye_blink_anomaly": {
        "description": "Many deepfake generators are trained on still images or short clips "
                       "where natural blink patterns are absent. This results in generated videos "
                       "with abnormally stable open eyes or erratic blink patterns.",
        "indicators": [
            "No detectable blinks over extended sequences",
            "Erratic eye detection (eyes appearing/disappearing)",
            "Unnatural eye aspect ratio (EAR) patterns",
        ],
        "known_generators": ["DeepFaceLab (early versions)", "FaceSwap"],
        "deepfake_correlation": "moderate",
    },
    "lighting_inconsistency": {
        "description": "When a face is composited onto a different body or background, the "
                       "lighting conditions often do not match. This manifests as luminance "
                       "differences between the face and background regions.",
        "indicators": [
            "Face luminance does not match scene lighting",
            "Shadow direction mismatch",
            "Specular highlight inconsistencies",
        ],
        "known_generators": ["DeepFaceLab", "FaceShifter", "HifiFace"],
        "deepfake_correlation": "moderate",
    },
    "background_coherence": {
        "description": "Some deepfake methods warp or distort the background around the "
                       "manipulated face region. This is visible as unnatural background "
                       "motion that correlates with face movements.",
        "indicators": [
            "Background motion correlates with face manipulation",
            "Warping artifacts near face boundary",
            "Background optical flow exceeds expected camera motion",
        ],
        "known_generators": ["First Order Motion Model", "Face2Face"],
        "deepfake_correlation": "weak-to-moderate",
    },
}


# ─────────────────────────────────────────────────────────────────────
# Context Retrieval Functions
# ─────────────────────────────────────────────────────────────────────

def retrieve_forensic_context(
    features: dict,
    graph_summary: dict | None = None,
) -> str:
    """
    Build a rich forensic context string for the LLM reasoning engine.

    Combines:
    1. Built-in forensic knowledge for features above threshold
    2. Graph summary (triggered artifacts and inferences)
    3. Neo4j historical patterns (if available)

    Args:
        features: Dict of feature_name → score from the feature extractor.
        graph_summary: Output from graph_builder.graph_to_summary(),
                       containing artifacts, inferences, and reasons.

    Returns:
        Formatted context string ready for inclusion in the LLM prompt.
    """
    context_parts = []

    # ── Section 1: Triggered forensic knowledge ──
    context_parts.append("=== FORENSIC KNOWLEDGE BASE ===")
    active_features = {
        name: score for name, score in features.items() if score >= 0.4
    }

    if active_features:
        for feature_name, score in sorted(
            active_features.items(), key=lambda x: x[1], reverse=True
        ):
            knowledge = FORENSIC_KNOWLEDGE.get(feature_name)
            if knowledge:
                context_parts.append(
                    f"\n[{feature_name.upper()}] Score: {score:.2f} "
                    f"(Correlation: {knowledge['deepfake_correlation']})"
                )
                context_parts.append(f"  Description: {knowledge['description']}")
                context_parts.append(
                    f"  Indicators: {', '.join(knowledge['indicators'])}"
                )
                context_parts.append(
                    f"  Known generators: {', '.join(knowledge['known_generators'])}"
                )
    else:
        context_parts.append("No features above the significance threshold.")

    # ── Section 2: Graph-based reasoning ──
    if graph_summary:
        context_parts.append("\n=== GRAPH ANALYSIS ===")
        if graph_summary.get("artifacts"):
            context_parts.append("Triggered artifacts:")
            for art in graph_summary["artifacts"]:
                context_parts.append(f"  - {art['type']}: {art['label']}")

        if graph_summary.get("inferences"):
            context_parts.append("Inferred conclusions:")
            for inf in graph_summary["inferences"]:
                context_parts.append(f"  - {inf['type']}: {inf['label']}")

    # ── Section 3: Neo4j historical patterns ──
    neo4j_context = _retrieve_from_neo4j(active_features)
    if neo4j_context:
        context_parts.append("\n=== HISTORICAL PATTERN MATCHES ===")
        context_parts.append(neo4j_context)

    return "\n".join(context_parts)


def _retrieve_from_neo4j(active_features: dict) -> str | None:
    """
    Query Neo4j for historical patterns matching the active features.
    Parallelized for performance.
    """
    try:
        from graph_builder import query_related_indicators
        from concurrent.futures import ThreadPoolExecutor
    except ImportError:
        return None

    if not active_features:
        return None

    results = []
    
    def fetch_indicator(feature_name):
        indicators = query_related_indicators(feature_name)
        if not indicators:
            return None
        out = [f"Feature '{feature_name}' historically linked to:"]
        for ind in indicators[:3]: # Limit to top 3 for speed and brevity
            out.append(
                f"  - {ind.get('artifact', 'unknown')} → "
                f"{ind.get('inference', 'unknown')} "
                f"(past score: {ind.get('score', 'N/A')})"
            )
        return "\n".join(out)

    with ThreadPoolExecutor(max_workers=len(active_features)) as executor:
        future_results = list(executor.map(fetch_indicator, active_features.keys()))
        results = [r for r in future_results if r]

    return "\n".join(results) if results else None


def get_forensic_knowledge_for_feature(feature_name: str) -> dict | None:
    """Get the built-in forensic knowledge entry for a specific feature."""
    return FORENSIC_KNOWLEDGE.get(feature_name)
