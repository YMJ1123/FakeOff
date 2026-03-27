"""
Scam Classifier — loads the trained EmbClassifier (adaptive.pt)
and exposes a classify_text() function.

Pipeline: text → Titan Embed (1024-d) → EmbClassifier MLP → scam probability
"""

import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.nn import functional as F

from embedder import embed_text

CHECKPOINT_PATH = Path(__file__).parent.parent / "classifier" / "checkpoints" / "adaptive.pt"
LABELS = ["legitimate", "scam"]


class EmbClassifier(nn.Module):
    def __init__(self, input_dim=1024, hidden_dim=512, n_class=2):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(num_features=hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(num_features=hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, n_class),
        )

    def forward(self, x):
        return self.model(x)


_model = None
_device = torch.device("cpu")


def _load_model():
    global _model
    if _model is not None:
        return _model

    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(f"Checkpoint not found: {CHECKPOINT_PATH}")

    model = EmbClassifier(input_dim=1024, hidden_dim=512, n_class=2)
    ckpt = torch.load(CHECKPOINT_PATH, map_location=_device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(_device)
    model.eval()
    _model = model
    return _model


def classify_text(text: str) -> dict:
    """
    Classify a single text as scam or legitimate.

    Returns:
        {
            "label": "scam" | "legitimate",
            "confidence": float (0-1),
            "scam_probability": float (0-1),
            "legitimate_probability": float (0-1),
        }
    """
    model = _load_model()

    embedding = embed_text(text)
    x = torch.tensor([embedding], dtype=torch.float32, device=_device)

    with torch.no_grad():
        logits = model(x)
        probs = F.softmax(logits, dim=1)[0]

    scam_prob = probs[1].item()
    legit_prob = probs[0].item()
    predicted_idx = int(torch.argmax(probs).item())

    return {
        "label": LABELS[predicted_idx],
        "confidence": max(scam_prob, legit_prob),
        "scam_probability": round(scam_prob, 4),
        "legitimate_probability": round(legit_prob, 4),
    }


if __name__ == "__main__":
    test_texts = [
        "我是台北地檢署檢察官，你涉嫌洗錢案，請立即轉帳到安全帳戶",
        "您好，您的包裹已送達，請到便利商店取件",
        "恭喜您中獎了！請點擊連結領取獎金",
        "明天下午三點開會，記得準備報告",
    ]

    print("Loading classifier model...")
    _load_model()
    print("Model loaded.\n")

    for text in test_texts:
        result = classify_text(text)
        emoji = "🚨" if result["label"] == "scam" else "✅"
        print(f"{emoji} [{result['label'].upper()}] conf={result['confidence']:.3f} scam_p={result['scam_probability']:.3f}")
        print(f"   {text}\n")
