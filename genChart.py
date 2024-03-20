import librosa
import numpy as np
import matplotlib.pyplot as plt


# Function to analyze loudness of audio file
def analyze_loudness(audio_file, segment_duration):
    y, sr = librosa.load(audio_file)
    segment_samples = int(segment_duration * sr)
    num_segments = len(y) // segment_samples
    rms_values = []

    for i in range(num_segments):
        segment = y[i * segment_samples: (i + 1) * segment_samples]
        rms = librosa.feature.rms(y=segment)
        average_rms = np.mean(rms)
        rms_values.append(average_rms)

    return rms_values


def genChart(audio_file, chartpath, barpath, segment_duration=5):
    segment_rms = analyze_loudness(audio_file, segment_duration)
    avg = np.average(segment_rms)
    high = avg * 1.4
    silent = avg * 0.5
    low = avg * 0.7
    lowcount = 0
    highcount = 0
    normalcount = 0
    segmentsnum = 0
    silentcount = 0
    time = np.arange(0, len(segment_rms) * segment_duration, segment_duration)
    for segment in segment_rms:
        segmentsnum += 1
        if segment < silent:
            silentcount += 1
            continue
        if segment > silent and segment < low:
            lowcount += 1
            continue
        if segment < avg and segment > low and segment < high:
            normalcount += 1
            continue
        if segment > high:
            highcount += 1
    mylabels = ["Silent", "Low", "Normal", "High"]
    pies = np.array([silentcount, lowcount, normalcount, highcount])
    # plt.plot(time, segment_rms)
    # plt.xlabel('Time (seconds)')
    # plt.ylabel('RMS')
    plt.title('Loudness')
    wedge, text = plt.pie(pies, colors=['c', 'b', 'g', 'r'], shadow=True)
    for w in wedge:
        w.set_linewidth(2)
        w.set_edgecolor('black')
    plt.legend(labels=mylabels)
    plt.tight_layout()

    plt.savefig(chartpath)
    plt.close()
    """ plt.plot(time, segment_rms)
    plt.xlabel('Time (seconds)')
    plt.ylabel('RMS')
    plt.axhline(y=avg, color='g', linestyle='-')
    plt.axhline(y=low, color='b', linestyle='-')
    plt.axhline(y=high, color='r', linestyle='-')
    plt.axhline(y=silent, color='r', linestyle='-')
    plt.grid(True)
    plt.show()
    plt.close() """
