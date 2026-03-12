# consensus_engine.py — Ensemble Consensus Decision Engine
# Combines CNN, Graph, and LLM scores using a weighted formula
# to produce the final verdict.

from __future__ import annotations


# ─────────────────────────────────────────────────────────────────────
# Default weights (can be overridden via function parameters)
# ─────────────────────────────────────────────────────────────────────

DEFAULT_WEIGHTS = {
    "cnn": 0.40,   
    "graph": 0.30,
    "llm": 0.30,   
}

# Verdict thresholds (Balanced for False Positives vs Sensitivity)
FAKE_THRESHOLD = 0.72 
REAL_THRESHOLD = 0.42


def compute_consensus(
    cnn_score: float,
    graph_score: float,
    llm_score: float,
    reasons: list[str],
    llm_analysis: str = "",
    weights: dict[str, float] | None = None,
) -> dict:
    """
    Compute the final consensus verdict by combining all pipeline scores.

    Formula:
        final_score = w_cnn * CNN_score + w_graph * Graph_score + w_llm * LLM_score

    Verdict:
        - final_score > 0.70 → FAKE
        - final_score < 0.30 → REAL
        - Otherwise → UNCERTAIN

    Args:
        cnn_score: Deepfake probability from EfficientNet+LSTM (0.0–1.0).
        graph_score: Graph-based confidence from the feature graph (0.0–1.0).
        llm_score: LLM-assessed deepfake probability (0.0–1.0).
        reasons: List of human-readable reason strings (from graph + LLM).
        llm_analysis: Detailed LLM analysis text.
        weights: Optional custom weights dict with keys "cnn", "graph", "llm".

    Returns:
        Final detection result dict matching the API response schema.
    """
    w = weights or DEFAULT_WEIGHTS

    # Ensure weights sum to 1.0 (normalize if needed)
    total_weight = w.get("cnn", 0.5) + w.get("graph", 0.3) + w.get("llm", 0.2)
    w_cnn = w.get("cnn", 0.5) / total_weight
    w_graph = w.get("graph", 0.3) / total_weight
    w_llm = w.get("llm", 0.2) / total_weight

    # Weighted ensemble score
    final_score = (w_cnn * cnn_score) + (w_graph * graph_score) + (w_llm * llm_score)
    
    # ── STABILITY FILTER (False Positive Mitigation) ──
    # If only one of the three components is high, while others are very low,
    # pull the score down (it's likely isolated noise/artefact)
    scores = [cnn_score, graph_score, llm_score]
    high_count = sum(1 for s in scores if s > 0.6)
    
    if high_count == 1:
        # Isolated suspicion: Dampen the score by 20%
        final_score *= 0.8
    elif high_count == 0 and final_score > 0.5:
        # Low consensus: Dampen to uncertain
        final_score *= 0.9

    # ── AGREEMENT BOOSTING ──
    # If all three components agree it's likely fake, boost heavily
    if all(s > 0.55 for s in scores):
        final_score = max(final_score, 0.82)

    final_score = round(min(max(final_score, 0.0), 1.0), 4)

    # Determine verdict
    if final_score >= FAKE_THRESHOLD:
        verdict = "FAKE"
    elif final_score <= REAL_THRESHOLD:
        verdict = "REAL"
    else:
        verdict = "UNCERTAIN"

    # Confidence = how far the score is from the uncertain zone (0.3–0.7)
    if verdict == "FAKE":
        confidence = round(final_score * 100, 1)
    elif verdict == "REAL":
        confidence = round((1.0 - final_score) * 100, 1)
    else:
        # For UNCERTAIN, report the raw score as confidence
        confidence = round(final_score * 100, 1)

    # Build human-readable summary
    summary = _build_summary(verdict, final_score, cnn_score, graph_score, llm_score, llm_analysis)

    # Deduplicate reasons while preserving order
    seen = set()
    unique_reasons = []
    for r in reasons:
        if r and r not in seen:
            unique_reasons.append(r)
            seen.add(r)

    return {
        "verdict": verdict,
        "confidence": confidence,
        "reasons": unique_reasons,
        "summary": summary,
        "pipeline_scores": {
            "cnn_score": round(cnn_score, 4),
            "graph_score": round(graph_score, 4),
            "llm_score": round(llm_score, 4),
            "final_score": final_score,
            "weights": {
                "cnn": round(w_cnn, 2),
                "graph": round(w_graph, 2),
                "llm": round(w_llm, 2),
            },
        },
    }


def _build_summary(
    verdict: str,
    final_score: float,
    cnn_score: float,
    graph_score: float,
    llm_score: float,
    llm_analysis: str,
) -> str:
    """Generate a human-readable summary of the consensus decision."""

    if verdict == "FAKE":
        base = (
            "The media likely contains AI-generated or digitally manipulated content. "
            f"The ensemble pipeline produced a deepfake probability of {final_score:.1%}."
        )
    elif verdict == "REAL":
        base = (
            "The media appears authentic based on multi-stage forensic analysis. "
            f"The ensemble pipeline produced a deepfake probability of {final_score:.1%}."
        )
    else:
        base = (
            "The analysis is inconclusive. Some forensic signals are suspicious, but the "
            f"evidence is not definitive. Ensemble deepfake probability: {final_score:.1%}."
        )

    detail = (
        f" Individual scores — CNN: {cnn_score:.2f}, "
        f"Graph: {graph_score:.2f}, LLM: {llm_score:.2f}."
    )

    # Append LLM analysis if available
    if llm_analysis and len(llm_analysis) > 10:
        detail += f" LLM assessment: {llm_analysis}"

    return base + detail
