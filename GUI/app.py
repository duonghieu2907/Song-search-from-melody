import sys
import os
import subprocess
import json
import re
from io import BytesIO
from pydub import AudioSegment
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from index_search import MilvusManager, CLAP, search_similar_audio

# Function to load data from a JSON file
def load_video_data():
    # Load the JSON data from the file
    with open('../songs_info.json', 'r', encoding='utf-8') as file:
        video_data = json.load(file)
    return video_data

# Function to reprocess WAV file using ffmpeg
def reprocess_wav_with_ffmpeg(input_wav):
    temp_input_path = "temp_input.wav"
    temp_output_path = "temp_output.wav"

    # Save input BytesIO as temporary file
    with open(temp_input_path, "wb") as temp_input_file:
        temp_input_file.write(input_wav.read())

    # Execute ffmpeg command
    ffmpeg_command = [
        "ffmpeg", "-y",  # Overwrite output without asking
        "-i", temp_input_path,  # Input file
        "-acodec", "pcm_s16le",  # Convert to PCM 16-bit
        temp_output_path  # Output file
    ]

    try:
        subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Error occurred while running ffmpeg: {e.stderr.decode()}")
        return None

    # Load the reprocessed file into BytesIO
    with open(temp_output_path, "rb") as temp_output_file:
        processed_wav = BytesIO(temp_output_file.read())

    # Clean up temporary files
    os.remove(temp_input_path)
    os.remove(temp_output_path)

    return processed_wav

# Function to convert MP3 to WAV
def convert_mp3_to_wav(mp3_file):
    mp3_audio = AudioSegment.from_file(mp3_file, format="mp3")
    wav_buffer = BytesIO()
    mp3_audio.export(wav_buffer, format="wav")
    wav_buffer.seek(0)
    return wav_buffer

# Title
st.set_page_config(page_title="Song Search from Melody", page_icon="🎶")
st.title("🎶 Song Search from Melody 🎶")
st.write("Upload an MP3 file or record your voice to search for a song.")

# Option Selection
option = st.radio("How would you like to proceed?", ("Upload an MP3 File", "Record Your Voice"))

# Initialize
@st.cache_resource
def initialize():
    video_data = load_video_data()
    database_path = "../milvus_demo.db"
    collection_name = "audio_collection"
    clap_model = CLAP()
    milvus_manager = MilvusManager(db_path=database_path, collection_name=collection_name)
    return video_data, clap_model, milvus_manager

uploaded_file = None
video_data, clap_model, milvus_manager = initialize()

# Option 1: Upload MP3 File
if option == "Upload an MP3 File":
    uploaded_file = st.file_uploader("Choose an MP3 or WAV file", type=["mp3", "wav"])
    if uploaded_file:
        if uploaded_file.type == "audio/mpeg":  # Check if the uploaded file is an MP3
            st.info("Converting MP3 to WAV...")
            converted_wav = convert_mp3_to_wav(uploaded_file)
            st.success("File converted to WAV format successfully! 🎧")
            st.audio(converted_wav, format="audio/wav", start_time=0)
            processed_wav = reprocess_wav_with_ffmpeg(converted_wav)
        else:
            st.success("WAV file uploaded successfully! 🎧")
            st.audio(uploaded_file, format="audio/wav", start_time=0)
            processed_wav = reprocess_wav_with_ffmpeg(uploaded_file)

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
        processed_wav = reprocess_wav_with_ffmpeg(uploaded_file)

# Search Functionality
st.markdown("---")
if st.button("🔍 Search for the Song"):
    if uploaded_file is None or processed_wav is None:
        st.warning("Please upload a file before searching for a song!")
    else:
        # Perform the search
        results = search_similar_audio(query_file=processed_wav, clap_model=clap_model, milvus_manager=milvus_manager, top_k=10)

        # Display results
        for song_title, similarity in results:
            # Find corresponding YouTube link in video_data
            youtube_link = None
            for video in video_data:
                if video['title'] == song_title:
                    youtube_link = video['video_url']
                    thumbnail_url = video['thumbnail_url']
                    break

            if youtube_link:
                # Display song name, thumbnail, and YouTube link
                st.markdown(f"### [🎵 {song_title}]({youtube_link})")
                st.image(thumbnail_url, caption=song_title, use_container_width=True)
            else:
                st.markdown(f"### 🎵 {song_title}")
                st.warning("Due to our limited data in the JSON file, no video link is available for this song.")