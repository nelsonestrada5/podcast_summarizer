from flask import Flask, request, jsonify
from transcribe_and_summarize import summarize_local_podcast

app = Flask(__name__)

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    podcast_url = data.get('podcast_url')
    test_run = data.get('test_run', False)
    if not podcast_url:
        return jsonify({'error': 'No podcast URL provided'}), 400

    # Download and summarize the podcast
    try:
        result = summarize_local_podcast(podcast_url, test_run)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
