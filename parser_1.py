import json
import os
import time
import datetime
from collections import Counter
import statistics


def parseSpeakers(data, labels, speaker_start_times):
    for label in labels:
     for item in label['items']:
      speaker_start_times[item['start_time']] =item['speaker_label']
    items = data['results']['items']
    lines=[]
    line=''
    time=0
    speaker='null'
    i=0
    for item in items:
     i=i+1
     content = item['alternatives'][0]['content']
     if item.get('start_time'):
      current_speaker=speaker_start_times[item['start_time']]
     elif item['type'] == 'punctuation':
      line = line+content
     if current_speaker != speaker:
      if speaker:
       lines.append({'speaker':speaker, 'line':line, 'time':time})
      line=content
      speaker=current_speaker
      time=item['start_time']
     elif item['type'] != 'punctuation':
      line = line + ' ' + content
    lines.append({'speaker':speaker, 'line':line,'time':time})
    sorted_lines = sorted(lines,key=lambda k: float(k['time']))
    sp1 = ""
    sp2 = ""
    for line_data in sorted_lines:
      if  line_data.get('speaker') == "spk_0":
       sp1 = sp1 + line_data.get('line')
      else :
       sp2 = sp2 + line_data.get('line')
      ms1 , ms2 = parseWords(sp1,sp2,3)
      line=line +'[' + str(datetime.timedelta(seconds=int(round(float(line_data['time']))))) + '] ' + line_data.get('speaker') + ': ' + line_data.get('line') + '\n'
    return line + '\nSpeaker 0 most used words ' + str(ms1) + '\nSpeaker 1 most used words ' + str(ms2)

def parseWords(sp1,sp2,n):
 split1 = sp1.split()
 counter1 = Counter(split1)
 split2 = sp2.split()
 counter2 = Counter(split2)
 return counter1.most_common(n) , counter2.most_common(n)

def parsePace(data):
 segments = data['results']['speaker_labels']['segments']
 sp1total = []
 sp2total = []
 for segment in segments:
  start_time = segment['start_time']
  end_time = segment['end_time']
  speaker_label = segment['speaker_label']
  timediff = float(end_time) - float(start_time)
  wordcount = 0
  for item in segment['items']:
   wordcount += 1
  if speaker_label == "spk_0":
    sp1total.append(float(wordcount)/timediff)
  else:
    sp2total.append(float(wordcount)/timediff)
 avg1 = statistics.fmean(sp1total)
 avg2 = statistics.fmean(sp2total)
 return int(avg1)*60,int(avg2)*60   


 
