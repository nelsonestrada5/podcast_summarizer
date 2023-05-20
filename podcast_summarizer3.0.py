import openai
import os
import requests
from pydub import AudioSegment
from io import BytesIO
import tempfile
import configparser
import textwrap
import youtube_dl

config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config.get('openai', 'api_key')

downloads_folder = os.path.join(os.getcwd(), 'workspace_files', 'podcasts')
if not os.path.exists(downloads_folder):
    os.makedirs(downloads_folder)

print("Please enter the URL of the podcast you'd like to transcribe (and any flags):")
user_input = input().split()
podcast_url = user_input[0]  # The first part of the input should always be the URL
flags = user_input[1:]  # The rest of the input (if any) will be considered as flags

# Now the rest of the code will work as expected
downloaded_file_path = download_podcast(podcast_url)
test_run = "-t" in flags or "--test" in flags


# Use youtube-dl to download the podcast
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': downloads_folder + '/%(title)s.%(ext)s'
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    info_dict = ydl.extract_info(rss_feed_url, download=True)
    podcast_title = info_dict.get('title', None)
    local_file_path = ydl.prepare_filename(info_dict)

test_run = False
if "-t" in flags or "--test" in flags:
    test_run = True

def transcribe_audio_data(api_key, audio_data):
    openai.api_key = api_key
    transcript = openai.Audio.transcribe("whisper-1", audio_data)
    return transcript["text"]

def transcribe_audio_file(api_key, file_path, test_run=False):
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

def join_transcripts(transcripts):
    joined_transcript = '\n'.join(transcripts)
    print("")
    print("Full transcript:\n", joined_transcript)
    return joined_transcript

def summarize_full_transcript(podcast_title, podcast_transcript, prompt_length=2048):
    try:
        print("")
        print("")
        print("Summarizing full transcript...")
        if len(podcast_transcript.split()) > prompt_length:
            print("Transcript is too long for a single summary. Will be summarized in chunks.")
            return None
        else:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that speaks Spanish perfectly. You keep track of the big picture while handling small tasks methodically."
                },
                {
                    "role": "user",
                    "content": f"Summarize the transcript from a episode of the podcast \"Mi Mejor Versión con Isa Garcia\". The summary should be in spanish and should include the key points discussed in the episode, along with any important quotes or examples mentioned. Try to keep the summary under 2000 tokens. Here is the transcript: {podcast_transcript}"
                }
            ]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=prompt_length,
                n=1,
                stop=None,
                temperature=0.5,
            )
            summary = response['choices'][0]['message']['content'].strip()
            print("Finished summarizing full transcript.")
            print(f"Full Summary: {summary}")
            return summary
    except Exception as e:
        print(f"An error occurred during summarization: {e}")
        return None

def summarize_transcript(podcast_title, podcast_transcript, prompt_length=2000):
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
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=prompt_length,
                n=1,
                stop=None,
                temperature=0.5,
            )
            summary = response['choices'][0]['message']['content'].strip()
            summaries.append(summary)
            print(f"Finished summarizing chunk {i}/{len(transcript_chunks)}. Summary: {summary}")

        print("Summary completed.")
        return ' '.join(summaries)
    except Exception as e:
        print(f"An error occurred during summarization: {e}")
        return None

def summarize_local_podcast(podcast_title, local_file_path):
    transcript = transcribe_audio_file(openai.api_key, downloaded_file_path, test_run)
    if transcript is None:
        return None

    summary = summarize_full_transcript(podcast_title, transcript)
    if summary is None:
        summary = summarize_transcript(podcast_title, transcript)
    return summary


try:
    summary = summarize_local_podcast(podcast_title, local_file_path)
    if summary is not None:
        print("\nPodcast summary:\n", summary)
    else:
        print("\nNo podcast summary was generated due to errors during processing.")
except Exception as e:
    print(f"An error occurred during podcast processing: {e}")
