# SpeechToTextAWS
Web Application that take video/audio from user and outputs transcription using Flask and Boto3

Supported formats mp3 , mp4 , wav , flac , ogg , amr , webm , m4a , mpeg.

2/12 - Added support for Arabic , Diraization , WPM and Most used words.

2/13 - Added Interruptions , Delays and Pauses detection.

2/15 - Added support for MPEG by converting to WAV and Added GPT function.

2/25 - Added GPT summrarization

2/26 - Added Speaker identfication , Sentiment analysis and Clarity analysis with GPT

2/28 - Refactored code for readability and easier modification and feature addition in the future. Looks alot cleaner now :D

2/29 - Prettier HTML. Added loundness detction saved in piechart on server.

2/29 - Some extra GPT functionality

3/5 - Added debug for speechmatics

3/8 - Added json processor and added chunking to GPT to accept inputs of any length and cleaned GPT output
