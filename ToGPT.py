from openai import OpenAI
import json
from envparam import OPENAI_API_KEY

SUMMARIZE = "You are fluent in arabic. Summarize the following conversation between a customer service agent and a customer in arabic Include the following information if its avaliable : The customer's Complaint and What steps were taken by the agent to solve the issue include the speaker who is the agent in this converstation in this exact format either @spk_0 or @spk_1 at the end of your summaray"

def getFromGPT(master,user):
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": master},
    {"role": "user", "content": user}
  ]
)
    return str(completion.choices[0].message)



