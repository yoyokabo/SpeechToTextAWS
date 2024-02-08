import boto3
import time
import urllib.request, json
import os


def aws_contact(file_path,bucket_name,job_name,format,typer):

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
            LanguageCode="en-US")
    else:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": file_uri},
            MediaFormat=format,
            LanguageCode="en-US",
            Subtitles= {'Formats' : [typer]})   #Send proper format type

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
            d = json.load(url)
        
        if d :
            return d["results"]["transcripts"][0]["transcript"] #Return URL for redirect
    else:
        return download


