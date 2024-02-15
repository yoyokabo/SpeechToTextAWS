from openai import OpenAI

def getFromGPT(master,user):
    client = OpenAI()

    completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": master},
    {"role": "user", "content": user}
  ]
)
    return str(completion.choices[0].message)