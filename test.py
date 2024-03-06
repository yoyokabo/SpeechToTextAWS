from openai import OpenAI
import json
from envparam import OPENAI_API_KEY


def getFromGPT(master,user):
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  messages=[
    {"role": "system", "content": master},
    {"role": "user", "content": user}
  ],
  temperature=0,
  max_tokens=1024
  
)
    
    return str(completion.choices[0].message.content)

print(getFromGPT("",'tell me a fun story about hippos'))