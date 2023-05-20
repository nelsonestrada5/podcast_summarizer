import openai
import os
import requests
from pydub import AudioSegment
from io import BytesIO
import tempfile
import configparser
import textwrap

config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config.get('openai', 'api_key')

podcast_title = "Estoy Escribiendo, por Isa Garcia"
downloads_folder = os.path.expanduser('/Users/nelsonestrada/projects/podcast_summarizer/workspace_files/')
local_file_path = os.path.join(downloads_folder, 'good_morning_10.mp3')

def transcribe_audio_data(api_key, audio_data):
    openai.api_key = api_key
    transcript = openai.Audio.transcribe("whisper-1", audio_data)
    return transcript["text"]

def transcribe_audio_file(api_key, file_path):
    try:
        print("Loading audio file...")
        audio = AudioSegment.from_file(file_path)
        chunk_length_ms = 1000 * 60 * 1  # 1-minute chunks
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
        transcripts = []

        print(f"Audio file loaded. Transcribing {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks, start=1):
            print(f"Transcribing chunk {i}/{len(chunks)}...")
            with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_audio_file:
                chunk.export(temp_audio_file.name, format="mp3")
                temp_audio_file.seek(0)  # Reset the file pointer to the beginning
                transcript = transcribe_audio_data(api_key, temp_audio_file)
                start_time = i
                end_time = i + 1
                transcripts.append(f"(Timestamp: {start_time}-{end_time} minutes)\n{transcript}")
            print(f"Finished transcribing chunk {i}/{len(chunks)}")
            print(f"Transcription for chunk {i}: {transcript}")  # Print the transcript for the current chunk

        print("Transcription completed.")
        return '\n'.join(transcripts)

    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None

def summarize_transcript(podcast_title, podcast_transcript, prompt_length=2000):
    try:
        print("Summarizing transcript...")

        transcript_chunks = textwrap.wrap(podcast_transcript, prompt_length - 200)  # Split the transcript into smaller chunks
        summaries = []

        for i, chunk in enumerate(transcript_chunks, start=1):
            print(f"Summarizing chunk {i}/{len(transcript_chunks)}...")
            prompt = f"Summarize the transcript from a episode of the podcast \"Mi Mejor Versión con Isa Garcia\". The summary should be in spanish and should include the key points discussed in the episode, along with any important quotes or examples mentioned. Try to keep the summary under 2000 tokens. Here is the transcript: {chunk}"
            response = openai.Completion.create(
                engine="text-davinci-003",  # Replace with "gpt-3.5-turbo" when it is available
                prompt=prompt,
                max_tokens=prompt_length,
                n=1,
                stop=None,
                temperature=0.5,
            )
            summary = response.choices[0].text.strip()
            summaries.append(summary)
            print(f"Finished summarizing chunk {i}/{len(transcript_chunks)}")

        print("Summary completed.")
        return ' '.join(summaries)
    except Exception as e:
        print(f"An error occurred during summarization: {e}")
        return None

def summarize_local_podcast(podcast_title, local_file_path):
    transcript = transcribe_audio_file(openai.api_key, local_file_path)
    if transcript is None:
        return None
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
