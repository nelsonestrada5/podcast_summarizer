import spotipy
import spotipy.util as util
import configparser
import requests
import os
import json
from datetime import timedelta

PODCAST_ID = "1Grr7tNmgKPvWwsiA98AqK"
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-library-read'

def main():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    client_id = config.get('spotify', 'client_id')
    client_secret = config.get('spotify', 'client_secret')

    try:
        token = util.prompt_for_user_token(
            username=None,
            scope=SCOPE,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=REDIRECT_URI
        )
    except spotipy.SpotifyException as e:
        print(f"Error obtaining access token: {e}")
        return

    sp = spotipy.Spotify(token)

    try:
        metadata = sp.show(PODCAST_ID)
    except spotipy.SpotifyException as e:
        print(f"Error retrieving metadata: {e}")
        return

    with open("metadata.json", "w") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print("Podcast metadata saved to metadata.json")

    num_episodes = input("How many recent episodes do you want to retrieve? Enter a number or 'all': ")
    try:
        if num_episodes == "all":
            # Retrieve all episodes
            print("Retrieving all episodes...")
            episodes = []
            total = 1
            offset = 0
            while len(episodes) < total:
                results = sp.show_episodes(PODCAST_ID, limit=50, offset=offset)
                total = results['total']
                offset += len(results['items'])
                episodes.extend(results['items'])
        else:
            # Retrieve specified number of episodes
            print(f"Retrieving {num_episodes} episodes...")
            results = sp.show_episodes(PODCAST_ID, limit=num_episodes)
            episodes = results['items']
    except spotipy.SpotifyException as e:
        print(f"Error retrieving episodes: {e}")
        return

    for episode in episodes:
        episode_data = {
            "Release Date": episode["release_date"],
            "Description": episode["description"],
            "Duration": str(timedelta(milliseconds=episode["duration_ms"])).split(".")[0],
            "Podcast URL": episode["external_urls"]["spotify"]
        }
        print(json.dumps({episode["name"]: episode_data}, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main()
