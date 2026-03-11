# test_consensus_engine.py — Unit tests for the consensus decision engine
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from consensus_engine import compute_consensus


class TestComputeConsensus:
    """Test the ensemble scoring and verdict logic."""

    def test_fake_verdict(self):
        result = compute_consensus(
            cnn_score=0.95,
            graph_score=0.85,
            llm_score=0.90,
            reasons=["GAN fingerprint", "Face blending"],
        )
        assert result["verdict"] == "FAKE"
        assert result["confidence"] > 80

    def test_real_verdict(self):
        result = compute_consensus(
            cnn_score=0.05,
            graph_score=0.10,
            llm_score=0.08,
            reasons=["No anomalies detected"],
        )
        assert result["verdict"] == "REAL"
        assert result["confidence"] > 80

    def test_uncertain_verdict(self):
        result = compute_consensus(
            cnn_score=0.50,
            graph_score=0.45,
            llm_score=0.55,
            reasons=["Mixed signals"],
        )
        assert result["verdict"] == "UNCERTAIN"

    def test_pipeline_scores_present(self):
        result = compute_consensus(
            cnn_score=0.80,
            graph_score=0.70,
            llm_score=0.60,
            reasons=["test"],
        )
        assert "pipeline_scores" in result
        assert "cnn_score" in result["pipeline_scores"]
        assert "graph_score" in result["pipeline_scores"]
        assert "llm_score" in result["pipeline_scores"]
        assert "final_score" in result["pipeline_scores"]

    def test_default_weights(self):
        result = compute_consensus(
            cnn_score=1.0,
            graph_score=0.0,
            llm_score=0.0,
            reasons=[],
        )
        # With default weights: 0.5*1.0 + 0.3*0.0 + 0.2*0.0 = 0.5
        assert result["pipeline_scores"]["final_score"] == 0.5

    def test_custom_weights(self):
        result = compute_consensus(
            cnn_score=1.0,
            graph_score=0.0,
            llm_score=0.0,
            reasons=[],
            weights={"cnn": 1.0, "graph": 0.0, "llm": 0.0},
        )
        # All weight on CNN → final_score = 1.0
        assert result["pipeline_scores"]["final_score"] == 1.0
        assert result["verdict"] == "FAKE"

    def test_reasons_deduplication(self):
        result = compute_consensus(
            cnn_score=0.8,
            graph_score=0.7,
            llm_score=0.6,
            reasons=["duplicate reason", "duplicate reason", "unique reason"],
        )
        assert len(result["reasons"]) == 2

    def test_score_clamping(self):
        """Scores should be clamped to [0, 1]."""
        result = compute_consensus(
            cnn_score=1.5,  # Out of range
            graph_score=1.2,
            llm_score=1.1,
            reasons=[],
        )
        assert result["pipeline_scores"]["final_score"] <= 1.0

    def test_summary_non_empty(self):
        result = compute_consensus(
            cnn_score=0.8,
            graph_score=0.7,
            llm_score=0.6,
            reasons=["test"],
        )
        assert len(result["summary"]) > 20


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
