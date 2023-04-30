import spotipy
import spotipy.util as util
import feedparser
import requests

# Get user input for the podcast name
podcast_name = input("Enter the name of the podcast on Spotify: ")

# Get user input for the Spotify API access token
token = input("Enter your Spotify API access token: ")

# Initialize a Spotipy instance with the access token
print("Initializing Spotipy instance...")
sp = spotipy.Spotify(auth=token)

# Search for the podcast on Spotify
print(f"Searching for {podcast_name} on Spotify...")
results = sp.search(q=podcast_name, type='show')

# Extract the RSS feed URL from the first search result
rss_url = results['shows']['items'][0]['external_urls']['rss']
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
