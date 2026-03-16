import pandas as pd
import matplotlib.pyplot as plt

def plot_trajectory_comparison(csv_file):
    try:
        # 1. Đọc dữ liệu
        print(f"Đang đọc file {csv_file}...")
        df = pd.read_csv(csv_file)

        # === FIX LỖI (0,0) TẠI ĐÂY ===
        # Lọc bỏ các dòng mà Lat hoặc Lon bằng 0 (hoặc xấp xỉ 0)
        # Giữ lại dữ liệu hợp lệ (Lớn hơn 1 độ để an toàn)
        print(f"Số lượng mẫu trước khi lọc rác: {len(df)}")
        df_clean = df[(abs(df['Lat_Raw']) > 1.0) & (abs(df['Lon_Raw']) > 1.0)].copy()
        print(f"Số lượng mẫu sau khi loại bỏ điểm (0,0): {len(df_clean)}")

        if len(df_clean) == 0:
            print("Cảnh báo: Không còn dữ liệu sau khi lọc! Kiểm tra lại file CSV.")
            return

        # 2. Cấu hình hình vẽ
        plt.figure(figsize=(12, 10))
        plt.style.use('seaborn-v0_8-whitegrid')

        # A. Vẽ GPS Thô (Raw)
        plt.plot(df_clean['Lon_Raw'], df_clean['Lat_Raw'],
                 'r.', markersize=4, alpha=0.3, label='GPS Thô (Raw)')

        # B. Vẽ RBPF (Estimated)
        # Cũng cần lọc điểm 0 ở kết quả ước lượng (nếu có)
        df_est_clean = df[(abs(df['Lat_Est']) > 1.0) & (abs(df['Lon_Est']) > 1.0)]
        plt.plot(df_est_clean['Lon_Est'], df_est_clean['Lat_Est'],
                 'b-', linewidth=2.5, alpha=0.9, label='RBPF (Đã lọc)')

        # C. Đánh dấu điểm đầu/cuối (Dựa trên dữ liệu sạch)
        plt.scatter(df_est_clean['Lon_Est'].iloc[0], df_est_clean['Lat_Est'].iloc[0],
                    c='green', s=150, marker='^', label='Bắt đầu', zorder=5)
        plt.scatter(df_est_clean['Lon_Est'].iloc[-1], df_est_clean['Lat_Est'].iloc[-1],
                    c='black', s=150, marker='X', label='Kết thúc', zorder=5)

        # 3. Trang trí
        plt.title('So sánh Quỹ đạo (Đã loại bỏ điểm 0,0)', fontsize=16, fontweight='bold')
        plt.xlabel('Kinh độ (Longitude)')
        plt.ylabel('Vĩ độ (Latitude)')
        plt.legend(fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.axis('equal') # Giữ tỷ lệ bản đồ chuẩn

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    plot_trajectory_comparison('final_comparison_3.csv')