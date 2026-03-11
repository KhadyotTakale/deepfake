import torch
from model import DeepfakeDetector
import os

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Testing DeepfakeDetector on {device}...")

try:
    model = DeepfakeDetector().to(device)
    print("✅ Model initialized successfully")
    
    # Test forward pass
    x = torch.randn(1, 5, 3, 224, 224).to(device)
    out = model(x)
    print(f"✅ Forward pass successful: output shape {out.shape}")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    os._exit(1)
