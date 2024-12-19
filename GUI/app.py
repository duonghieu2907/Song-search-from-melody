import streamlit as st
import re

# Function to extract the video ID and generate thumbnail URL
def get_youtube_thumbnail(youtube_link):
    try:
        # Extract video ID using regex
        video_id = re.search(r"v=([a-zA-Z0-9_-]+)", youtube_link).group(1)
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        return thumbnail_url
    except Exception as e:
        return None

# Placeholder YouTube link and title
YOUTUBE_LINK = "https://www.youtube.com/watch?v=BgUFNi5MvzE"
SONG_TITLE = "Nơi Pháo Hoa Rực Rỡ (Đi Để Trở Về 8) - Orange x Hoàng Dũng"

# Title
st.set_page_config(page_title="Song Search from Melody", page_icon="🎶")
st.title("🎶 Song Search from Melody 🎶")
st.write("Upload an MP3 file or record your voice to search for a song.")

# Option Selection
option = st.radio("How would you like to proceed?", ("Upload an MP3 File", "Record Your Voice"))

# Initialize Uploaded File Variable
uploaded_file = None

# Option 1: Upload MP3 File
if option == "Upload an MP3 File":
    uploaded_file = st.file_uploader("Choose an MP3 or WAV file", type=["mp3", "wav"])
    if uploaded_file:
        st.success("File uploaded successfully! 🎧")
        st.audio(uploaded_file, format="audio/mp3", start_time=0)

# Option 2: Record Your Voice
elif option == "Record Your Voice":
    st.header("🎤 Voice Recorder")
    st.write("Click the **Record** button to start recording. Tap again to stop. Your file will download automatically.")

    # Load the HTML + JS recorder component
    with open("recorder_component.html", "r", encoding="utf-8") as f:
        recorder_html = f.read()

    st.components.v1.html(recorder_html, height=200)

    # File Uploader for Recording
    uploaded_file = st.file_uploader("Upload the recorded .wav file", type=["wav"])

    if uploaded_file:
        st.success("Recorded file uploaded successfully! 🎧")
        st.audio(uploaded_file, format="audio/wav", start_time=0)

# Search Functionality
st.markdown("---")
if st.button("🔍 Search for the Song"):
    if uploaded_file is None:
        st.warning("Please upload a file before searching for a song!")
    else:
        st.info("The matching song is:")
        
        # Generate thumbnail URL
        thumbnail_url = get_youtube_thumbnail(YOUTUBE_LINK)
        
        # Display clickable title and thumbnail
        st.markdown(f"### [🎵 {SONG_TITLE}]({YOUTUBE_LINK})")
        if thumbnail_url:
            st.image(thumbnail_url, caption=SONG_TITLE, use_container_width=True)
        st.markdown(f"[Watch on YouTube]({YOUTUBE_LINK})")