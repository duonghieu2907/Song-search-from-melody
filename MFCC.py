import librosa
import numpy as np
import os

# Thư mục chứa file âm thanh
data_dir = "dataset/"
features = {}

# Độ dài mỗi đoạn (4 giây)
segment_duration = 4  # đơn vị là giây

# Trích xuất MFCC từ từng file trong dataset
for file_name in os.listdir(data_dir):
    if file_name.endswith(".mp3"):  # Thay đổi sang .mp3
        file_path = os.path.join(data_dir, file_name)
        
        # Load file âm thanh (librosa hỗ trợ .mp3 nếu ffmpeg được cài đặt)
        y, sr = librosa.load(file_path, sr=None)
        
        # Tính số mẫu cho mỗi đoạn 4 giây
        segment_samples = segment_duration * sr
        
        # Danh sách chứa MFCC cho từng đoạn
        file_mfcc = []

        # Chia bài hát thành các đoạn nhỏ
        for start in range(0, len(y), segment_samples):
            end = min(start + segment_samples, len(y))  # Đảm bảo không vượt quá chiều dài của file âm thanh
            segment = y[start:end]
            
            # Trích xuất MFCC cho đoạn âm thanh
            mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=13)
            
            # Lưu MFCC của đoạn âm thanh này vào danh sách
            file_mfcc.append(mfcc)

        # Lưu các MFCC của file vào dictionary
        features[file_name] = file_mfcc

# Lưu các đặc trưng MFCC vào file .npy
np.save("audio_features_segments.npy", features)
print("Hoàn thành trích xuất và lưu MFCC cho từng đoạn!")
