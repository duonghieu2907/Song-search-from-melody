import librosa
import numpy as np

# Hàm tính MFCC cho một file âm thanh
def extract_mfcc(input_audio_path, segment_duration=4):
    # Load file âm thanh (librosa hỗ trợ .mp3 nếu ffmpeg được cài đặt)
    y, sr = librosa.load(input_audio_path, sr=None)
    
    # Tính số mẫu cho mỗi đoạn
    segment_samples = segment_duration * sr
    
    # Danh sách chứa MFCC cho từng đoạn
    mfcc_list = []

    # Chia bài hát thành các đoạn nhỏ
    for start in range(0, len(y), segment_samples):
        end = min(start + segment_samples, len(y))  # Đảm bảo không vượt quá chiều dài của file âm thanh
        segment = y[start:end]
        
        # Trích xuất MFCC cho đoạn âm thanh
        mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=13)
        
        # Thêm MFCC vào danh sách
        mfcc_list.append(mfcc.T)  # Chuyển từ (13, T) thành (T, 13) theo thời gian

    return mfcc_list, sr  # Trả về cả MFCC và sample rate (sr) để sử dụng khi cần thiết
