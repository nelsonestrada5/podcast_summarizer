import openai
import os
import requests
from pydub import AudioSegment
from io import BytesIO
import tempfile
import datetime
import configparser
import textwrap
from summarizer import Summarizer

config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config.get('openai', 'api_key')

podcast_title = "Estoy Escribiendo, por Isa Garcia"
downloads_folder = os.path.expanduser('/Users/nelsonestrada/Downloads/')
local_file_path = os.path.join(downloads_folder, '3_arquetipos.mp3')

def transcribe_audio_data(api_key, audio_data):
    openai.api_key = api_key
    transcript = openai.Audio.transcribe("whisper-1", audio_data)
    return transcript["text"]


def transcribe_audio_file(api_key, file_path):
    print("Loading audio file...")
    audio = AudioSegment.from_file(file_path)
    chunk_length_ms = 1000 * 60 * 5  # 5-minute chunks
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    transcripts = []

    print(f"Audio file loaded. Transcribing {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks, start=1):
        print(f"Transcribing chunk {i}/{len(chunks)}...")
        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_audio_file:
            chunk.export(temp_audio_file.name, format="mp3")
            temp_audio_file.seek(0)  # Reset the file pointer to the beginning
            transcript = transcribe_audio_data(api_key, temp_audio_file)
            transcripts.append(transcript)
        print(f"Finished transcribing chunk {i}/{len(chunks)}")
        print(f"Transcription for chunk {i}: {transcript}")  # Print the transcript for the current chunk

    print("Transcription completed.")
    return ' '.join(transcripts)

# NEW FUNCTION TO SAVE OUTPUT
def write_to_file(file_name, content):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_file_name = f"{os.path.splitext(file_name)[0]}_{timestamp}{os.path.splitext(file_name)[1]}"
    with open(unique_file_name, 'w') as file:
        file.write(content)

def summarize_transcript(podcast_title, podcast_transcript, prompt_length=2000):
    print("Summarizing transcript...")

    transcript_chunks = textwrap.wrap(podcast_transcript, prompt_length - 200)
    important_sentences = []

    bert_model = Summarizer()
    for i, chunk in enumerate(transcript_chunks, start=1):
        print(f"Extracting important sentences from chunk {i}/{len(transcript_chunks)}...")
        important_chunk = bert_model(chunk)  # Extract important sentences from the chunk
        important_sentences.append(important_chunk)
        print(f"Finished extracting important sentences from chunk {i}/{len(transcript_chunks)}")
        print(f"Important sentences for chunk {i}: {important_chunk}")  # Print the important sentences for the current chunk

    important_text = ' '.join(important_sentences)  # Join the important sentences

    # Write the complete podcast transcript to a file
    write_to_file('podcast_transcript.txt', podcast_transcript)

    # Write the important sentences to another file
    write_to_file('important_sentences.txt', important_text)

    # Read the important sentences from the file
    with open('important_sentences.txt', 'r') as file:
        important_text = file.read()

    print("Generating summary based on important sentences...")
    prompt = f"Summarize the transcript from a episode of the podcast \"Mi Mejor Versión con Isa Garcia\". The summary should be in spanish and should include the key points discussed in the episode, along with any important quotes or examples mentioned. Try to keep the summary under 2000 tokens. Here are the important sentences: {important_text}"
    response = openai.Completion.create(
        engine="text-davinci-003",  # Replace with "gpt-3.5-turbo" when it is available
        prompt=prompt,
        max_tokens=prompt_length,
        n=1,
        stop=None,
        temperature=0.5,
    )
    summary = response.choices[0].text.strip()
    print("Summary completed.")
    return summary


def summarize_local_podcast(podcast_title, local_file_path, api_key):
    podcast_transcript = transcribe_audio_file(api_key, local_file_path)
    return summarize_transcript(podcast_title, podcast_transcript)

summary = summarize_local_podcast(podcast_title, local_file_path, openai.api_key)
print("\nPodcast summary:\n", summary)
