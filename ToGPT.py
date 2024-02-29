from openai import OpenAI
import json
from envparam import OPENAI_API_KEY

SENTIMENT = """You are fluent in arabic.
Your job is to analyze the sentiment and mood of every line in the conversation and give it a label based on your analysis 
Labels:
      Positive
      Neutral
      Negative
Make sure to read every line and analyze the sentiment of the speaker carefully then add the appropriate label
Always provide your answer in the following format:

[line_num][Label]
"""

SUMMARIZE = """You are fluent in arabic.
Summarize the following conversation between a customer service agent and a customer in arabic
Include the following information if its avaliable : The customer's Complaint and What steps were taken by the agent to address the issue
Carefully read the arabic text again and Include the speaker who is the agent in this converstation in this exact format either @spk_0 or @spk_1 at the end of your summaray"""

CLARITY = """You are fluent in arabic.
Your job is to analyze the clarity of each line of in the conversation and output True or False where:
False: Confusing and unclear
True: Confident and clear

Make sure to carefully read and analyze ever line for clarity then rate it appropriatly.
Always provide your answer in the following format:

[line_num][output]
"""

YESNO = """You are fluent in arabic
Answer the following questions about the following conversation between a customer service agent and a customer in arabic :
[1]Did the Agent use the call the customer by name?
[2]Was the Agent helpful / welcoming in the start of the conversation?

Only answer in Yes or No
"""


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

