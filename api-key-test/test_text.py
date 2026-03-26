import os
from dotenv import load_dotenv
import boto3

load_dotenv()

os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("API_KEY", "")

client = boto3.client("bedrock-runtime", region_name="us-west-2")

response = client.converse(
    modelId="us.meta.llama3-3-70b-instruct-v1:0",
    messages=[{
        "role": "user",
        "content": [
            {"text": "Explain what phishing is in 3 sentences."}
        ]
    }]
)

print(response["output"]["message"]["content"][0]["text"])
