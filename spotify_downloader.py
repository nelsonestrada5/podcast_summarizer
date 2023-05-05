import spotipy
import spotipy.util as util
import feedparser
import requests
import configparser
import os

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
print(f"Podcast metadata: {metadata}")

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
    print(f"Episode name: {episode['name']}")
    print(f"Release date: {episode['release_date']}")
    print(f"Description: {episode['description']}")
    print()  # add blank line between episodes

# Commented out original code
'''
# Get user input for the podcast name
podcast_name = input("Enter the name of the podcast on Spotify: ")


# Search for the podcast on Spotify
print(f"Searching for {podcast_name} on Spotify...")
results = sp.search(q=podcast_name, type='show')

# Extract the RSS feed URL from the first search result
rss_url = None
for item in results['shows']['items']:
    if 'rss' in item['external_urls']:
        rss_url = item['external_urls']['rss']
        break

if rss_url is None:
    print("Could not find an RSS feed URL for this podcast.")
else:
    print(f"RSS feed URL: {rss_url}")

    # Parse the RSS feed using feedparser
    print("Parsing RSS feed...")
    feed = feedparser.parse(rss_url)

    # Download the first podcast from the RSS feed
    podcast_url = feed.entries[0]['enclosures'][0]['url']
    print(f"Downloading first podcast from {podcast_url}...")
    response = requests.get(podcast_url)

    # Save the podcast to a file
    filename = feed.entries[0]['title'] + ".mp3"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Podcast saved to {filename}!")
'''
