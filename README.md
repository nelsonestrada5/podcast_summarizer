# Podcast Summarizer
WARNING: This is only a work in progress!!! 

Podcast Summarizer is an app that automatically downloads podcast episodes, transcribes them using [Whisper](https://whisper.ai/), and generates summaries using [ChatGPT](https://openai.com/blog/chat-history/).

## Features

- Automatic downloading of podcast episodes from RSS feeds
- Speech-to-text transcription using Whisper
- Text summarization using ChatGPT
- Customizable summary length and language
- Support for multiple podcast platforms and languages

## Getting Started

### Prerequisites

- Python 3.7 or higher
- An OpenAI API key with access to ChatGPT models
- A Whisper API key for speech-to-text transcription
- Podcast RSS feed URLs

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/YOUR_USERNAME/podcast-summarizer.git
   cd podcast-summarizer
   ```

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

3. Set your API keys as environment variables:

   ```
   export OPENAI_API_KEY=YOUR_OPENAI_API_KEY
   export WHISPER_API_KEY=YOUR_WHISPER_API_KEY
   ```

4. Add the RSS feed URLs for the podcasts you want to summarize to `podcasts.txt`:

   ```
   https://example.com/podcast.rss
   https://another.example.com/podcast.rss
   ```

5. Run the app:

   ```
   python main.py
   ```

## Configuration

The app can be configured using environment variables or a `.env` file. Here are the available configuration options:

- `SUMMARY_LENGTH`: The maximum number of words or characters to include in each summary (default: 100 words)
- `SUMMARY_LANGUAGE`: The language to use for the summaries (default: English)
- `PODCAST_FEEDS`: A comma-separated list of RSS feed URLs for the podcasts to summarize (default: `podcasts.txt`)
- `WHISPER_API_KEY`: Your Whisper API key (required)
- `OPENAI_API_KEY`: Your OpenAI API key with access to ChatGPT models (required)

## Contributing

Contributions are welcome! If you have a bug fix, feature request, or other improvement, please submit a pull request or open an issue.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
