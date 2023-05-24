# Podcast Summarizer
WARNING: This is only a work in progress!!!

Podcast Summarizer is an app that automatically downloads podcast episodes, transcribes them using [Whisper](https://whisper.ai/), and generates summaries using [ChatGPT](https://openai.com/blog/chat-history/).

## Features
- Extract the RSS feed URL based on a podcast name
- Automatic downloading of podcast episodes from RSS feeds
- Speech-to-text transcription using Whisper
- Text summarization using ChatGPT
- Customizable summary length and language
- Support for multiple podcast platforms and languages

# Podcast Summarizer

Podcast Summarizer is a Python script that uses OpenAI's GPT-3.5-turbo model to generate a summary of a given podcast transcript.

## Installation

1. First, clone this repository to your local machine using the following command:
    ```
    git clone https://github.com/nelsonestrada5/podcast_summarizer.git
    ```
2. Move to the cloned directory:
    ```
    cd podcast_summarizer
    ```
3. It is recommended to use a virtual environment. If you have Python `venv` module installed, create a new environment with the command:
    ```
    python3 -m venv env
    ```
   Activate the virtual environment:
   - On Windows:
        ```
        .\env\Scripts\activate
        ```
   - On Unix or MacOS:
        ```
        source env/bin/activate
        ```
4. Install the Python requirements:
    ```
    pip install -r requirements.txt
    ```

## Setup

1. The script uses OpenAI's GPT-3.5-turbo, so you will need an OpenAI API key. Once you have your API key, create a `config.ini` file in the root directory of the project with the following content:
    ```
    [openai]
    api_key = your_openai_api_key
    ```
    Replace `your_openai_api_key` with your actual OpenAI API key.

2. You can modify the script to customize its behavior. For instance, you can modify the podcast URL or the `prompt_length` parameter when calling the `summarize_transcript` function.

## Usage

After setting up, you can run the script using the following command:

    ```
    python podcast_summarizer.py

    ```
The script will print out the summary of the podcast transcript to the console.

## Note

Please make sure you have enough OpenAI API credits, as long requests to the API (like summarizing a long podcast transcript) might consume more credits.

Also note that the quality of the summary can vary depending on the content and complexity of the podcast transcript.

If you encounter any issues or have any improvements, feel free to open an issue or a pull request.


## Contributing

Contributions are welcome! If you have a bug fix, feature request, or other improvement, please submit a pull request or open an issue.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
