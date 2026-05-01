from datetime import date
import os

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
import yt_dlp
import whisper

# defining a function that takes video id and returns cleaned transcript
def fetch_transcript(api, video_id):
    transcript = api.fetch(video_id) #use the fetch method from the api class to get the transcript based on video id
    
    lines = []
    for snippet in transcript:
        lines.append(snippet.text.replace("\n", " "))
            
    clean_transcript = " ".join(lines)

    return clean_transcript

def build_finished_transcript(clean_transcript, url):
    word_count = len(clean_transcript.split())

    adult_reading_time = 200 #words per minute
    reading_time = round(word_count/adult_reading_time)

    header = f"Video URL: {url}\nWord count: {word_count}\nEstimated Reading Time: {reading_time} minutes\n"
    finished_transcript = header + clean_transcript

    return finished_transcript, word_count, reading_time


def save_transcript(finished_transcript, filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(finished_transcript)
        print(f"Saved to {filename}")
    else:
        print(f"File already exist at {filename}")

def transcribe_with_whisper(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    audio_filename =f"{video_id}"
    audio_path = f"{audio_filename}.mp3"
    ydl_opts = {
        "format": "bestaudio/best",     # download the best quality audio available
        "outtmpl": audio_filename,      # save with out chosen filename
        "postprocessors": [{            # convert to mp3 after download
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
        "quiet": True                 # suppress yt-dlp's own output
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    model = whisper.load_model("base")          # Loads whisper AI model into memory
    result = model.transcribe(audio_path)   # Runs the audio file through the model
    clean_transcript = result["text"]           # Extracts just the text from the result dictionary

    os.remove(audio_path)
    return clean_transcript

def main():
    # setup
    today = date.today()
    url = input("Input video URL: ")

    # validation
    if "v=" not in url:
        print("Invalid YouTube URL")
        exit()

    parts = url.split("=", 1)

    video_id = parts[1]
    video_id = video_id.split("&")[0]

    os.makedirs("transcripts", exist_ok=True) # make a directory called 'transcripts', only if it does not already exist
    filename = os.path.join("transcripts", f"{video_id}_{today}.txt") # Build the file path

    api = YouTubeTranscriptApi() # instantiate an instance of the YoutubeTranscriptApi class

    try:
        clean_transcript = fetch_transcript(api, video_id) # call the fetch_trancript() function
        
    except NoTranscriptFound:
        clean_transcript = transcribe_with_whisper(video_id)    

    except TranscriptsDisabled:
        clean_transcript = transcribe_with_whisper(video_id)    

    except VideoUnavailable:
        print(f"This video is unavailable or does not exist")
        return

    finished_transcript, word_count, reading_time = build_finished_transcript(clean_transcript, url) # call the build_finished_transcript() function
    save_transcript(finished_transcript, filename)
    print(f"Transcript fetched!\nVideo URL:{url}\nWord count:{word_count}\nReading Time:{reading_time}\nSaved to {filename}")

if __name__ == "__main__":
    main()