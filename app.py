from transcription import *
from flask import Flask, render_template, request, send_file, flash, url_for, redirect
from aws import aws_contact
from datetime import *
import time as ti
import os
from werkzeug.utils import secure_filename
from converter import convert_mpeg_to_wav
from helpers import count_words

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Uploads')
ALLOWED_EXTENSIONS = {
    'mp3',
    'mp4',
    'wav',
    'flac',
    'ogg',
    'amr',
    'webm',
    'm4a',
    'mpeg'}  # All formats supported by AWS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('acess.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If user does not select file, browser also
        # Submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    typer = request.form['typer']
    lang = request.form['lang']
    fillerwords = request.form['filler']
    print(typer)
    processed = process_file(file, typer, lang)
    processed_text = processed.rawtrans
    processed.tostringsave()
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
        spechs = "Customer speechmatics :" + "Interrupts speechmatics :" + '\n' + processed.interrupts1s + '\n' + \
            "pause speechmatics :" + '\n' + processed.pause_counter1s + '\n' + "delays speechmatics :" + '\n' + processed.sp1_delays + "\n\n"
        spechs += "Agent speechmatics :" + "Interrupts speechmatics :" + '\n' + processed.interrupts2s + '\n' + "pause speechmatics :" + \
            '\n' + processed.pause_counter2s + '\n' + "delays speechmatics :" + '\n' + processed.sp2_delays + "\n\n"
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
        spechs = "Agent speechmatics :" + "Interrupts speechmatics :" + '\n' + processed.interrupts1s + '\n' + \
            "pause speechmatics :" + '\n' + processed.pause_counter1s + "delays speechmatics :" + '\n' + processed.sp1_delays + "\n\n"
        spechs += "Customer speechmatics :" + "Interrupts speechmatics :" + '\n' + processed.interrupts2s + '\n' + \
            "pause speechmatics :" + '\n' + processed.pause_counter2s + "delays speechmatics :" + '\n' + processed.sp2_delays + "\n\n"
    senticlear = processed.sentiment + "\n\n" + processed.clarity + \
        "\n\n" + processed.yesno + "\n \n" + processed.compare
    filler = count_words(processed.tokensaver, fillerwords)
    # Process text inline or redirect in case SRT or VTT
    if typer == "text":
        return render_template('acess.html', transcription=processed_text,
                               summary=processed.summary,
                               paceagent=pacea,
                               pacecustomer=pacec,
                               interruptagent=inta,
                               interruptcustomer=intc,
                               delayagent=dla,
                               delaycustomer=dlc,
                               pauseagent=psa,
                               pausecustomer=psc,
                               mostagent=msa,
                               mostcustomer=msc,
                               senticlear=senticlear,
                               talkingagent=talka,
                               talkingcustomer=talkc,
                               tokensaver=processed.matched,
                               png=processed.savepath,
                               filler=filler,
                               spechs=spechs)
    else:
        return redirect(processed_text)

# Process the uploaded file using AWS


def process_file(file, typer, lang): #Send file to AWS and returns Transcription Object
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if file.filename.rsplit('.', 1)[1].lower() == 'mpeg':
        file_path = convert_mpeg_to_wav(file_path)
        print('aha caught ya')
    print(file_path)
    bucket_name = 'yk-dev-tts1'
    now = datetime.now()
    # Job Name saved with current date and time to avoid overlaps
    current_time = now.strftime("%j-%H-%M-%S")
    job_name = current_time
    filesplit = file_path.split(".")
    format = filesplit[len(filesplit) - 1]
    return aws_contact(file_path, bucket_name, job_name, format, typer, lang)


if __name__ == '__main__':
    app.run(debug=True)
