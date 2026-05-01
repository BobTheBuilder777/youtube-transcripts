# YouTube Transcript Generator
## Function
This python program takes as input a youtube video URL and generates a transcript, word count, and estimated reading time.

## Installation
1. Install the latest version of python
2. Create a virtual environment `python -m venv venv`
3. Activate the venv - For Mac/Linux: `source venv/bin/activate`, for windows: `venv\Scripts\activate`
5. Install ffmpeg — on Mac: `brew install ffmpeg`
4. Run `pip install -r requirements.txt`

## Usage
1. Run `python3 transcript.py`
2. Input YouTube video URL
3. If no captions are available, this program will generate an .mp3 audio file and run it through the Whisper AI model, which will generate a transcript. Note that this works best with normal human dialog, and does not work well with songs.
4. Transcripts are saved to the `transcripts/` folder