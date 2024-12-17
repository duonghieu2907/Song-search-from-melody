import streamlit as st
import streamlit.components.v1 as components

# Title
st.title("🎶 Song Search from Melody 🎶")
st.write("Upload an MP3 file or record your voice to search for a song.")

# Option Selection
option = st.radio("How would you like to proceed?", ("Upload an MP3 File", "Record Your Voice"))

# Option 1: Upload MP3 File
if option == "Upload an MP3 File":
    uploaded_file = st.file_uploader("Choose an MP3 file to upload", type=["mp3"])
    if uploaded_file is not None:
        st.success("File uploaded successfully! 🎧")
        st.audio(uploaded_file, format="audio/mp3", start_time=0)
    else:
        st.info("Please upload an MP3 file.")
        
    # Placeholder for search functionality
    st.markdown("---")
    if st.button("🔍 Search for the Song"):
        st.warning("Search functionality is not implemented yet. Stay tuned! 🚀")

# Option 2: Record Your Voice
elif option == "Record Your Voice":
    st.header("🎤 Voice Recorder")
    st.write("Click **Start Recording** to record your voice and **Stop Recording** to save.")
    
    # Load the HTML + JS recorder component
    with open("recorder_component.html", "r", encoding="utf-8") as f:
        recorder_html = f.read()

    # Display the audio recorder
    components.html(recorder_html, height=150)
    
    # Placeholder for search functionality
    st.markdown("---")
    st.info("After finishing recording your voice, please upload it to the search engine.")


