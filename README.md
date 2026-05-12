# YouTube Transcript Generator
## Function
This python program takes as input a youtube video URL and generate header section with the date fetched, video URL, video title, uploader, word count, and estimated reading time.
The program then generates a video transcript followed by an AI summary with Deepseek V4. 
To generate a transcript, the program will either download the transcript from youtube if available, and if not, the program will first generate an .mp3 audio file, run it through ahe Whisper AI model, and then generate the transcript from there. Note that this works best with normal human dialog, and does not work well with songs.

## Installation
1. Install the latest version of python
2. Create a virtual environment `python -m venv venv`
3. Activate the venv - For Mac/Linux: `source venv/bin/activate`, for windows: `venv\Scripts\activate`
5. Install ffmpeg — on Mac: `brew install ffmpeg`
4. Run `pip install -r requirements.txt`

## Usage
1. Run `python3 transcript.py`
2. Input YouTube video URL
3. Transcripts are saved to the `transcripts/` folder