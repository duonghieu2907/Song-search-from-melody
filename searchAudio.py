import librosa
import numpy as np
import os
from scipy.spatial.distance import euclidean

# Đọc dữ liệu đã lưu
features = np.load("audio_features_segments.npy", allow_pickle=True).item()

# Đoạn âm thanh người dùng nhập vào (input)
def extract_mfcc_from_input(input_audio_path, segment_duration=4):
    # Load file âm thanh (librosa hỗ trợ .mp3 nếu ffmpeg được cài đặt)
    y, sr = librosa.load(input_audio_path, sr=None)
    
    # Tính số mẫu cho mỗi đoạn 4 giây
    segment_samples = segment_duration * sr
    
    # Danh sách chứa MFCC cho từng đoạn
    input_mfcc = []
    
    # Chia bài hát thành các đoạn nhỏ
    for start in range(0, len(y), segment_samples):
        end = min(start + segment_samples, len(y))  # Đảm bảo không vượt quá chiều dài của file âm thanh
        segment = y[start:end]
        
        # Trích xuất MFCC cho đoạn âm thanh
        mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=13)
        
        # Thêm MFCC vào danh sách (giữ nguyên độ dài 13 của mỗi đoạn)
        input_mfcc.append(mfcc.T)  # Chuyển từ (13, T) thành (T, 13) theo thời gian
    
    return input_mfcc

# Hàm tìm kiếm âm thanh
def search_audio(input_audio_path):
    input_mfcc = extract_mfcc_from_input(input_audio_path)
    
    # Đảm bảo tính trung bình các MFCC của input âm thanh theo chiều thời gian và chuyển thành vector 1D
    input_mfcc_mean = np.mean(np.concatenate(input_mfcc, axis=0), axis=0)  # Chuyển thành vector 1D
    
    distances = []  # Danh sách để lưu trữ khoảng cách và tên file tương ứng

    # Duyệt qua từng file trong database và so sánh với đoạn âm thanh input
    for file_name, file_mfcc in features.items():
        # Duyệt qua các đoạn trong file âm thanh trong database
        for segment_mfcc in file_mfcc:
            # Tính khoảng cách Euclidean giữa MFCC trung bình của đoạn input và đoạn trong database
            segment_mfcc_mean = np.mean(segment_mfcc, axis=1)  # Lấy trung bình MFCC trong database theo chiều thời gian
            
            # Tính khoảng cách Euclidean giữa MFCC trung bình của đoạn input và đoạn trong database
            distance = euclidean(input_mfcc_mean, segment_mfcc_mean)
            
            # Thêm kết quả vào danh sách
            distances.append((file_name, distance, segment_mfcc_mean))

    # Sắp xếp danh sách kết quả theo khoảng cách
    distances.sort(key=lambda x: x[1])  # Sắp xếp theo khoảng cách (index 1 là khoảng cách)

    # Trả về top 5 kết quả gần nhất
    top_7_results = distances[:7]
    
    # In ra kết quả
    print("Top 7 kết quả gần nhất:")
    for idx, (file_name, distance, _) in enumerate(top_7_results):
        print(f"{idx+1}. File âm thanh: {file_name}, Khoảng cách: {distance}")

# Ví dụ sử dụng hàm tìm kiếm với file âm thanh người dùng nhập
input_audio_path = "input/matketnoi_full.mp3"  # Đoạn âm thanh người dùng cung cấp (định dạng MP3)
search_audio(input_audio_path)
