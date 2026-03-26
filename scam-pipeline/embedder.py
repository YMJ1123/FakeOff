"""
Titan Embedding interface for text and multimodal embeddings.
Uses invoke_model() (NOT converse()).
"""

import base64
import json
import os

import boto3
from dotenv import load_dotenv

from config import (
    BEDROCK_REGION,
    EMBED_MULTIMODAL_MODEL_ID,
    EMBED_TEXT_MODEL_ID,
    EMBEDDING_DIMENSIONS,
)

load_dotenv()
os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("API_KEY", "")

_client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)


def embed_text(text: str, dimensions: int = EMBEDDING_DIMENSIONS) -> list[float]:
    """
    Titan Text Embeddings V2.
    Returns a normalized vector of the specified dimensions.
    """
    response = _client.invoke_model(
        modelId=EMBED_TEXT_MODEL_ID,
        body=json.dumps({
            "inputText": text,
            "dimensions": dimensions,
            "normalize": True,
        }),
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result["embedding"]


def embed_image(image_path: str, dimensions: int = EMBEDDING_DIMENSIONS) -> list[float]:
    """
    Titan Multimodal Embeddings G1 — image only.
    """
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    response = _client.invoke_model(
        modelId=EMBED_MULTIMODAL_MODEL_ID,
        body=json.dumps({
            "inputImage": image_b64,
            "embeddingConfig": {"outputEmbeddingLength": dimensions},
        }),
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result["embedding"]


def embed_text_and_image(text: str, image_path: str,
                         dimensions: int = EMBEDDING_DIMENSIONS) -> list[float]:
    """
    Titan Multimodal Embeddings G1 — text + image combined.
    Output is the averaged embedding of both modalities.
    """
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    response = _client.invoke_model(
        modelId=EMBED_MULTIMODAL_MODEL_ID,
        body=json.dumps({
            "inputText": text,
            "inputImage": image_b64,
            "embeddingConfig": {"outputEmbeddingLength": dimensions},
        }),
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result["embedding"]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


if __name__ == "__main__":
    print("=== Text Embedding Test ===")
    vec1 = embed_text("報稅截止日延長，國稅局提醒儘速申報")
    vec2 = embed_text("我收到國稅局簡訊說退稅失敗要補件")
    vec3 = embed_text("今天天氣很好適合出去玩")

    print(f"vec1 length: {len(vec1)}")
    print(f"sim(報稅新聞, 退稅詐騙): {cosine_similarity(vec1, vec2):.4f}")
    print(f"sim(報稅新聞, 天氣):     {cosine_similarity(vec1, vec3):.4f}")
