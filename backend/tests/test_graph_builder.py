# test_graph_builder.py — Unit tests for the feature graph builder
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from graph_builder import (
    build_feature_graph,
    compute_graph_score,
    graph_to_summary,
    FEATURE_ARTIFACT_MAP,
)


def _make_payload(features: dict, model_probability: float = 0.8) -> dict:
    """Helper to construct a forensic payload."""
    return {
        "media_type": "video",
        "model_probability": model_probability,
        "features": features,
    }


class TestBuildFeatureGraph:
    """Test graph construction."""

    def test_basic_graph_structure(self):
        payload = _make_payload({
            "gan_noise": 0.9,
            "face_blending": 0.7,
            "temporal_jump": 0.1,
        })
        G = build_feature_graph(payload)

        # Should have: 1 Media + 3 Features + artifacts for gan_noise & face_blending
        media_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Media"]
        feature_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Feature"]

        assert len(media_nodes) == 1
        assert len(feature_nodes) == 3

    def test_artifacts_triggered_above_threshold(self):
        # gan_noise threshold is 0.5, face_blending is 0.45
        payload = _make_payload({
            "gan_noise": 0.8,       # above 0.5 → triggers
            "face_blending": 0.3,   # below 0.45 → does NOT trigger
        })
        G = build_feature_graph(payload)

        artifact_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Artifact"]
        assert len(artifact_nodes) == 1  # Only gan_noise

    def test_no_artifacts_when_all_below_threshold(self):
        payload = _make_payload({
            "gan_noise": 0.1,
            "face_blending": 0.1,
            "temporal_jump": 0.1,
        })
        G = build_feature_graph(payload)

        artifact_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Artifact"]
        assert len(artifact_nodes) == 0

    def test_inference_nodes_created(self):
        # When gan_noise triggers → synthetic_generation → ai_generated_content
        payload = _make_payload({"gan_noise": 0.9})
        G = build_feature_graph(payload)

        inference_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Inference"]
        assert len(inference_nodes) >= 1

    def test_edge_relations(self):
        payload = _make_payload({"gan_noise": 0.9})
        G = build_feature_graph(payload)

        edge_relations = [d.get("relation") for _, _, d in G.edges(data=True)]
        assert "has_feature" in edge_relations
        assert "indicates" in edge_relations
        assert "supports" in edge_relations


class TestComputeGraphScore:
    """Test graph scoring."""

    def test_high_score_when_many_artifacts(self):
        payload = _make_payload({
            "gan_noise": 0.9,
            "face_blending": 0.8,
            "temporal_jump": 0.7,
            "lip_sync_error": 0.6,
        })
        G = build_feature_graph(payload)
        score = compute_graph_score(G)
        assert score > 0.5

    def test_zero_score_when_no_artifacts(self):
        payload = _make_payload({
            "gan_noise": 0.1,
            "face_blending": 0.1,
        })
        G = build_feature_graph(payload)
        score = compute_graph_score(G)
        assert score == 0.0

    def test_score_in_range(self):
        payload = _make_payload({
            "gan_noise": 0.6,
            "face_blending": 0.5,
            "temporal_jump": 0.3,
        })
        G = build_feature_graph(payload)
        score = compute_graph_score(G)
        assert 0.0 <= score <= 1.0


class TestGraphToSummary:
    """Test summary extraction."""

    def test_summary_structure(self):
        payload = _make_payload({"gan_noise": 0.9})
        G = build_feature_graph(payload)
        summary = graph_to_summary(G)

        assert "artifacts" in summary
        assert "inferences" in summary
        assert "reasons" in summary

    def test_reasons_populated(self):
        payload = _make_payload({
            "gan_noise": 0.9,
            "face_blending": 0.8,
        })
        G = build_feature_graph(payload)
        summary = graph_to_summary(G)

        assert len(summary["reasons"]) >= 2


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
