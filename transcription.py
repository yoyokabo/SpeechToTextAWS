import datetime
from collections import Counter
import statistics
from genChart import genChart
import os
from helpers import stoMSconverted, cleaner
import codecs
from ToGPT import *

DELAY_THRESHOLD = 0.7
MOST_COMMON_WORDS = 3
PAUSE_THRESHOLD = 0.7
CHARTS_DIR = os.path.join(os.getcwd(), 'Charts')
SAVED_DIR = os.path.join(os.getcwd(), 'Saved')


class Transcription():  # Store Transcript and is responsible for sending outputs to GPT Note: Split into Speaker and GPT classes later
    def __init__(
            self,
            data,
            name='json',
            lang='json',
            filepath='json') -> None:
        self.name = name
        self.data = data
        self.lang = lang
        self.filepath = filepath
        self.interrupts1 = 0
        self.interrupts2 = 0
        self.most_used1 = ''
        self.most_used2 = ''
        self.sp1_delay = 0.0
        self.sp2_delay = 0.0
        self.parsePace()
        self.speechmatics()
        self.rawtrans = self.parseSpeakers()
        self.tokensaver = self.parseSpeakers(False)

        pass

    def processWithGPT(self):
        self.agents = getFromGPT(AGENT, self.rawtrans[0:500]).split('@')
        self.tokensaver = self.applySpeakers(self.tokensaver)
        self.rawtrans = self.applySpeakers(self.rawtrans)
        self.summary = getFromGPT(SUMMARIZE, self.rawtrans)
        self.sentiment = cleaner(
            'Neutral', getFromGPT(
                SENTIMENT, self.tokensaver))
        self.clarity = cleaner('True', getFromGPT(CLARITY, self.tokensaver))
        self.yesno = getFromGPT(YESNO, self.tokensaver)
        self.compare = getFromGPT(COMPARE, self.tokensaver)
        self.matched = self.tokensaver  # PlaceHolder for matching later

    def applySpeakers(self, text):
        if 'spk_0' in self.agents[1]:
            text = text.replace("spk_0", "Agent")
            text = text.replace("spk_1", "Customer")
            text = text.replace("speaker 0", "Agent")
            text = text.replace("speaker 1", "Customer")
            self.agent = 0

            print("replaced")
        else:
            text = text.replace("spk_1", "Agent")
            text = text.replace("spk_0", "Customer")
            text = text.replace("speaker 1", "Agent")
            text = text.replace("speaker 0", "Customer")

            self.agent = 1

            print("-replaced")
        return text

    def parseSpeakers(self, raw=True):
        labels = self.data['results']['speaker_labels']['segments']
        speaker_start_times = {}
        for label in labels:
            for item in label['items']:
                speaker_start_times[item['start_time']] = item['speaker_label']
        items = self.data['results']['items']
        lines = []
        line = ''
        time = 0
        timesc = 0
        speaker = 'null'
        i = 0
        for item in items:
            i = i + 1
            content = item['alternatives'][0]['content']
            if item.get('start_time'):
                current_speaker = speaker_start_times[item['start_time']]
            elif item['type'] == 'punctuation':
                line = line + content
            if current_speaker != speaker:
                if speaker:
                    lines.append(
                        {'speaker': speaker, 'line': line, 'time': time})
                line = content
                speaker = current_speaker
                time = item['start_time']
            elif item['type'] != 'punctuation':
                line = line + ' ' + content
        lines.append({'speaker': speaker, 'line': line, 'time': time})
        sorted_lines = sorted(lines, key=lambda k: float(k['time']))

        self.speaker1 = ""
        self.speaker2 = ""
        for line_data in sorted_lines:
            if line_data.get('speaker') == "spk_0":
                self.speaker1 = self.speaker1 + line_data.get('line')
            else:
                self.speaker2 = self.speaker2 + line_data.get('line')
            self.most_used1, self.most_used2 = self.parsewords(
                self.speaker1, self.speaker2)
            if raw:
                line = line + '[' + str(datetime.timedelta(seconds=int(round(float(line_data['time']))))) + \
                    '] ' + line_data.get('speaker') + ': ' + line_data.get('line') + '\n'
            else:
                line = line + '[' + str(timesc) + '] ' + line_data.get(
                    'speaker') + ': ' + line_data.get('line') + '\n'
                timesc += 1
        # '\nspeaker 0 most used words ' + str(self.most_used1) + '\nspeaker 1 most used words ' + str(self.most_used2)
        return line

    def parsewords(self, sp1, sp2):
        split1 = sp1.split()
        counter1 = Counter(split1)
        split2 = sp2.split()
        counter2 = Counter(split2)
        return counter1.most_common(
            MOST_COMMON_WORDS), counter2.most_common(MOST_COMMON_WORDS)

    def parsePace(self):
        segments = self.data['results']['speaker_labels']['segments']
        sp1avg = []
        sp2avg = []
        self.total1 = 0
        self.total2 = 0
        for segment in segments:
            start_time = segment['start_time']
            end_time = segment['end_time']
            speaker_label = segment['speaker_label']
            timediff = float(end_time) - float(start_time)
            wordcount = 0
            for item in segment['items']:
                wordcount += 1
            if speaker_label == "spk_0":
                sp1avg.append(float(wordcount) / timediff)
                self.total1 += timediff
            else:
                sp2avg.append(float(wordcount) / timediff)
                self.total2 += timediff
        avg1 = statistics.fmean(sp1avg)
        avg2 = statistics.fmean(sp2avg)
        self.pace1 = max(int(avg1) * 60, 60)
        self.pace2 = max(int(avg2) * 60, 60)

    def speechmatics(self):
        self.pause_counter1 = 0
        self.pause_counter1s = ''
        self.pause_counter2 = 0
        self.pause_counter2s = ''
        last_speaker = ''
        previous_end_time = 0
        self.sp1_delay = 0
        self.sp1_delays = ''
        self.sp2_delay = 0
        self.sp2_delays = ''
        self.interrupts1 = 0
        self.interrupts1s = ''
        self.interrupts2 = 0
        self.interrupts2s = ''
        segments = self.data['results']['speaker_labels']['segments']
        for segment in segments:
            start_time = segment['start_time']
            end_time = segment['end_time']
            speaker_label = segment['speaker_label']
            if float(previous_end_time) > 0:
                if last_speaker == speaker_label:
                    temp = float(start_time) - float(previous_end_time)
                    if temp > PAUSE_THRESHOLD:
                        if speaker_label == "spk_0":
                            self.pause_counter1 += 1
                            self.pause_counter1s += f"[{self.pause_counter1}]" + "Pause from : " + stoMSconverted(
                                float(previous_end_time)) + "to :" + stoMSconverted(float(start_time)) + '\n'
                        else:
                            self.pause_counter2 += 1
                            self.pause_counter2s += f"[{self.pause_counter2}]" + "Pause from : " + stoMSconverted(
                                float(previous_end_time)) + "to :" + stoMSconverted(float(start_time)) + '\n'
                else:
                    if float(previous_end_time) >= float(start_time):
                        if speaker_label == "spk_0":
                            self.interrupts1 += 1
                            self.interrupts1s += f"[{self.interrupts1}]" + \
                                stoMSconverted(float(start_time)) + '\n'
                        else:
                            self.interrupts2 += 1
                            self.interrupts2s += f"[{self.interrupts2}]" + \
                                stoMSconverted(float(start_time)) + '\n'
                    else:
                        temp = float(start_time) - float(previous_end_time)
                        if temp > DELAY_THRESHOLD:
                            if speaker_label == "spk_0":
                                self.sp1_delay += temp
                                self.sp1_delays += f"[{self.sp1_delay}]" + "Delay from : " + stoMSconverted(
                                    float(previous_end_time)) + "to :" + stoMSconverted(float(start_time)) + '\n'
                            else:
                                self.sp2_delay += temp
                                self.sp2_delays += f"[{self.sp2_delay}]" + "Delay from : " + stoMSconverted(
                                    float(previous_end_time)) + "to :" + stoMSconverted(float(start_time)) + '\n'
            last_speaker = speaker_label
            previous_end_time = end_time

    def saveChart(self, sr=5):
        savepath = os.path.join(CHARTS_DIR, self.name)
        genChart(self.filepath, savepath, sr)
        self.savepath = savepath + ".png"
        return self.savepath

    def matchlines(self):
        splitclarity = self.clarity.split("\n")
        splitsentiment = self.sentiment.split("\n")
        splittoken = self.tokensaver.split('\n')
        if splitclarity:
            extract_numbers = [int(line.split()[0][1:-1])
                               for line in splitclarity]
        if splitsentiment:
            extract_numbers += [int(line.split()[0][1:-1])
                                for line in splitsentiment]
        if extract_numbers:
            self.matched = [line for line in splittoken if int(
                line.split('')[0][1:-1]) in extract_numbers]
        else:
            self.matched = self.tokensaver

    def tostringsave(self):

        self_text = self.rawtrans

        if self.agent:
            msa = str(self.most_used2)
            dla = int(self.sp2_delay)
            inta = self.interrupts2
            psa = self.pause_counter2
            pacea = self.pace2
            talka = int(self.total2)
            msc = str(self.most_used1)
            dlc = int(self.sp1_delay)
            intc = self.interrupts1
            psc = self.pause_counter1
            pacec = self.pace1
            talkc = int(self.total1)
            spechs = "Customer speechmatics :" + "Interrupts speechmatics :" + '\n' + self.interrupts1s + '\n' + \
                "pause speechmatics :" + '\n' + self.pause_counter1s + '\n' + "delays speechmatics :" + '\n' + self.sp1_delays + "\n\n"
            spechs += "Agent speechmatics :" + "Interrupts speechmatics :" + '\n' + self.interrupts2s + '\n' + \
                "pause speechmatics :" + '\n' + self.pause_counter2s + '\n' + "delays speechmatics :" + '\n' + self.sp2_delays + "\n\n"
        else:
            msc = str(self.most_used2)
            dlc = int(self.sp2_delay)
            intc = self.interrupts2
            psc = self.pause_counter2
            pacec = self.pace2
            talkc = int(self.total2)
            msa = str(self.most_used1)
            dla = int(self.sp1_delay)
            inta = self.interrupts1
            psa = self.pause_counter1
            pacea = self.pace1
            talka = int(self.total1)
            spechs = "Agent speechmatics :" + "Interrupts speechmatics :" + '\n' + self.interrupts1s + '\n' + \
                "pause speechmatics :" + '\n' + self.pause_counter1s + "delays speechmatics :" + '\n' + self.sp1_delays + "\n\n"
            spechs += "Customer speechmatics :" + "Interrupts speechmatics :" + '\n' + self.interrupts2s + '\n' + \
                "pause speechmatics :" + '\n' + self.pause_counter2s + "delays speechmatics :" + '\n' + self.sp2_delays + "\n\n"

        senticlear = self.sentiment + "\n\n" + self.clarity + \
            "\n\n" + self.yesno + "\n \n" + self.compare

        tostring = ''
        tostring += "\n\n\n\n\n\n\n\n\n\nAudio File : " + self.filepath
        tostring += "\n\n\n\n\nTranscript : " + self_text
        tostring += "\n\n\n\n\nSummary : " + self.summary
        tostring += "\n\n\n\n\nSpeechmatics Debug : " + spechs
        tostring += "\n\n\n\n\nGPT's outputs : " + senticlear
        tostring += "\n\n\n\n\nToken Debug : " + self.matched

        with codecs.open(os.path.join(SAVED_DIR, self.name), "w", 'utf-8') as file:
            file.write(tostring)
            file.close
