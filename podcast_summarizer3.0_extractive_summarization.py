import openai
import os
import requests
from pydub import AudioSegment
from io import BytesIO
import tempfile
import configparser
import textwrap
from summarizer import Summarizer

config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config.get('openai', 'api_key')

podcast_title = "Estoy Escribiendo, por Isa Garcia"
downloads_folder = os.path.expanduser('/Users/nelsonestrada/Downloads/')
local_file_path = os.path.join(downloads_folder, '3_arquetipos.mp3')

# The rest of the code remains the same until the summarize_transcript function

def extract_important_sentences(text, num_sentences=3):
    model = Summarizer()
    summary = model(text, num_sentences=num_sentences)
    return ' '.join(summary)

def summarize_transcript(podcast_title, podcast_transcript, prompt_length=2000):
    print("Summarizing transcript...")

    transcript_chunks = textwrap.wrap(podcast_transcript, prompt_length - 200)
    important_sentences = []

    for i, chunk in enumerate(transcript_chunks, start=1):
        print(f"Extracting important sentences from chunk {i}/{len(transcript_chunks)}...")
        important_chunk = extract_important_sentences(chunk, num_sentences=3)  # Extract important sentences from the chunk
        important_sentences.append(important_chunk)
        print(f"Finished extracting important sentences from chunk {i}/{len(transcript_chunks)}")

    important_text = ' '.join(important_sentences)  # Join the important sentences

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

# The rest of the code remains the same

summary = summarize_local_podcast(podcast_title, local_file_path)
print("\nPodcast summary:\n", summary)
