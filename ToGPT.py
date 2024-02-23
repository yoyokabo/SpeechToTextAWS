from openai import OpenAI
import json
from envparam import OPENAI_API_KEY

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

userprompt = "بأي وقت شاكرة اختيارك حمادة ويومك سعيد.[0:00:00] null: [0:00:04] spk_0: حمامات ممكن أساعد صباح الخير حبيبتي[0:00:06] spk_1: كيف حالك[0:00:08] spk_0: صباح نوري أهلا.[0:00:10] spk_1: حبيتي تستفسر عن التوظيف عندكم في ال- في المطعم كيف آلية التوظيف[0:00:17] spk_0: توظيف؟[0:00:19] spk_1: أكيد تك توجهي[0:00:21] spk_0: حضرتك على الفرع حضرتك تريدك تتوجهي على الفرع ومن خلاله يزودوك بكافة التفاصيل.[0:00:27] spk_1: اه يعني لو بدي أقدم على فرع مرج الحمام بالفرع نفسه بقدم.[0:00:32] spk_0: بتروحي على نفس الفرع هم بزودوكي بكافة التفاصيل.[0:00:35] spk_1: آه والله طيب شكرا فكرت من عندكم من الفرع الأساسي[0:00:42] spk_0: مش هام أخوي مرة ثانية[0:00:44] spk_1: ولا فكرت من عندكم يعني من أو يعني الفرع الأساسي مش من الفروع الفرعية.[0:00:51] spk_0: إحنا ال call center لجميع أفرح حمادة مش لفرع واحد[0:00:55] spk_1: آه آه يعني تقلي في التقديم عادي أي فرع بدي أقدم فيه باجي على الفرع نصه[0:01:05] spk_0: تمام حضرتك اذا بتحبي ممكن تروحي على الفرع الرئيسي اللي هو فرع الاردن وهناك يودوكي بكافة التفاصيل.[0:01:11] spk_1: خلاص تمام شكرا يعطيكي العافية باي باي باي بالخدمة[0:01:15] spk_0: بأي وقت شاكرة اختيارك حمادة ويومك سعيد."
masterprompt = "You are fluent in arabic. Summarize the following conversation between a customer service agent and a customer in arabic Include the following information if its avaliable : The customer's Complaint and What steps were taken by the agent to solve the issue "
messagestr = getFromGPT(masterprompt,userprompt)

my_str = "Gpts response : " + messagestr 
my_str = my_str.replace('.','\n')

with open('GPToutputs.txt','a',encoding="utf-8") as outfile:
    outfile.write('\n\n' + my_str + '\nMaster Prompt :' + masterprompt + '\nUser Prompt :' + userprompt)

