# model.py
import torch
import torch.nn as nn
from torchvision.models import resnext50_32x4d, ResNeXt50_32X4D_Weights
from transformers import ViTModel, ViTConfig

class HybridDeepfakeDetector(nn.Module):
    def __init__(self):
        super(HybridDeepfakeDetector, self).__init__()
        weights = ResNeXt50_32X4D_Weights.DEFAULT
        self.resnext = resnext50_32x4d(weights=weights)
        self.resnext.fc = nn.Identity()
        self.vit = ViTModel(ViTConfig(image_size=224, num_channels=3))
        self.flow_cnn = nn.Sequential(
            nn.Conv2d(2, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten()
        )
        self.fc = nn.Sequential(
            nn.Linear(2048 + 768 + 16, 512),
            nn.ReLU(),
            nn.Linear(512, 1),
            nn.Sigmoid()
        )

    def forward(self, img, flow):
        spatial_features = self.resnext(img)
        temporal_features = self.vit(img).last_hidden_state[:, 0, :]
        flow_features = self.flow_cnn(flow)
        combined = torch.cat([spatial_features, temporal_features, flow_features], dim=1)
        return self.fc(combined)
