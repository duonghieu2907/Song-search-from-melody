from datetime import timedelta
import googleapiclient.discovery
import time
import json
import requests
import yt_dlp
import os

# Global variables
LIMIT = 300  # Common limit for videos per playlist or total
MAX_RESULTS_PER_REQUEST = 50  # Max results per API request

# Your API key from Google Cloud Console
API_KEY = 'AIzaSyBpa1uprQ9PLW_7ASmEyC-lOPKJT1zYBiE'

DOWNLOADED_IDS_FILE = './downloaded_video_ids.json'

# Load existing video IDs from file
def load_downloaded_ids(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

# Save video IDs to file
def save_downloaded_ids(file_path, downloaded_ids):
    with open(file_path, 'w') as f:
        json.dump(downloaded_ids, f, indent=4)


def get_video_durations(youtube, video_ids):
    durations = {}
    for video_id in video_ids:
        try:
            response = youtube.videos().list(
                part="snippet,contentDetails",  # Request contentDetails
                id=video_id
            ).execute()

            # Ensure response contains items
            if 'items' in response and response['items']:
                video = response['items'][0]

                # Ensure contentDetails and duration exist
                if 'contentDetails' in video and 'duration' in video['contentDetails']:
                    duration = iso8601_duration_to_seconds(video['contentDetails']['duration'])
                    durations[video_id] = duration
                    print(f"Duration for video ID {video_id}: {duration} seconds")
                else:
                    print(f"contentDetails or duration missing for video ID {video_id}")
                    durations[video_id] = None
            else:
                print(f"No data found for video ID {video_id}")
                durations[video_id] = None

        except Exception as e:
            print(f"Error retrieving data for video ID {video_id}: {e}")
            durations[video_id] = None

    return durations



def iso8601_duration_to_seconds(duration):
    try:
        parsed_duration = timedelta()
        is_parsing = False
        value = ''
        for char in duration:
            if char.isdigit():
                value += char
                is_parsing = True
            elif is_parsing:
                is_parsing = False
                if char == 'H':
                    parsed_duration += timedelta(hours=int(value))
                elif char == 'M':
                    parsed_duration += timedelta(minutes=int(value))
                elif char == 'S':
                    parsed_duration += timedelta(seconds=int(value))
                value = ''
        return parsed_duration.total_seconds()
    except Exception as e:
        print(f"Error parsing duration {duration}: {str(e)}")
        return None


# Initialize the YouTube API client
def youtube_api_client():
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)
    return youtube


# Search for playlists based on a query
def search_playlists(youtube, query, max_results = MAX_RESULTS_PER_REQUEST):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="playlist",  # Search specifically for playlists
        maxResults=max_results
    )
    response = request.execute()
    return response


# Get video IDs from a playlist
def get_playlist_videos(youtube, playlist_id, max_results = MAX_RESULTS_PER_REQUEST):
    videos = []
    next_page_token = None

    while len(videos) < LIMIT:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=max_results,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            videos.append(video_id)
            if len(videos) >= LIMIT:
                break

        next_page_token = response.get('nextPageToken', None)
        if not next_page_token or len(videos) >= LIMIT:
            break

        time.sleep(1)  # Avoid hitting rate limits

    return videos

# Get video details (title, official song URL) for a video ID
def get_video_data(youtube, video_id, max_duration = 6*60):
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails",
            id=video_id
        )
        response = request.execute()

        if not response['items']:
            print(f"Warning: Video ID {video_id} not found.")
            return None

        video = response['items'][0]        
        if 'contentDetails' in video and 'duration' in video['contentDetails']:
            duration = iso8601_duration_to_seconds(video['contentDetails']['duration'])
            if duration > max_duration:  # 6 minutes in seconds
                print(f"Video ID {video_id} is longer than {max_duration / 60} minutes. Skipping download.")
                return None

            video_url = f"https://www.youtube.com/watch?v={video_id}"
            title = video['snippet']['title']
            thumbnail_url = video['snippet']['thumbnails']['high']['url']

            return {
                "title": title,
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
            }
        else:
            print(f"contentDetails or duration missing for video ID {video_id}")
            return None
        
    except Exception as e:
        print(f"Error retrieving data for video ID {video_id}: {str(e)}")
        return None

# Function to download audio from YouTube URL using yt-dlp
def download_audio_from_youtube(video_url, download_path='./'):
    try:
        # Define yt-dlp options for downloading and converting audio
        ydl_opts = {
            'format': 'bestaudio/best',  # Best audio quality
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',  # Use FFmpeg to extract audio
                'preferredcodec': 'wav',      # Convert to MP3
                'preferredquality': '192',    # Set audio quality to 192kbps
            }],
            'ffmpeg_location': r"D:\ffmpeg-2024-12-04-git-2f95bc3cb3-essentials_build\ffmpeg-2024-12-04-git-2f95bc3cb3-essentials_build\bin\ffmpeg.exe",
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),  # Save in the specified folder
            'noplaylist': True,  # Ensure we're downloading only one video
            'quiet': False,      # Show progress
        }

        # Download and convert the audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        print(f"Audio extracted and saved successfully for: {video_url}")

    except Exception as e:
        print(f"Error downloading audio for {video_url}: {str(e)}")
        return None  # Audio download failed


def save_thumbnail(thumbnail_url, save_path, file_name):
    try:
        response = requests.get(thumbnail_url, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(save_path, f"{file_name}.jpg")
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Thumbnail saved: {file_path}")
        else:
            print(f"Failed to download thumbnail: {thumbnail_url}")
    except Exception as e:
        print(f"Error saving thumbnail {thumbnail_url}: {str(e)}")


# Function to fetch playlist songs, download audio, and save info to JSON
def fetch_playlist_songs_and_download_audio(max_results=MAX_RESULTS_PER_REQUEST, total_results=LIMIT, download_path='./songs', json_output='./songs_info.json'):
    youtube = youtube_api_client()
    songs_info = []  # List to hold information about each song

    downloaded_ids = set(load_downloaded_ids(DOWNLOADED_IDS_FILE))


    # Create directory for saving data if it doesn't exist
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Step 1: Search playlists
    playlist_queries = [
        "Best US-UK Songs Released in 2024",
        "Adele's Top Songs",
        "Top Hits by Taylor Swift",
        "Billboard Hot 100",
        "Spotify Playlist 2024"
    ]
    
    # Step 2: Fetch playlists and videos from each query
    total_videos_fetched = 0  # To keep track of how many videos we've processed
    
    for query in playlist_queries:
        playlist_response = search_playlists(youtube, query, max_results=max_results)
        for playlist in playlist_response['items']:
            playlist_title = playlist['snippet']['title']
            playlist_id = playlist['id']['playlistId']

            # Step 3: Get video data from playlist
            video_ids = get_playlist_videos(youtube, playlist_id, max_results=max_results)
            for video_id in video_ids:
                if video_id in downloaded_ids:
                    print(f"Skipping duplicate video ID: {video_id}")
                    continue

                video_data = get_video_data(youtube, video_id)
                if video_data:
                    title = video_data["title"]
                    video_url = video_data["video_url"]
                    songs_info.append(video_data)

                    thumbnail_file_name = video_data["title"].replace("/", "-")  # Replace invalid filename characters
                    save_thumbnail(video_data["thumbnail_url"], './thumbnails', thumbnail_file_name)

                    # Step 4: Download audio
                    download_audio_from_youtube(video_url, download_path)
                    total_videos_fetched += 1

                    # If we've reached the total number of results we want, stop
                    if total_videos_fetched >= total_results:
                        break

            # If we've reached the desired number of results, exit
            if total_videos_fetched >= total_results:
                break

    # Save song info to JSON
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(songs_info, f, ensure_ascii=False, indent=4)

    print(f"Downloaded {len(songs_info)} songs. Information saved to {json_output}")

# Example usage
fetch_playlist_songs_and_download_audio(max_results=MAX_RESULTS_PER_REQUEST, total_results=LIMIT, download_path='./songs', json_output='./songs_info.json')