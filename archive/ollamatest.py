from ollama import chat

print("Starting...")

response = chat(
    model="qwen3:8b",
    messages=[
        {"role": "user", "content": "Say hello"}
    ]
)

print("Got response")
print(response)