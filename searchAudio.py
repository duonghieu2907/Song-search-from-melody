import numpy as np
from scipy.spatial.distance import euclidean
from extract_mfcc import extract_mfcc  # Import hàm extract_mfcc

# Đọc dữ liệu đã lưu
features = np.load("audio_features_segments.npy", allow_pickle=True).item()

# Hàm tìm kiếm âm thanh
def search_audio(input_audio_path):
    # Sử dụng hàm extract_mfcc để trích xuất MFCC từ đoạn âm thanh input
    input_mfcc, sr = extract_mfcc(input_audio_path)
    
    # Đảm bảo tính trung bình các MFCC của input âm thanh theo chiều thời gian và chuyển thành vector 1D
    input_mfcc_mean = np.mean(np.concatenate(input_mfcc, axis=0), axis=0)  # Chuyển thành vector 1D
    
    distances = []  # Danh sách để lưu trữ khoảng cách và tên file tương ứng

    # Duyệt qua từng file trong database và so sánh với đoạn âm thanh input
    for file_name, file_mfcc in features.items():
        # Duyệt qua các đoạn trong file âm thanh trong database
        for segment_mfcc in file_mfcc:
            # Tính trung bình MFCC trong database theo chiều thời gian
            segment_mfcc_mean = np.mean(segment_mfcc, axis=0)  # Trung bình theo chiều thời gian
            
            # Tính khoảng cách Euclidean giữa MFCC trung bình của đoạn input và đoạn trong database
            distance = euclidean(input_mfcc_mean, segment_mfcc_mean)
            
            # Thêm kết quả vào danh sách
            distances.append((file_name, distance, segment_mfcc_mean))

    # Sắp xếp danh sách kết quả theo khoảng cách
    distances.sort(key=lambda x: x[1])  # Sắp xếp theo khoảng cách (index 1 là khoảng cách)

    # Trả về top 7 kết quả gần nhất
    top_7_results = distances[:7]
    
    # In ra kết quả
    print("Top 7 kết quả gần nhất:")
    for idx, (file_name, distance, _) in enumerate(top_7_results):
        print(f"{idx+1}. File âm thanh: {file_name}, Khoảng cách: {distance}")

# Ví dụ sử dụng hàm tìm kiếm với file âm thanh người dùng nhập
input_audio_path = "input/matketnoi_cover.mp3"  # Đoạn âm thanh người dùng cung cấp (định dạng MP3)
search_audio(input_audio_path)
