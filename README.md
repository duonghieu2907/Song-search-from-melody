# Song Search From Melody

## Overview
**Song Search From Melody** is an audio-based search system that allows users to find songs based on short audio snippets. The system processes and indexes audio files using the **CLAP model** for feature extraction and **Milvus** for vector storage and similarity search. Users can search for songs by uploading an audio query, and the system will return the most similar matches from the indexed dataset.

## Features
- **Streamlit-based Frontend**: Provides an intuitive UI for users to upload and search songs.
- **CLAP Model for Audio Embeddings**: Extracts meaningful representations from audio files.
- **Milvus Vector Database**: Stores and retrieves similar audio embeddings efficiently.
- **YouTube Audio Crawling**: Collects audio data from YouTube videos for indexing.
- **Chunk-Based Audio Processing**: Splits audio files into 10-second segments for improved feature extraction.
- **Fast Approximate Nearest Neighbor (ANN) Search**: Enables efficient similarity matching.

## Technologies Used
- **Python**
- **Streamlit** (Frontend UI)
- **laion_clap** (Audio embedding model)
- **pymilvus** (Vector database management)
- **pydub** (Audio file processing)
- **NumPy** (Data processing)
- **Pathlib & OS** (File management)

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/song-search-from-melody.git
   cd song-search-from-melody
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure **Milvus** is installed and running locally or on a remote server.

## Usage
### 1. Indexing Audio Data
Before performing searches, you must process and index audio files:
```bash
python main.py
```
This will:
- Extract audio embeddings using CLAP
- Store the embeddings in a Milvus collection

### 2. Searching for Similar Songs
Run the Streamlit app to perform searches via UI:
```bash
streamlit run app.py
```
Upload an audio file to find similar songs in the indexed database.

## How It Works
### Audio Processing & Indexing
1. Audio files are **split into 10-second chunks**.
2. Each chunk is **encoded into a feature vector** using CLAP.
3. The **average embedding of all chunks** is computed.
4. The resulting vector is **normalized and stored in Milvus**.

### Searching for Songs
1. The user uploads a **query audio file**.
2. The query audio is **processed into an embedding**.
3. The embedding is used to **search for similar songs in Milvus**.
4. The top **matching results are returned**.

## Crawling Audio from YouTube
The system can **extract audio** from YouTube videos:
- Download YouTube videos.
- Extract audio and convert it to WAV.
- Process and index audio for search.

## Future Improvements
- **Enhance YouTube audio crawling** with automatic dataset updates.
- **Optimize Milvus storage** for large-scale datasets.
- **Improve UI** for better user experience.
- **Implement real-time music recognition**.

## Contributing
We welcome contributions! Feel free to submit **issues** or **pull requests**.

## License
This project is licensed under the MIT License. See `LICENSE` for details.
