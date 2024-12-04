import os
import numpy as np
from extract_mfcc import extract_mfcc  # Import hàm extract_mfcc

# Thư mục chứa file âm thanh
data_dir = "dataset/"
features = {}

# Độ dài mỗi đoạn (4 giây)
segment_duration = 4  # đơn vị là giây

# Trích xuất MFCC từ từng file trong dataset
for file_name in os.listdir(data_dir):
    if file_name.endswith(".mp3"):  # Thay đổi sang .mp3
        file_path = os.path.join(data_dir, file_name)
        
        # Sử dụng hàm extract_mfcc để trích xuất MFCC
        file_mfcc, sr = extract_mfcc(file_path, segment_duration)
        
        # Lưu các MFCC của file vào dictionary
        features[file_name] = file_mfcc

# Lưu các đặc trưng MFCC vào file .npy
np.save("audio_features_segments.npy", features)
print("Hoàn thành trích xuất và lưu MFCC cho từng đoạn!")
