import os
from dotenv import load_dotenv
import boto3

load_dotenv()

os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("API_KEY", "")

client = boto3.client("bedrock-runtime", region_name="us-west-2")

with open("image.png", "rb") as f:
    image_bytes = f.read()

response = client.converse(
    # modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    modelId="us.anthropic.claude-sonnet-4-6",
    # modelId='us.meta.llama3-3-70b-instruct-v1:0',
    messages=[{
        "role": "user",
        "content": [
            {"image": {
                "format": "png",
                "source": {"bytes": image_bytes}
            }},
            {"text": "What is in this image?"}
        ]
    }]
)

print(response["output"]["message"]["content"][0]["text"])
