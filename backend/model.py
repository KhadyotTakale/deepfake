# model.py — Advanced Attention-Enhanced Deepfake Detector
import torch
import torch.nn as nn
import torch.nn.functional as F
from efficientnet_pytorch import EfficientNet
import ssl

# Bypass SSL verification for model downloads (common issue on macOS)
ssl._create_default_https_context = ssl._create_unverified_context

class MultiHeadFrameAttention(nn.Module):
    """
    Learns global dependencies across the video sequence using Self-Attention.
    Unlike Conv1d, this can relate distant frames regardless of their position.
    """
    def __init__(self, in_features, num_heads=8):
        super().__init__()
        self.attn = nn.MultiheadAttention(in_features, num_heads, batch_first=True)
        self.ln = nn.LayerNorm(in_features)

    def forward(self, x):
        # x shape: (batch_size, seq_len, in_features)
        # Self-attention allows each frame to look at all other frames
        attn_out, _ = self.attn(x, x, x)
        return self.ln(x + attn_out)

class DeepfakeDetector(nn.Module):
    """
    Advanced Deepfake Detector:
    1. EfficientNet-B4 for spatial feature extraction.
    2. Multi-Head Self-Attention to capture non-linear temporal artifacts.
    3. Multi-layer Bi-Directional GRU for sequential motion consistency.
    4. Residual Classification Head with diagnostic depth.
    """

    def __init__(self, hidden_dim: int = 512, num_layers: int = 2, dropout: float = 0.4):
        super().__init__()

        # ── 1. Spatial Backbone (EfficientNet-B4) ──
        self.encoder = EfficientNet.from_pretrained("efficientnet-b4")
        self.feature_dim = self.encoder._fc.in_features  # 1792
        self.encoder._fc = nn.Identity()

        # ── 2. Global Frame Attention ──
        # Replaced 1D Conv attention with Multi-Head Self-Attention
        self.attention = MultiHeadFrameAttention(self.feature_dim, num_heads=8)

        # ── 3. Temporal Sequence Modeling (GRU) ──
        self.gru = nn.GRU(
            input_size=self.feature_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
        )

        # ── 4. Classification Head ──
        self.head = nn.Sequential(
            nn.LayerNorm(hidden_dim * 2),
            nn.Linear(hidden_dim * 2, 512),
            nn.SiLU(), # Modern activation
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.SiLU(),
            nn.Linear(256, 1)
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input: (batch, seq_len, C, H, W)
        Output: (batch, 1) - Sigmoid probability
        """
        batch_size, seq_len, c, h, w = x.shape

        # Merge batch and sequence to run through CNN
        x = x.view(batch_size * seq_len, c, h, w)
        features = self.encoder(x) # (batch * seq_len, 1792)

        # Separate sequence back
        features = features.view(batch_size, seq_len, -1) # (batch, seq_len, 1792)

        # Apply Multi-Head Attention
        # Each frame now weights its importance based on ALL other frames
        features = self.attention(features)

        # GRU for sequential motion patterns
        gru_out, _ = self.gru(features) # (batch, seq_len, hidden_dim * 2)

        # Pooling: Combine global average and the max-pooled features for robustness
        avg_pool = torch.mean(gru_out, dim=1)
        max_pool, _ = torch.max(gru_out, dim=1)
        
        # Combined context (Residual style)
        context = avg_pool + max_pool # (batch, hidden_dim * 2)
        
        # Reasoning head
        out = self.head(context)

        return self.sigmoid(out)
