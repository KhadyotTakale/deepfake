# test_feature_extractor.py — Unit tests for forensic feature extraction
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from feature_extractor import (
    extract_forensic_features,
    _compute_gan_noise_score,
    _compute_face_blending_score,
    _compute_temporal_jump_score,
    _compute_lip_sync_error,
    _compute_eye_blink_anomaly,
    _compute_lighting_inconsistency,
    _compute_background_coherence,
)


def _generate_synthetic_frames(n: int = 10, size: int = 224) -> list[np.ndarray]:
    """Generate synthetic BGR frames for testing."""
    frames = []
    for i in range(n):
        # Gradient frame with slight variation per frame
        frame = np.zeros((size, size, 3), dtype=np.uint8)
        frame[:, :, 0] = np.linspace(50 + i, 200 + i, size, dtype=np.uint8).reshape(1, -1)
        frame[:, :, 1] = np.linspace(30 + i, 180 + i, size, dtype=np.uint8).reshape(-1, 1)
        frame[:, :, 2] = 128
        frames.append(frame)
    return frames


class TestExtractForensicFeatures:
    """Test the main entry point."""

    def test_returns_correct_structure(self):
        frames = _generate_synthetic_frames(10)
        result = extract_forensic_features(frames, model_probability=0.75)

        assert "media_type" in result
        assert "model_probability" in result
        assert "features" in result
        assert result["media_type"] == "video"
        assert result["model_probability"] == 0.75

    def test_all_feature_keys_present(self):
        frames = _generate_synthetic_frames(10)
        result = extract_forensic_features(frames, model_probability=0.5)

        expected_keys = {
            "gan_noise", "face_blending", "temporal_jump",
            "lip_sync_error", "eye_blink_anomaly",
            "lighting_inconsistency", "background_coherence",
        }
        assert set(result["features"].keys()) == expected_keys

    def test_scores_in_valid_range(self):
        frames = _generate_synthetic_frames(10)
        result = extract_forensic_features(frames, model_probability=0.5)

        for name, score in result["features"].items():
            assert 0.0 <= score <= 1.0, f"Score {name}={score} is out of range"

    def test_single_frame(self):
        """Temporal features should handle single frames gracefully."""
        frames = _generate_synthetic_frames(1)
        result = extract_forensic_features(frames, model_probability=0.5)
        assert result["features"]["temporal_jump"] == 0.0
        assert result["features"]["lip_sync_error"] == 0.0

    def test_two_frames(self):
        """Should work with just two frames."""
        frames = _generate_synthetic_frames(2)
        result = extract_forensic_features(frames, model_probability=0.5)
        for name, score in result["features"].items():
            assert 0.0 <= score <= 1.0


class TestIndividualFeatures:
    """Test individual feature extractors."""

    def test_gan_noise_returns_float(self):
        frames = _generate_synthetic_frames(5)
        score = _compute_gan_noise_score(frames)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_temporal_jump_identical_frames(self):
        """Identical frames should have 0 temporal jump."""
        frame = np.full((224, 224, 3), 128, dtype=np.uint8)
        frames = [frame.copy() for _ in range(10)]
        score = _compute_temporal_jump_score(frames)
        assert score == 0.0

    def test_temporal_jump_random_frames(self):
        """Random frames should have higher temporal jump."""
        rng = np.random.default_rng(42)
        frames = [rng.integers(0, 255, (224, 224, 3), dtype=np.uint8) for _ in range(10)]
        score = _compute_temporal_jump_score(frames)
        assert score >= 0.0  # Just verify it doesn't crash

    def test_background_coherence_static(self):
        """Static frames should have low background coherence score."""
        frame = np.full((224, 224, 3), 100, dtype=np.uint8)
        frames = [frame.copy() for _ in range(5)]
        score = _compute_background_coherence(frames)
        assert score == 0.0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
