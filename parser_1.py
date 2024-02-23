import json
import os
import time
import datetime
from collections import Counter
import statistics

DELAY_THRESHOLD = 0.7
MOST_COMMON_WORDS = 3
PAUSE_THRESHOLD = 0.7


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
 return counter1.most_common(MOST_COMMON_WORDS) , counter2.most_common(MOST_COMMON_WORDS)

def parsePace(data):
 segments = data['results']['speaker_labels']['segments']
 sp1avg = []
 sp2avg = []
 sp1total = 0
 sp2total = 0
 for segment in segments:
  start_time = segment['start_time']
  end_time = segment['end_time']
  speaker_label = segment['speaker_label']
  timediff = float(end_time) - float(start_time)
  wordcount = 0
  for item in segment['items']:
   wordcount += 1
  if speaker_label == "spk_0":
    sp1avg.append(float(wordcount)/timediff)
    sp1total += timediff
  else:
    sp2avg.append(float(wordcount)/timediff)
    sp2total += timediff
 avg1 = statistics.fmean(sp1avg)
 avg2 = statistics.fmean(sp2avg)
 return max(int(avg1)*60,60), max(int(avg2)*60,60) , sp1total , sp2total

def speechmatics(data):
 pause_counter1 = 0
 pause_counter2 = 0
 last_speaker = ''
 previous_end_time = 0
 sp1_delay = 0
 sp2_delay = 0
 interrupts1 = 0
 interrupts2 = 0
 segments = data['results']['speaker_labels']['segments']
 for segment in segments:
  start_time = segment['start_time']
  end_time = segment['end_time']
  speaker_label = segment['speaker_label']
  if float(previous_end_time) > 0:
   if last_speaker == speaker_label:
    temp = float(start_time) - float(previous_end_time)
    if temp > PAUSE_THRESHOLD:
     if speaker_label == "spk_0":
      pause_counter1 += 1
     else:
      pause_counter2 += 1
   else:
    if float(previous_end_time) >= float(start_time):
     if speaker_label == "spk_0":
      interrupts1 += 1
     else:
      interrupts2 += 1
    else:
     temp = float(start_time) - float(previous_end_time)
     if temp > DELAY_THRESHOLD:
      if speaker_label == "spk_0":
       sp1_delay += temp
     else:
       sp2_delay += temp
  last_speaker = speaker_label
  previous_end_time = end_time
 return pause_counter1 , pause_counter2 , sp1_delay ,sp2_delay ,interrupts1 ,interrupts2