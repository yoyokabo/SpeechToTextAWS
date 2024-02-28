import boto3
import datetime
import urllib.request, json
import os
import time
from collections import Counter
import statistics
from transcription import *
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
            transcription = Transcription(data,job_name,lang,file_path)
            
            transcription.processWithGPT()

            """ line = transcription.rawtrans
            line = line + "speaker 0 most used word :" + str(transcription.most_used1) + "\nspeaker 1 most used word :"  + str(transcription.most_used2) + '\n'
            line = line + '\nspeaker 0 pace :' + str(int(transcription.pace1)) + " WPM" + "  Spoke for a total of " + str(int(transcription.total1)) + " Seconds" + '\nspeaker 1 pace :' + str(int(transcription.pace2)) + " WPM" + "  Spoke for a total of " + str(int(transcription.total2)) + " Seconds"
            line = line + '\nPauses for speaker 0 : ' + str(transcription.pause_counter1)
            line = line + '\nPauses for speaker 1 : ' + str(transcription.pause_counter2)
            line = line + '\nInterrupts for speaker 0 : ' + str(transcription.interrupts1)
            line = line + '\nInterrupts for speaker 1 : ' + str(transcription.interrupts2)
            line = line + '\nTotal Delay for speaker 0 : ' + str(int(transcription.sp1_delay))
            line = line + '\nTotal Delay for speaker 1 : ' + str(int(transcription.sp2_delay))
            line = line + '\n' + transcription.summary[0] + "Agent : " + '\n'+  transcription.summary[1]+ '\n' + transcription.sentiment + '\n' + transcription.clarity + '\n' + '\n' + transcription.tokensaver """
            """ line = transcription.applySpeakers(line) """
            savepath = transcription.saveChart()
        if data :
            return transcription 
    else:
        return download #Return URL for redirec
        



