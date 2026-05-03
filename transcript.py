from datetime import date
import os

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
from dotenv import load_dotenv
from openai import OpenAI
import yt_dlp
import whisper
import re
import textwrap

load_dotenv()

# defining a function that takes video id and returns cleaned transcript
def fetch_transcript(api, video_id):
    transcript = api.fetch(video_id) #use the fetch method from the api class to get the transcript based on video id
    
    lines = []
    for snippet in transcript:
        lines.append(snippet.text.replace("\n", " "))
            
    clean_transcript = " ".join(lines)
    clean_transcript = textwrap.fill(clean_transcript, width=80)
    return clean_transcript

def build_finished_transcript(clean_transcript, url):       
    today = date.today()
    word_count = len(clean_transcript.split())

    adult_reading_time = 200 #words per minute
    reading_time = round(word_count/adult_reading_time)

    header = f"Date fetched: {today}\nVideo URL: {url}\nWord count: {word_count}\nEstimated Reading Time: {reading_time} minutes\n"
    finished_transcript = header + clean_transcript

    return finished_transcript, word_count, reading_time


def save_transcript(finished_transcript, filename):
    with open(filename, "w") as f:
        f.write(finished_transcript)
    print(f"Saved to {filename}")


def transcribe_with_whisper(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    audio_filename =f"{video_id}"
    audio_path = f"{audio_filename}.mp3"
    ydl_opts = {
        "format": "bestaudio/best",             # download the best quality audio available
        "outtmpl": audio_filename,              # save with out chosen filename
        "postprocessors": [{                    # convert to mp3 after download
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
        "quiet": True,                          # suppress yt-dlp's own output
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    model = whisper.load_model("base")          # Loads whisper AI model into memory
    result = model.transcribe(audio_path)       # Runs the audio file through the model
    clean_transcript = result["text"]           # Extracts just the text from the result dictionary

    os.remove(audio_path)
    return clean_transcript

def fetch_video_title(video_id):        # Function to fetch video title from metadata
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "skip_download" : True,         # Don't download anything
        "quiet": True                   # Suppress output
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)

    return info["title"]

def summarize_transcript(clean_transcript):
    client = OpenAI (
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role":"system", "content": """You are a helpful assistant that summarises video transcripts. 
            If the content is educational or informational, produce a structured summary with these sections:
            - Overview: a 2-3 sentence summary of the video
            - Key Concepts: important terms and definitions as bullet points
            - Main Points: the core ideas and arguments as bullet points
            - Takeaways: actionable insights or things to remember as bullet points

            If the content is music, poetry, or non-informational, provide a brief 1-2 sentence description of what it is instead."""},
            
            {"role":"user", "content": f"Please summarize this transcript:\n\n{clean_transcript}"}
        ]
    )
    return response.choices[0].message.content

def main():
    # setup
    url = input("Input video URL: ")

    # validation
    if "v=" not in url:
        print("Invalid YouTube URL")
        exit()

    parts = url.split("=", 1)

    video_id = parts[1]
    video_id = video_id.split("&")[0]

    title = fetch_video_title(video_id)         # Fetch video title
    clean_title = re.sub(r'[^\w]', '_', title)  # make filename safe by removing dangerous characters

    os.makedirs("transcripts", exist_ok=True) # make a directory called 'transcripts', only if it does not already exist
    filename = os.path.join("transcripts", f"{clean_title}_{video_id}.txt") # Build the file path

    if os.path.exists(filename):
        print(f"Transcript already exists at {filename}")
        return

    api = YouTubeTranscriptApi() # instantiate an instance of the YoutubeTranscriptApi class

    try:
        clean_transcript = fetch_transcript(api, video_id) # call the fetch_trancript() function
        
    except (NoTranscriptFound, TranscriptsDisabled):
        clean_transcript = transcribe_with_whisper(video_id)    

    except VideoUnavailable:
        print(f"This video is unavailable or does not exist")
        return

    finished_transcript, word_count, reading_time = build_finished_transcript(clean_transcript, url) # call the build_finished_transcript() function
    save_transcript(finished_transcript, filename)

    # Generate AI summary through deepseek API
    try:
        summary = summarize_transcript(clean_transcript)
        paragraphs = summary.split("\n\n")
        wrapped_paragraphs = [textwrap.fill(p, width=80) for p in paragraphs]
        summary = "\n\n".join(wrapped_paragraphs)
        with open(filename, "a") as f:
            f.write(f"\n\n--- AI SUMMARY ---\n\n {summary}")

    except Exception as e:
        print(f"Summary could not be generated: {e}")


    print(f"Transcript fetched!\nVideo URL:{url}\nWord count:{word_count}\nReading Time:{reading_time}\nSaved to {filename}")

if __name__ == "__main__":
    main()