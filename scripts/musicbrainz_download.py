import pandas as pd
import musicbrainzngs
from sqlalchemy import create_engine
from time import sleep
import os
import sys
from urllib.parse import quote_plus
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import re
from datetime import datetime

musicbrainzngs.set_useragent("Music-Streaming-Analysis", "0.1", "joykissell@gmail.com")
encoded_password = quote_plus(config.DB_PASSWORD)
engine = create_engine(
    f"postgresql://{config.DB_USER}:{encoded_password}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    )

#only looking at main/first artist for features
def clean_artist(artists:str)-> str:
    lower = artists.lower()
    if "feat" in lower or "featuring" in lower or "ft." in lower or "with" in lower:
            artists = re.split(r"\s+(feat\.?|featuring|ft.|with)\s+", artists,
                               flags = re.IGNORECASE)[0].strip()
    return artists

#only fetching type of earliest release of song
def earliest_release(song_title:str, artist:str, first_week):
    try:
        result = musicbrainzngs.search_recordings(
                recording = song_title,
                artist = artist,
                limit = 20
        )
        releases = []
        # Define what we want to keep
        allowed_types = {"Single", "EP", "Album"}
        # Define priority for sorting
        priority = {"Single": 1, "EP": 2, "Album": 3}
        
        for rec in result["recording-list"]:
             # title match check
             recording_title = rec.get("title", "").lower()
             search_title = song_title.lower()
             
             # Skip if titles aren't close enough
             if recording_title != search_title:
                 continue
             
             for rel in rec.get("release-list", []):
                  release_date = rel.get("date")
                  release_group = rel.get("release-group", {})
                  release_type = ",".join(release_group.get("type-list", [])) or release_group.get("type")
                  
                  # Skip if not in our allowed types
                  if not release_type or release_type not in allowed_types:
                      continue
                  
                  if release_date:
                       try:
                            date_obj = datetime.strptime(release_date, "%Y-%m-%d")
                       except:
                            try:
                                 date_obj = datetime.strptime(release_date, "%Y-%m")
                            except:
                                 try:
                                      date_obj = datetime.strptime(release_date, "%Y")
                                 except:
                                      continue
                       # Only include releases that came out before or on the first Billboard week
                       if date_obj.date() <= first_week:
                           releases.append((date_obj, rel["title"], release_type, rel["id"]))
        
        if releases:
             # Sort by priority first, then by date
             releases.sort(key=lambda x: (priority.get(x[2], 10), x[0]))
             return releases[0]
        else:
             return None         
    except Exception as e:
         print(f"error searching {song_title} by {artist}: {e}")
         return None

#pulling from billboard_songs table to query musicbrainz
df_billboard = pd.read_sql("SELECT id, song_title, artist, first_week FROM billboard_songs;", engine)
rows = [] 

for index, row in df_billboard.iterrows():
    song_title = row['song_title']
    artist = row['artist']
    bb_id = row['id']
    first_week = row['first_week']  # Get the first_week from the query
    
    clean_artist_name = clean_artist(artist)
    print(f"Processing: {song_title} by {artist} (first charted: {first_week})")
    
    release_info = earliest_release(song_title, clean_artist_name, first_week)  # Pass first_week
    
    if release_info:
        release_date, release_name, release_type, mbid = release_info
        rows.append({
            'bb_id': bb_id,
            'mbid': mbid,
            'release_name': release_name,
            'release_type': release_type,
            'release_date': release_date.date()
        })
        print(f"Found: {release_name} ({release_date.year}) - {release_type}")
    else:
        print(f"No MusicBrainz data found for {song_title} by {artist}")
    
    sleep(1)
    
    if len(rows) >= 50:
        pd.DataFrame(rows).to_sql('musicbrainz', engine, if_exists='append', index=False)
        print(f"Inserted batch of {len(rows)} records")
        rows = []

# Insert any remaining rows
if rows:
    pd.DataFrame(rows).to_sql('musicbrainz', engine, if_exists='append', index=False)
    print(f"Inserted final batch of {len(rows)} records")

print("Processing complete!")