import os
from huggingface_hub import InferenceClient

# Replace with your actual token
TOKEN = "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"

client = InferenceClient(token=TOKEN)

completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3-0324",
    messages=[
        {
            "role": "user",
            "content": "How many 'G's in 'huggingface'?"
        }
    ],
)

print(completion.choices[0].message.content)