from transcription import *
import json
import codecs


jsonfile = 'jsons/aex5.json'

audiofile = jsonfile.split('.')[0].split('/')[1]

with codecs.open(jsonfile,'r','utf-8') as f:
    data = json.load(f)
    processed = Transcription(data)

processed.processWithGPT()

processed_text = processed.rawtrans

if processed.agent:
        msa = str(processed.most_used2)
        dla = int(processed.sp2_delay)
        inta = processed.interrupts2
        psa = processed.pause_counter2
        pacea = processed.pace2
        talka = int(processed.total2)
        msc = str(processed.most_used1)
        dlc = int(processed.sp1_delay)
        intc = processed.interrupts1
        psc = processed.pause_counter1
        pacec = processed.pace1
        talkc = int(processed.total1)
        spechs = "Customer speechmatics :" + "Interrupts speechmatics :"  + '\n'+ processed.interrupts1s  + '\n'+"pause speechmatics :"  + '\n'+ processed.pause_counter1s  + '\n'+ "delays speechmatics :"  + '\n'+ processed.sp1_delays + "\n\n"
        spechs += "Agent speechmatics :" + "Interrupts speechmatics :"  + '\n'+ processed.interrupts2s  + '\n'+ "pause speechmatics :"  + '\n'+ processed.pause_counter2s  + '\n'+ "delays speechmatics :"  + '\n'+ processed.sp2_delays + "\n\n"
else:
        msc = str(processed.most_used2)
        dlc = int(processed.sp2_delay)
        intc = processed.interrupts2
        psc = processed.pause_counter2
        pacec = processed.pace2
        talkc = int(processed.total2)
        msa = str(processed.most_used1)
        dla = int(processed.sp1_delay)
        inta = processed.interrupts1
        psa = processed.pause_counter1
        pacea = processed.pace1
        talka = int(processed.total1)
        spechs = "Agent speechmatics :" + "Interrupts speechmatics :"  + '\n'+ processed.interrupts1s  + '\n'+"pause speechmatics :"  + '\n'+ processed.pause_counter1s + "delays speechmatics :"  + '\n'+ processed.sp1_delays + "\n\n"
        spechs += "Customer speechmatics :" + "Interrupts speechmatics :"  + '\n'+ processed.interrupts2s  + '\n'+ "pause speechmatics :"  + '\n'+ processed.pause_counter2s + "delays speechmatics :"  + '\n'+ processed.sp2_delays + "\n\n"

senticlear = processed.sentiment + "\n\n" + processed.clarity + "\n\n" + processed.yesno + "\n \n" + processed.compare

tostring = ''
tostring += "\n\n\n\n\n\n\n\n\n\nAudio File : " + audiofile
tostring += "\n\n\n\n\nTranscript : " + processed_text
tostring += "\n\n\n\n\nSummary : " + processed.summary
tostring += "\n\n\n\n\nSpeechmatics Debug : " + spechs
tostring += "\n\n\n\n\nGPT's outputs : " + senticlear
tostring += "\n\n\n\n\nToken Debug : " + processed.matched

with codecs.open('jsonsoutput.txt',"a",'utf-8') as file:
       file.write(tostring)

       
       


