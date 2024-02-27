import boto3
import datetime
import urllib.request, json
import os
import time
from collections import Counter
import statistics
from parser_1 import parsePace , parseSpeakers , parseWords ,speechmatics , tokensaver
from ToGPT import *

def aws_contact(file_path,bucket_name,job_name,format,typer,lang):

    transcribe_client = boto3.client('transcribe')
    print(typer)
    s3 = boto3.resource('s3')
    # Upload a new file
    object_name = os.path.basename(file_path)
    with open(file_path, 'rb') as data:
        s3.Bucket(bucket_name).put_object(Key=object_name, Body=data)

    file_uri = "s3://{0}/{1}".format(bucket_name, object_name)

    
    if typer == "text":
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": file_uri},
            MediaFormat=format,
            LanguageCode=lang,
            Settings={"ShowSpeakerLabels" : True ,
                      "MaxSpeakerLabels" : 2})
    else:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": file_uri},
            MediaFormat=format,
            LanguageCode=lang,
            Subtitles= {'Formats' : [typer]},
            Settings={"ShowSpeakerLabels" : True ,
                      "MaxSpeakerLabels" : 2})   #Send proper format type

    #Main initilization of API request
    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job["TranscriptionJob"]["TranscriptionJobStatus"]


        if job_status in ["COMPLETED", "FAILED"]:
            print(f"Job {job_name} is {job_status}.")
            if job_status == "COMPLETED": 
                print(
                    f"Download the transcript from\n"
                    f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}."
                    )
                if typer == 'text':
                    download = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                else:
                    download = job['TranscriptionJob']['Subtitles']['SubtitleFileUris'][0] #Slicing URL
                    print(download)
                break
            else:
                print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)
    if typer == "text":
        with urllib.request.urlopen(download) as url:
            data = json.load(url)
            labels = data['results']['speaker_labels']['segments']
            speaker_start_times={}
            line = parseSpeakers(data, labels, speaker_start_times)
            tokensaver = parseSpeakers(data, labels, speaker_start_times,False)
            summary = getFromGPT(SUMMARIZE,line).split('@')
            if 'spk_0' in summary[1]:
                line = line.replace("spk_0","Agent")
                line = line.replace("spk_1","Customer")
                line = line.replace("speaker 0","Agent")
                line = line.replace("speaker 1","Customer")
                tokensaver = line.replace("spk_0","Agent")
                tokensaver = tokensaver.replace("spk_1","Customer")
                tokensaver = tokensaver.replace("speaker 0","Agent")
                tokensaver = tokensaver.replace("speaker 1","Customer")
                
                
                print("replaced")
            else:
                line = line.replace("spk_1","Agent")
                line = line.replace("spk_0","Customer")
                line = line.replace("speaker 1","Agent")
                line = line.replace("speaker 0","Customer")
                tokensaver = tokensaver.replace("spk_1","Agent")
                tokensaver = tokensaver.replace("spk_0","Customer")
                tokensaver = tokensaver.replace("speaker 1","Agent")
                tokensaver = tokensaver.replace("speaker 0","Customer")
                print("-replaced")
            senti = getFromGPT(SENTIMENT,tokensaver)
            clarityscore = getFromGPT(CLARITY,tokensaver)
            avg1 , avg2 , total1 , total2 = parsePace(data)
            line = line + '\nspeaker 0 pace :' + str(int(avg1)) + " WPM" + "  Spoke for a total of " + str(int(total1)) + " Seconds" + '\nspeaker 1 pace :' + str(int(avg2)) + " WPM" + "  Spoke for a total of " + str(int(total2)) + " Seconds"
            pause_counter1 , pause_counter2 , sp1_delay ,sp2_delay ,interrupts1 ,interrupts2 = speechmatics(data)
            line = line + '\nPauses for speaker 0 : ' + str(pause_counter1)
            line = line + '\nPauses for speaker 1 : ' + str(pause_counter2)
            line = line + '\nInterrupts for speaker 0 : ' + str(interrupts1)
            line = line + '\nInterrupts for speaker 1 : ' + str(interrupts2)
            line = line + '\nTotal Delay for speaker 0 : ' + str(int(sp1_delay))
            line = line + '\nTotal Delay for speaker 1 : ' + str(int(sp2_delay))
            if 'spk_0' in summary[1]:
                line = line.replace("spk_0","Agent")
                line = line.replace("spk_1","Customer")
                line = line.replace("speaker 0","Agent")
                line = line.replace("speaker 1","Customer")
                print("replaced")
            else:
                line = line.replace("spk_1","Agent")
                line = line.replace("spk_0","Customer")
                line = line.replace("speaker 1","Agent")
                line = line.replace("speaker 0","Customer")
                print("-replaced")
            line = line + '\n' + summary[0] + "Agent : " + '\n'+  summary[1]+ '\n' + senti + '\n' + clarityscore + '\n' + '\n' + tokensaver
        if data :
            return line #Return URL for redirect
    else:
        return download
        



