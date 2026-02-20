# model.py — EfficientNet-B4 + LSTM Deepfake Video Detector
import torch
import torch.nn as nn
from efficientnet_pytorch import EfficientNet


class DeepfakeDetector(nn.Module):
    """
    Hybrid temporal deepfake detector.
    • EfficientNet-B4 extracts 1792-dim spatial features per frame.
    • Bidirectional LSTM models temporal patterns across a sequence of frames.
    • A fully-connected head outputs a single sigmoid probability (fake score).
    """

    def __init__(self, lstm_hidden: int = 512, lstm_layers: int = 2, dropout: float = 0.3):
        super().__init__()

        # ── Spatial feature extractor (frozen by default) ──
        self.efficientnet = EfficientNet.from_pretrained("efficientnet-b4")
        self.feature_dim = self.efficientnet._fc.in_features  # 1792
        self.efficientnet._fc = nn.Identity()  # remove classification head

        # ── Temporal sequence model ──
        self.lstm = nn.LSTM(
            input_size=self.feature_dim,
            hidden_size=lstm_hidden,
            num_layers=lstm_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if lstm_layers > 1 else 0,
        )

        # ── Classification head ──
        self.classifier = nn.Sequential(
            nn.Linear(lstm_hidden * 2, 256),  # *2 for bidirectional
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, C, H, W) — sequence of face-cropped frames
        Returns:
            (batch, 1) — probability that the video is fake
        """
        batch, seq_len, C, H, W = x.shape

        # Flatten batch and sequence dims for EfficientNet
        x = x.view(batch * seq_len, C, H, W)
        features = self.efficientnet(x)  # (batch*seq_len, 1792)

        # Reshape back to sequence
        features = features.view(batch, seq_len, -1)  # (batch, seq_len, 1792)

        # LSTM over the sequence
        lstm_out, _ = self.lstm(features)  # (batch, seq_len, hidden*2)

        # Use the last timestep output
        last_output = lstm_out[:, -1, :]  # (batch, hidden*2)

        return self.classifier(last_output)  # (batch, 1)
