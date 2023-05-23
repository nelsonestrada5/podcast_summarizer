import requests
import feedparser
import json
import urllib.parse

# Get user input for the podcast name
podcast_name = input("Enter the name of the podcast on Apple Podcasts: ")

# URL encode the podcast name
podcast_name_encoded = urllib.parse.quote(podcast_name)

# Search for the podcast on Apple Podcasts
print(f"Searching for {podcast_name} on Apple Podcasts...")
search_url = f"https://itunes.apple.com/search?term={podcast_name_encoded}&entity=podcast"
response = requests.get(search_url)
results = response.json()

# Extract the RSS feed URL from the first search result
rss_url = None
for item in results['results']:
    if 'feedUrl' in item:
        rss_url = item['feedUrl']
        break

if rss_url is None:
    print("Could not find an RSS feed URL for this podcast.")
else:
    print(f"RSS feed URL: {rss_url}")

    # Parse the RSS feed using feedparser
    print("Parsing RSS feed...")
    feed = feedparser.parse(rss_url)

    # Check if the RSS feed has any podcast entries
    if len(feed.entries) == 0:
        print("This RSS feed does not have any podcast entries.")
    else:
        # Extract the desired information from the RSS feed entries
        podcasts = []
        for entry in feed.entries:
            podcast = {
                "title": entry.title,
                "date": entry.published,
                "link": entry.link,
                "duration": entry.itunes_duration
            }
            podcasts.append(podcast)

        # Print the list of podcasts as a JSON object
        print(json.dumps(podcasts, indent=4))
