from moviepy.editor import *


def convert_mpeg_to_wav(mpeg_file):
    wav_file = mpeg_file.rsplit('.', 1)
    wav_file[1] = 'wav'
    wav_file = '.'.join(wav_file)
    try:
        audio_clip = AudioFileClip(mpeg_file)
        audio_clip.write_audiofile(wav_file, codec='pcm_s16le')
        audio_clip.close()
        return wav_file
    except Exception as e:
        print(f"Error converting MPEG to WAV: {e}")
        return False
