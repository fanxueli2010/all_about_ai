from openai import OpenAI

client = OpenAI(
    base_url = 'http://127.0.0.1:11434/v1',
    api_key='ollama', # required, but unused
)

response = client.chat.completions.create(
  model="mistral",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The LA Dodgers won in 2020."},
    {"role": "user", "content": "Where was it played?"}
  ]
)
print(response.choices[0].message.content)