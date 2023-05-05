import spotipy
import spotipy.util as util
import configparser
import requests
import os
import json
from datetime import timedelta


# Set the podcast ID for the show you want to query
PODCAST_ID = "1Grr7tNmgKPvWwsiA98AqK"

# Read the Spotify API credentials from the config.ini file
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
client_id = config.get('spotify', 'client_id')
client_secret = config.get('spotify', 'client_secret')
redirect_uri = 'http://localhost:8888/callback'
scope = 'user-library-read'

# Obtain an access token using the OAuth2 authorization flow
print("Obtaining Spotify API access token...")
token = util.prompt_for_user_token(
    username=None,
    scope=scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri
)

# Initialize a Spotipy instance with the access token
print("Initializing Spotipy instance...")
sp = spotipy.Spotify(token)

# Get metadata for the podcast
print(f"Getting metadata for podcast {PODCAST_ID}...")
metadata = sp.show(PODCAST_ID)
metadata_file = 'podcast_metadata.json'
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

# Get the number of recent episodes to retrieve
num_episodes = input("How many recent episodes do you want to retrieve? Enter a number or 'all': ")
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

# Print information for each episode
for episode in episodes:
    episode_info = {
        'Episode name': episode['name'],
        'Release Date': episode['release_date'],
        'Description': episode['description'],
        'Duration': str(timedelta(milliseconds=episode['duration_ms'])),
        'Podcast URL': episode['external_urls']['spotify']
    }
    print(json.dumps(episode_info, indent=2))
