from flask import Flask, render_template, request, send_file , flash, url_for, redirect
from aws import aws_contact
from datetime import datetime
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'E:\Transcription\examples'
ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'wav', 'flac', 'ogg', 'amr' , 'webm' , 'm4a'} #All formats supported by AWS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

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
    print(typer)
    processed_text = process_file(file,typer,lang)

    # Process text inline or redirect in case SRT or VTT
    if typer == "text":
        return render_template('index.html', transcription=processed_text)
    else:
        return redirect(processed_text)

# Process the uploaded file using AWS
def process_file(file,typer,lang):
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(file_path)
    bucket_name = 'yk-dev-tts'
    now = datetime.now()
    current_time = now.strftime("%j-%H-%M-%S")  # Job Name saved with current date and time to avoid overlaps 
    job_name = current_time
    filesplit = file_path.split(".")
    format = filesplit[len(filesplit)-1]
    return aws_contact(file_path,bucket_name,job_name,format,typer,lang)

if __name__ == '__main__':
    app.run(debug=True)