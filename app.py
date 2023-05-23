from flask import Flask, request, jsonify
import urllib.request

# Assume we have the transcribe_and_summarize function here
# from transcribe_and_summarize import transcribe_and_summarize

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/summarize', methods=['POST'])
def summarize():
    # Get the podcast URL from the request data
    data = request.get_json()
    podcast_url = data.get('podcast_url')   
    if podcast_url is None:
        return jsonify({'error': 'No podcast URL provided'}), 400

    # Download the podcast
    import requests
    import shutil

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537',
    }

    response = requests.get(podcast_url, headers=headers, stream=True)

    if response.status_code == 200:
        with open('podcast.mp3', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        print("Podcast downloaded")
    else:
        return jsonify({'error': 'Failed to download podcast, status code:' + str(response.status_code)}), 400

    # Call your podcast summarization function here and send the results back to the client
    # ...
    return jsonify({'summary': 'This is a placeholder summary'}), 200

if __name__ == "__main__":
    app.run(debug=True)
