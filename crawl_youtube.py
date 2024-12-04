import yt_dlp

# YouTube video URL
url = "https://www.youtube.com/watch?v=GZ4vaTRn0HU"

# Options for downloading and converting audio
ydl_opts = {
    'format': 'bestaudio/best',  # Download the best available audio format
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',  # Use FFmpeg to extract audio
            'preferredcodec': 'mp3',      # Convert to MP3
            'preferredquality': '192',    # Set audio quality to 192kbps
        }
    ],
    'outtmpl': '%(title)s.%(ext)s',  # Set output filename as video title
    'noplaylist': True,              # Ensure only a single video is processed
    'quiet': False,                  # Show progress
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Audio extracted and saved successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
