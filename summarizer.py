import openai
import os
import requests
from pydub import AudioSegment


openai.api_key = "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"
podcast_title = "Estoy Escribiendo, por Isa Garcia"
downloads_folder = os.path.expanduser('~/Downloads')
local_file_path = os.path.join(downloads_folder, 'estoy_escribiendo_un_libro.m4a')


def transcribe_audio_data(api_key, audio_data):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Content-Type": "application/octet-stream",
        "Authorization": f"Bearer {api_key}",
        model: "whisper-1"
    }
    response = requests.post(url, headers=headers, data=audio_data)
    response.raise_for_status()
    return response.json()['transcript']

def transcribe_audio_file(api_key, file_path):
    print("Loading audio file...")
    audio = AudioSegment.from_file(file_path)
    chunk_length_ms = 1000 * 60 * 5  # 5-minute chunks
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    transcripts = []

    print(f"Audio file loaded. Transcribing {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks, start=1):
        print(f"Transcribing chunk {i}/{len(chunks)}...")
        audio_data = chunk.export(format="mp3")
        transcript = transcribe_audio_data(api_key, audio_data)
        transcripts.append(transcript)
        print(f"Finished transcribing chunk {i}/{len(chunks)}")

    print("Transcription completed.")
    return ' '.join(transcripts)

def summarize_transcript(podcast_title, podcast_transcript, prompt_length=50):
    print("Summarizing transcript...")
    prompt = f"Please provide a summary of the podcast '{podcast_title}'. Here is the transcript: {podcast_transcript}"
    response = openai.Completion.create(
        engine="text-davinci-002", # Replace with "gpt-3.5-turbo" when it is available
        prompt=prompt,
        max_tokens=prompt_length,
        n=1,
        stop=None,
        temperature=0.5,
    )
    summary = response.choices[0].text.strip()
    print("Summary completed.")
    return summary

def summarize_local_podcast(podcast_title, local_file_path):
    transcript = transcribe_audio_file(openai.api_key, local_file_path)
    summary = summarize_transcript(podcast_title, transcript)
    return summary


summary = summarize_local_podcast(podcast_title, local_file_path)
print("\nPodcast summary:", summary)