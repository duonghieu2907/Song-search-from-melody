import os
import numpy as np
from pymilvus import MilvusClient
from pathlib import Path
from typing import List
import laion_clap
from pydub import AudioSegment
from pydub.utils import make_chunks


# Lớp xử lý CLAP model
class CLAP:
    def __init__(self):
        self.model = laion_clap.CLAP_Module(enable_fusion=False)
        self._load_model()

    def _load_model(self):
        self.model.load_ckpt()

    def encode_audios(self, audios: List[str]):
        return self.model.get_audio_embedding_from_filelist(x=audios, use_tensor=False)


# Lớp quản lý Milvus
class MilvusManager:
    def __init__(self, db_path: str, collection_name: str, dimension: int = 512):
        self.client = MilvusClient(db_path)
        self.collection_name = collection_name
        self.dimension = dimension

    def create_collection(self, metric_type: str = "IP"):
        """Tạo collection nếu chưa tồn tại."""
        self.client.create_collection(
            collection_name=self.collection_name,
            dimension=self.dimension,
            metric_type=metric_type,
            auto_id=True,
        )
        print(f"Collection '{self.collection_name}' created with dimension {self.dimension}.")

    def insert_vectors(self, vector_data: List[dict]):
        """Chèn dữ liệu vector vào collection."""
        if not vector_data:
            print("No data to insert.")
            return
        self.client.insert(collection_name=self.collection_name, data=vector_data)
        print(f"Inserted {len(vector_data)} vectors into the collection '{self.collection_name}'.")

    def search_vectors(self, query_vector: np.ndarray, top_k: int):
        """Tìm kiếm các vector tương tự."""
        if query_vector.ndim != 1:
            raise ValueError("Query vector must be 1-dimensional.")

        query_vector_normalized = query_vector / np.linalg.norm(query_vector, keepdims=True)
        res = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector_normalized.tolist()],
            limit=top_k,
            output_fields=["audio_name"],
        )

        results = []
        for result in res:
            for match in result:
                audio_name = match["entity"].get("audio_name", "Unknown")
                distance = match.get("distance", "N/A")
                results.append((audio_name, distance))
        return results


# Hàm xử lý các file audio
def process_audio_files(input_dir: str, output_dir: str, clap_model: CLAP):
    # Tạo thư mục output nếu chưa tồn tại
    os.makedirs(output_dir, exist_ok=True)

    # Lấy danh sách tất cả các file .wav trong thư mục input
    audio_files = [str(file) for file in Path(input_dir).rglob("*.wav")]

    if not audio_files:
        print("No audio files found in the input directory.")
        return

    for audio_file in audio_files:
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_file)

            # Chia nhỏ audio thành các đoạn 10 giây
            chunk_length_ms = 10 * 1000  # 10 giây
            chunks = make_chunks(audio, chunk_length_ms)

            embeddings = []
            for i, chunk in enumerate(chunks):
                # Lưu chunk tạm thời để xử lý với CLAP
                temp_chunk_path = os.path.join(output_dir, f"{Path(audio_file).stem}_chunk{i}.wav")
                chunk.export(temp_chunk_path, format="wav")

                # Vectorize đoạn audio
                chunk_embedding = clap_model.encode_audios([temp_chunk_path])
                embeddings.append(chunk_embedding)

                # Xóa file tạm
                os.remove(temp_chunk_path)

            if not embeddings:
                print(f"No embeddings generated for file {audio_file}. Skipping.")
                continue

            # Tính mean vector của tất cả các đoạn
            embeddings = np.vstack(embeddings)  # Chuyển list thành mảng numpy
            mean_embedding = np.mean(embeddings, axis=0)

            # Normalize mean embedding
            normalized_embedding = mean_embedding / np.linalg.norm(mean_embedding, keepdims=True)

            # Tên file output .npy
            output_file = os.path.join(output_dir, Path(audio_file).stem + ".npy")

            # Lưu vector hóa
            np.save(output_file, normalized_embedding)

            print(f"Processed and saved: {output_file}")
        except Exception as e:
            print(f"Error processing file {audio_file}: {e}")


# Hàm tìm kiếm file audio tương tự
def search_similar_audio(query_file: str, clap_model: CLAP, milvus_manager: MilvusManager, top_k: int):
    audio = AudioSegment.from_file(query_file)

    # Chia nhỏ query audio thành các đoạn 10 giây
    chunk_length_ms = 10 * 1000  # 10 giây
    chunks = make_chunks(audio, chunk_length_ms)

    embeddings = []
    for i, chunk in enumerate(chunks):
        temp_chunk_path = f"temp_chunk_{i}.wav"
        chunk.export(temp_chunk_path, format="wav")

        # Vectorize đoạn audio
        chunk_embedding = clap_model.encode_audios([temp_chunk_path])
        embeddings.append(chunk_embedding)

        # Xóa file tạm
        os.remove(temp_chunk_path)

    if not embeddings:
        print("No embeddings generated for the query file. Exiting.")
        return

    # Tính mean vector cho query audio
    embeddings = np.vstack(embeddings)  # Chuyển list thành mảng numpy
    mean_embedding = np.mean(embeddings, axis=0)

    # Tìm kiếm trong Milvus
    results = milvus_manager.search_vectors(mean_embedding, top_k)
    print(f"Top {top_k} similar audio files:")
    for audio_name, distance in results:
        print(f"Audio Name: {audio_name}, Distance: {distance}")


if __name__ == "__main__":
    # Các tham số
    input_directory = "./songs"
    output_directory = "./output"
    database_path = "./milvus_demo.db"
    collection_name = "audio_collection"

    # Khởi tạo
    clap_model = CLAP()
    milvus_manager = MilvusManager(db_path=database_path, collection_name=collection_name)

    # Bước 1: Xử lý các file audio và lưu vector hóa
    process_audio_files(input_directory, output_directory, clap_model)

    # Bước 2: Tạo cơ sở dữ liệu Milvus
    milvus_manager.create_collection()

    # Chèn dữ liệu vào Milvus
    vector_files = [str(file) for file in Path(output_directory).rglob("*.npy")]
    vector_data = [
        {
            "vector": np.load(file).tolist(),
            "audio_name": Path(file).stem,
        }
        for file in vector_files
    ]
    milvus_manager.insert_vectors(vector_data)

    # Bước 3: Tìm kiếm file audio tương tự
    query_audio = "./query.wav"  # File audio query
    search_similar_audio(query_audio, clap_model, milvus_manager, top_k=5)