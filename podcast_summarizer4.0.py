import openai
import os
import requests
from pydub import AudioSegment
from io import BytesIO
import tempfile
import configparser
import textwrap
import youtube_dl
import re
import time

# Load the OpenAI API key from a config file
config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config.get('openai', 'api_key')

# Set up the folder to download podcasts to
downloads_folder = os.path.join(os.getcwd(), 'workspace_files', 'podcasts')
if not os.path.exists(downloads_folder):
    os.makedirs(downloads_folder)

print("Please enter the URL of the podcast you'd like to transcribe (and any flags):")
user_input = input().split()
podcast_url = user_input[0]  # The first part of the input should always be the URL
flags = user_input[1:]  # The rest of the input (if any) will be considered as flags
test_run = "-t" in flags or "--test" in flags

# ------------- DOWNLOADING FUNCTIONS -------------

def download_podcast(podcast_url):
    """
    Downloads the podcast from the given URL and saves it as an MP3 file.

    Parameters:
    podcast_url (str): The URL of the podcast to download.

    Returns:
    str: The local file path of the downloaded podcast.
    str: The title of the podcast.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': downloads_folder + '/%(title)s.%(ext)s',
        'nopostoverwrites': False,
        'nooverwrites': True,
        'noprogress': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(podcast_url, download=False)
        podcast_title = info_dict.get('title', None)
        local_file_path = ydl.prepare_filename(info_dict)

    if not os.path.isfile(local_file_path):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([podcast_url])

    return local_file_path, podcast_title

# ------------- TRANSCRIPTION FUNCTIONS -------------

def transcribe_audio_data(api_key, audio_data):
    """
    Transcribes the given audio data using OpenAI's Whisper ASR system. This function is used inside transcribe_audio_file().

    Parameters:
    api_key (str): Your OpenAI API key.
    audio_data (BytesIO): The audio data to transcribe.

    Returns:
    str: The transcription of the audio data.
    """
    openai.api_key = api_key
    transcript = openai.Audio.transcribe("whisper-1", audio_data)
    return transcript["text"]

def transcribe_audio_file(api_key, file_path, test_run=False):
    """
    Transcribes the given audio file using OpenAI's Whisper ASR system. But first it breaks down the file into predetermined chunks so that it doesn't reach token limits.

    Parameters:
    api_key (str): Your OpenAI API key.
    file_path (str): The local file path of the audio file to transcribe.
    test_run (bool, optional): If True, only the first 5 minutes of the audio file are transcribed.

    Returns:
    str: The transcription of the audio file.
    """
    try:
        print("Loading audio file...")
        audio = AudioSegment.from_file(file_path)
        chunk_length_ms = 1000 * 60 * 1  # 1-minute chunks
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
        transcripts = []

        if test_run:
            chunks = chunks[:5]  # If it's a test run, only consider the first 5 chunks

        print(f"Audio file loaded. Transcribing {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks, start=1):
            print(f"")
            print(f"Transcribing chunk {i}/{len(chunks)}...")
            with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_audio_file:
                chunk.export(temp_audio_file.name, format="mp3")
                temp_audio_file.seek(0)  # Reset the file pointer to the beginning
                transcript = transcribe_audio_data(api_key, temp_audio_file)
                start_time = i - 1
                end_time = i
                transcripts.append(f"(Timestamp: {start_time}:00-{end_time}:00 minutes)\n{transcript}")
            print(f"Finished transcribing chunk {i}/{len(chunks)}")
            print(f"Transcription for chunk {i}: {transcript}")  # Print the transcript for the current chunk

        print("Transcription completed.")
        print("")
        print(f"Complete transcript: {transcripts}")
        return '\n'.join(transcripts)
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None

# ------------- SUMMARIZATION FUNCTIONS -------------

def summarize_transcript(podcast_title, podcast_transcript, prompt_length=2000):
    """
    Summarizes the given podcast transcript in chunks using OpenAI's GPT-3.5-turbo model.

    Parameters:
    podcast_title (str): The title of the podcast.
    podcast_transcript (str): The transcript of the podcast to summarize.
    prompt_length (int, optional): The maximum length of each chunk of the summary.

    Returns:
    str: The summary of the podcast transcript.
    """
    try:
        print("")
        print("")
        print("Summarizing transcript...")

        transcript_chunks = textwrap.wrap(podcast_transcript, prompt_length - 200)  # Split the transcript into smaller chunks
        summaries = []

        for i, chunk in enumerate(transcript_chunks, start=1):
            print("")
            print(f"Summarizing chunk {i}/{len(transcript_chunks)}...")
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that speaks Spanish perfectly. You keep track of the big picture while handling small tasks methodically."
                },
                {
                    "role": "user",
                    "content": f"Summarize the transcript from a episode of the podcast \"Mi Mejor Versión con Isa Garcia\". The summary should be in spanish and should include the key points discussed in the episode, along with any important quotes or examples mentioned. Try to keep the summary under 2000 tokens. Here is the transcript: {chunk}"
                }
            ]
            response = safe_summary(openai.api_key, messages)
            summary = response['choices'][0]['message']['content'].strip()
            summaries.append(summary)
            print(f"Finished summarizing chunk {i}/{len(transcript_chunks)}. Summary: {summary}")

        print("Summary completed.")
        return ' '.join(summaries)
    except Exception as e:
        print(f"An error occurred during summarization: {e}")
        return None

def safe_summary(api_key, messages, attempts=5, cooldown=5):
    """
    This function is called from within summarize_transcript(). This function
    is there to help with the OpenAI rate limits.

    It slows down the requests and also adds retry logic.
    """
    for _ in range(attempts):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=2000,
                n=1,
                stop=None,
                temperature=0.5,
            )
            return response
        except Exception as e:
            print(f"Error: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(cooldown)
    print("Failed to get summary after multiple attempts.")
    return None


# ------------- SCRIPT SAVING FUNCTION -------------

def save_transcript_to_file(transcript, podcast_title):
    # Sanitize the podcast title to use it as a filename
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", podcast_title)  # remove characters not safe for filenames
    safe_filename = safe_filename[:200]  # truncate if needed to avoid extremely long filenames

    scripts_folder = os.path.join(downloads_folder, 'podcast_scripts')
    if not os.path.exists(scripts_folder):
        os.makedirs(scripts_folder)  # create the scripts folder if it doesn't exist

    file_path = os.path.join(scripts_folder, safe_filename + ".txt")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(transcript)

    print(f"Transcript saved to {file_path}")

# ------------- MAIN FUNCTION -------------

def summarize_local_podcast(podcast_url):
    """
    Downloads, transcribes, saves script and summarizes a podcast from the given URL.

    Parameters:
    podcast_url (str): The URL of the podcast to process.

    Returns:
    str: The summary of the podcast.
    """
    local_file_path, podcast_title = download_podcast(podcast_url)
    transcript = transcribe_audio_file(openai.api_key, local_file_path, test_run)
    if transcript is None:
        return

    save_transcript_to_file(transcript, podcast_title)

    summary = summarize_transcript(podcast_title, transcript)

try:
    summary = summarize_local_podcast(podcast_url)
    if summary is not None:
        print("\nPodcast summary:\n", summary)
    else:
        print("\nNo podcast summary was generated due to errors during processing.")
except Exception as e:
    print(f"An error occurred during podcast processing: {e}")
