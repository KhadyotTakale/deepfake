# model.py — Advanced Attention-Enhanced Deepfake Detector
import torch
import torch.nn as nn
import torch.nn.functional as F
from efficientnet_pytorch import EfficientNet

class SpatialAttention(nn.Module):
    """
    Learns where to look in the feature map to identify manipulation artifacts.
    """
    def __init__(self, in_features):
        super().__init__()
        self.conv1 = nn.Conv1d(in_features, in_features // 4, kernel_size=1)
        self.conv2 = nn.Conv1d(in_features // 4, 1, kernel_size=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch_size, seq_len, in_features)
        # We treat the sequence as a 1D signal to find temporal-spatial focal points
        attn = x.transpose(1, 2) # (batch, in_features, seq_len)
        attn = F.relu(self.conv1(attn))
        attn = self.conv2(attn) # (batch, 1, seq_len)
        attn = self.sigmoid(attn).transpose(1, 2) # (batch, seq_len, 1)
        return x * attn

class DeepfakeDetector(nn.Module):
    """
    Advanced Deepfake Detector:
    1. EfficientNet-B4 for spatial feature extraction.
    2. Spatial-Temporal Attention layer to weigh important frames/regions.
    3. Multi-layer Bi-Directional GRU (usually more efficient than LSTM for this).
    4. Dense Reasoning Head with LayerNorm and Dropout.
    """

    def __init__(self, hidden_dim: int = 512, num_layers: int = 2, dropout: float = 0.4):
        super().__init__()

        # ── 1. Spatial Backone (EfficientNet-B4) ──
        self.encoder = EfficientNet.from_pretrained("efficientnet-b4")
        self.feature_dim = self.encoder._fc.in_features  # 1792
        self.encoder._fc = nn.Identity()

        # ── 2. Frame Attention ──
        self.attention = SpatialAttention(self.feature_dim)

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
        self.ln = nn.LayerNorm(hidden_dim * 2)
        self.fc1 = nn.Linear(hidden_dim * 2, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 1)
        
        self.dropout = nn.Dropout(dropout)
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

        # Apply Attention
        features = self.attention(features)

        # GRU for temporal patterns
        gru_out, _ = self.gru(features) # (batch, seq_len, hidden_dim * 2)

        # Pooling: Use both adaptive average and the last hidden state
        avg_pool = torch.mean(gru_out, dim=1)
        last_hidden = gru_out[:, -1, :]
        
        # Combined context
        context = avg_pool + last_hidden # (batch, hidden_dim * 2)
        
        # Reasoning head
        out = self.ln(context)
        out = F.relu(self.fc1(out))
        out = self.dropout(out)
        out = F.relu(self.fc2(out))
        out = self.fc3(out)

        return self.sigmoid(out)
