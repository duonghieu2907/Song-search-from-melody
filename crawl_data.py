import googleapiclient.discovery
import time
import json
import yt_dlp
import os

# Global variables
LIMIT = 10  # Common limit for videos per playlist or total
MAX_RESULTS_PER_REQUEST = 10  # Max results per API request

# Your API key from Google Cloud Console
API_KEY = 'AIzaSyBpa1uprQ9PLW_7ASmEyC-lOPKJT1zYBiE'

# Initialize the YouTube API client
def youtube_api_client():
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)
    return youtube

# Search for playlists based on a query
def search_playlists(youtube, query, max_results=MAX_RESULTS_PER_REQUEST):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="playlist",  # Search specifically for playlists
        maxResults=max_results
    )
    response = request.execute()
    return response

# Get video IDs from a playlist
def get_playlist_videos(youtube, playlist_id, max_results=MAX_RESULTS_PER_REQUEST):
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
def get_video_data(youtube, video_id):
    try:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()

        if not response['items']:
            print(f"Warning: Video ID {video_id} not found.")
            return None

        video = response['items'][0]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        title = video['snippet']['title']

        return {
            "title": title,
            "video_url": video_url
        }

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
                'preferredcodec': 'mp3',      # Convert to MP3
                'preferredquality': '192',    # Set audio quality to 192kbps
            }],
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

# Function to fetch playlist songs, download audio, and save info to JSON
def fetch_playlist_songs_and_download_audio(query="classic hits USUK OR classic Vietnamese songs", max_results=MAX_RESULTS_PER_REQUEST, total_results=LIMIT, download_path='./songs', json_output='./songs_info.json'):
    youtube = youtube_api_client()
    songs_info = []  # List to hold information about each song

    # Create directory for saving data if it doesn't exist
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Step 1: Search playlists
    playlist_queries = [
        "classic hits USUK",  # USUK classic hits
        "Những bài hát đình đám",  # Vietnamese classic hits
        "popular songs USUK",  # Additional query to increase diversity
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
                video_data = get_video_data(youtube, video_id)
                if video_data:
                    title = video_data["title"]
                    video_url = video_data["video_url"]
                    songs_info.append(video_data)

                    # Step 4: Download audio
                    download_audio_from_youtube(video_url, download_path)
                    total_videos_fetched += 1

                    # If we've reached the total number of results we want, stop
                    if total_videos_fetched >= total_results:
                        break

            # If we've reached the desired number of results, exit
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
fetch_playlist_songs_and_download_audio(query="classic hits USUK", max_results=MAX_RESULTS_PER_REQUEST, total_results=LIMIT, download_path='./songs', json_output='./songs_info.json')