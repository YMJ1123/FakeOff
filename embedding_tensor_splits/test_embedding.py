import os
import json
import base64
from dotenv import load_dotenv
import boto3

load_dotenv()

os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("API_KEY", "")

client = boto3.client("bedrock-runtime", region_name="us-west-2")


def test_text_embedding_v2():
    """Titan Text Embeddings V2 - 文字轉向量"""
    print("=" * 60)
    print("TEST 1: Titan Text Embeddings V2")
    print("=" * 60)

    response = client.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({
            "inputText": "This is a test sentence for embedding.",
            "dimensions": 1024,
            "normalize": True
        }),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    embedding = result["embedding"]
    print(f"Embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print()


def test_multimodal_text():
    """Titan Multimodal Embeddings G1 - 純文字"""
    print("=" * 60)
    print("TEST 2: Titan Multimodal Embeddings G1 (text only)")
    print("=" * 60)

    response = client.invoke_model(
        modelId="amazon.titan-embed-image-v1",
        body=json.dumps({
            "inputText": "endoscopic image of a colorectal lesion",
            "embeddingConfig": {"outputEmbeddingLength": 1024}
        }),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    embedding = result["embedding"]
    print(f"Embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"Token count: {result.get('inputTextTokenCount')}")
    print()


def test_multimodal_image():
    """Titan Multimodal Embeddings G1 - 圖片"""
    print("=" * 60)
    print("TEST 3: Titan Multimodal Embeddings G1 (image only)")
    print("=" * 60)

    with open("image.png", "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    response = client.invoke_model(
        modelId="amazon.titan-embed-image-v1",
        body=json.dumps({
            "inputImage": image_b64,
            "embeddingConfig": {"outputEmbeddingLength": 1024}
        }),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    embedding = result["embedding"]
    print(f"Embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print()


def test_multimodal_text_and_image():
    """Titan Multimodal Embeddings G1 - 圖文混合"""
    print("=" * 60)
    print("TEST 4: Titan Multimodal Embeddings G1 (text + image)")
    print("=" * 60)

    with open("image.png", "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    response = client.invoke_model(
        modelId="amazon.titan-embed-image-v1",
        body=json.dumps({
            "inputText": "A colorful test image with geometric shapes",
            "inputImage": image_b64,
            "embeddingConfig": {"outputEmbeddingLength": 1024}
        }),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    embedding = result["embedding"]
    print(f"Embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"Token count: {result.get('inputTextTokenCount')}")
    print()


if __name__ == "__main__":
    test_text_embedding_v2()
    test_multimodal_text()
    test_multimodal_image()
    test_multimodal_text_and_image()
    print("All embedding tests completed!")
