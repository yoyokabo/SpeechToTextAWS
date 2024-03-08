from openai import OpenAI
import json
from envparam import OPENAI_API_KEY
from helpers import chunk_text_if_large

MAXCONTEXT = 8193

QA = """سؤال: هل يُشترط وجود عدد معين من الاشتراكات لتوفير تعويض للمؤمن عليه في حالة وفاته؟
جواب: لا، لا يشترط وجود عدد معين من الاشتراكات لتوفير تعويض للمؤمن عليه في حالة وفاته.

سؤال: ما هي الحالة التي يُثبت فيها العجز الطبيعي خارج خدمة المؤمن عليه؟
جواب: يُثبت العجز الطبيعي سواء كان كليًا أو جزئيًا خارج خدمة المؤمن عليه.

سؤال: ما هي الشروط لاستكمال المؤمن عليه السن خارج خدمته المشمولة؟
جواب: يمكن للمؤمن عليه استكمال السن خارج خدمته المشمولة دون استكمال المدة الموجبة لاستحقاق الراتب (180 اشتراك).

سؤال: ماذا يحدث إذا قام المؤمن عليه الأردني بالاستغناء عن الجنسية الأردنية أو حصل على جنسية أخرى؟
جواب: ينتهي خدمة المؤمن عليه الأردني إذا قام بالاستغناء عن الجنسية الأردنية أو حصل على جنسية أخرى.

سؤال: متى ينتهي خدمة المؤمن عليه الأردني ويحكم عليه بالسجن؟
جواب: ينتهي خدمة المؤمن عليه الأردني ويحكم عليه بالسجن إذا حُكم عليه بحكم قطعي لمدة لا تقل عن سنتين وكان داخل السجن.

سؤال: متى ينتهي خدمة المؤمن عليه الأردني وغير الأردني الذي أكمل سن 55 للذكر والمؤمن عليها 50 أنثى؟
جواب: تنتهي خدمة المؤمن عليه الأردني وغير الأردني الذي أكمل سن 55 للذكر والمؤمن عليها 50 أنثى، شريطة ألا تزيد الاشتراكات عن 83 اشتراك وأن يكون قد انقطع عن الشمول مدة لا تقل عن 36 اشتراك."""


OG = """ بحال توفى المؤمن عليه ولا يشترط وجود عدد اشتراكات . 

 ثبوت حالة العجز الطبيعي سواء كلي او جزئي خارج خدمته المشمولة . 

اكمال المؤمن عليه السن خارج خدمته المشمولة دون اكمال المدة الموجبة لااستحقاق الراتب ( 180 اشتراك ) . 

 اذا كان المؤمن عليه اردني وقام ب الاستغناء عن الجنسية الاردنية او معه جنسية اخرى. 

انتهاء خدمة المؤمن عليه الاردني والحكم عليه بالسجن حكم قطعي لمدة لا تقل عن سنتين ويجب ان يكون داخل السجن . 

 انتهاء خدمة المؤمن عليه الاردني وغير الاردني الذي اكمل سن 55 للذكر والمؤمن عليها 50 انثى , بشرط ان لا تزيد عدد الاشتراكات عن 83 اشتراك وان يكون قد انقطع عن الشمول مدة لا تقل عن 36 اشتراك . 

انتهاء خدمة المؤمن عليه الاردني الحاصل على راتب تقاعد بموجب قانون التقاعد المدني او العسكري شريطة ان تقل اشتراكاته عن 120 اشتراك ولا يقل عمره عن 50 سنه . 

 بحال كان المؤمن عليه عمره اقل من 25 سنة وبهدف دراسة البكالوريوس . 

 فقط ل اردنية الجنسية , انتهاء خدمة المؤمن عليها الاردنية بسبب الزواج والطلاق والترمل . 

 انتهاء خدمة المؤمن عليها الاردنية العزباء 40 وفوق . 

 انتهاء خدمة المؤمن عليه الغير اردني بحال مغادرة البلاد . 

* الجنسيات التي تقوم بصرف تعويض الدفعة الواحدة بسبب مغادرة البلاد دون الحاجة للمغادرة * 

 الفلسطيني – ابناء قطاع غزة – سوري الجنسية – ابناء الاردنيات – زوجات الاردنيين – ازواج الاردنيات   

  

 

 يستطيع الاردني طلب تعويض الدفعة الواحدة 3 مرات خلال فترة شموله بالضمان وبين كل صرف وصرف 60 اشتراك فعلي

"""

KB = QA


SENTIMENT = """You are fluent in arabic.
Your job is to analyze the sentiment of every line in the conversation and give it a label based on your analysis 
Labels:
      Positive
      Neutral
      Negative
Make sure to read every line and analyze the sentiment of the speaker carefully then add the appropriate label
Always provide your answer in the following format:

[line_num][Label]
"""
AGENT = """You are fluent in arabic.
Summarize the following conversation between a customer service agent and a customer in arabic
Include the following information if its avaliable : The customer's Complaint and What steps were taken by the agent to address the issue
Carefully read the arabic text again and Include the speaker who is the agent in this converstation in this exact format either @spk_0 or @spk_1 at the end of your summaray"""

SUMMARIZE = """You are fluent in arabic.
Summarize the following conversation between a customer service agent and a customer in arabic
Include the following information if its avaliable : The customer's Question or Complaint and What steps were taken by the agent to address the issue
Include the important details of the conversation"""

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
[1]Did the Agent use the customer's by name?
[2]Was the Agent helpful / welcoming in the start of the conversation?

Only answer with Yes or No
"""

COMPARE = f"""You are fluent in arabic
You are analyzing a conversation between a customer service agent and a customer in arabic the agents's job is to try to provide accurate information to the customer by using the knowledge base.
Your job is to compare between agent's responses the the customer's questions and the knowledge bases and to check if the agent's responses were accurate to the knowledge base provided and answer the following questions

[1]If the answer to the customer's questions is in the knowledge base did the agent give wrong information when compared to the knowledge base
[2]Did at any point answer a customer' questions with knowledge outside the knowledge base
[3]Were the answers given by the agent to the customer's questions accurate and correct when compared to the knowledge base



Knowledge base : {KB}


"""

def getFromGPT(master,text):
    text = chunk_text_if_large(text)
    response = ''
    for chunk in text:
        response += "\n\n" + callGPT(master,chunk)
    if master == SUMMARIZE:
        response = callGPT(master,response)
    
    return response

def callGPT(master,user):
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  messages=[
    {"role": "system", "content": master},
    {"role": "user", "content": user}
  ],
  temperature=0.2
  
)
    return str(completion.choices[0].message.content)
