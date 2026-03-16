import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class KalmanFilter:
    def __init__(self, x0, P0, Q, R):
        self.x = x0.copy()
        self.P = P0.copy()
        self.Q = Q
        self.R = R
        self.C = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]])

    def predict(self, dt, accel_n, accel_e, alpha=0.5):
        R_earth = 6378137.0
        lat_rad = np.deg2rad(self.x[0])
        meters_to_lat = 1.0 / R_earth * (180.0 / np.pi)
        meters_to_lon = 1.0 / (R_earth * np.cos(lat_rad)) * (180.0 / np.pi)

        F = np.eye(4)
        F[0, 2] = dt * meters_to_lat
        F[1, 3] = dt * meters_to_lon
        F[2, 2] = alpha
        F[3, 3] = alpha

        self.x[0] += self.x[2] * dt * meters_to_lat
        self.x[1] += self.x[3] * dt * meters_to_lon
        self.x[2] = self.x[2] * alpha + accel_n * dt
        self.x[3] = self.x[3] * alpha + accel_e * dt

        self.P = F @ self.P @ F.T + self.Q

    def update(self, y):
        y_pred = self.C @ self.x
        innovation = y - y_pred
        S = self.C @ self.P @ self.C.T + self.R
        K = self.P @ self.C.T @ np.linalg.inv(S)
        self.x = self.x + K @ innovation
        I = np.eye(4)
        term = (I - K @ self.C)
        self.P = term @ self.P @ term.T + K @ self.R @ K.T

        S_det = np.linalg.det(S)
        S_inv = np.linalg.inv(S)
        mahalanobis = innovation.T @ S_inv @ innovation
        return -0.5 * (mahalanobis + np.log(S_det) + 2 * np.log(2 * np.pi))

    def copy(self):
        return KalmanFilter(self.x, self.P, self.Q, self.R)

class RBPF:
    def __init__(self, N, R1n, R2, kf_template):
        self.N = N
        self.R1n = R1n

        self.particles_heading = np.random.uniform(-np.pi, np.pi, N)
        self.kfs = [kf_template.copy() for _ in range(N)]

        # Khởi tạo weights ban đầu
        self.weights = np.ones(N) / N
        self.log_weights = np.zeros(N) - np.log(N)

    def predict(self, gyro_z, accel_n, accel_e, dt):
        noise_heading = np.random.normal(0, np.sqrt(self.R1n), self.N)
        for i in range(self.N):
            self.particles_heading[i] += gyro_z * dt + noise_heading[i]
            self.particles_heading[i] = np.arctan2(np.sin(self.particles_heading[i]),
                                                   np.cos(self.particles_heading[i]))
            self.kfs[i].predict(dt, accel_n, accel_e)

    def update(self, gps_lat, gps_lon):
        y = np.array([gps_lat, gps_lon])
        for i in range(self.N):
            lik = self.kfs[i].update(y)
            self.log_weights[i] += lik

        max_log_w = np.max(self.log_weights)
        weights = np.exp(self.log_weights - max_log_w)

        # Tránh chia cho 0
        sum_w = np.sum(weights)
        if sum_w > 0:
            weights /= sum_w
        else:
            weights = np.ones(self.N) / self.N

        self.weights = weights
        self.log_weights = np.log(weights + 1e-300)

        N_eff = 1.0 / np.sum(weights**2)
        if N_eff < self.N / 2:
            self.resample()

    def resample(self):
        indices = np.zeros(self.N, dtype=int)
        cumsum = np.cumsum(self.weights)
        step = 1.0 / self.N
        u = np.random.uniform(0, step)
        idx = 0
        for i in range(self.N):
            while u > cumsum[idx]:
                idx += 1
                if idx >= self.N: idx = self.N - 1
            indices[i] = idx
            u += step

        self.particles_heading = self.particles_heading[indices]
        self.kfs = [self.kfs[i].copy() for i in indices]
        self.weights = np.ones(self.N) / self.N
        self.log_weights = np.zeros(self.N) - np.log(self.N)

    def get_estimate(self):
        sin_sum = np.sum(self.weights * np.sin(self.particles_heading))
        cos_sum = np.sum(self.weights * np.cos(self.particles_heading))
        heading_est = np.arctan2(sin_sum, cos_sum)

        x_est = np.zeros(4)
        for i in range(self.N):
            x_est += self.weights[i] * self.kfs[i].x
        return heading_est, x_est


def load_data(filepath):
    try:
        df = pd.read_csv(filepath, sep=None, engine='python')
        print(f"Columns found: {df.columns}")

        col_map = {
            'Timestamp': 'time',
            'Latitude': 'lat',
            'Longtidue': 'lon',
            'gyro Z': 'gyro_z',
            'Accel North': 'acc_n',
            'Accel East': 'acc_e'
        }

        missing_cols = [c for c in col_map.keys() if c not in df.columns]
        if missing_cols:
            print(f"CẢNH BÁO: Không tìm thấy các cột: {missing_cols}")
            return None

        df = df.rename(columns=col_map)

        try:
            df['time'] = pd.to_datetime(df['time'])
        except:
            df['time'] = pd.to_datetime(df['time'], format='mixed', dayfirst=True)

        df['dt'] = df['time'].diff().dt.total_seconds().fillna(0.1)
        df.loc[df['dt'] > 1.0, 'dt'] = 0.1
        df.loc[df['dt'] <= 0, 'dt'] = 0.01

        #
        initial_len = len(df)
        # 1. Lọc bỏ dữ liệu rác
        df = df[(abs(df['lat']) > 1.0) & (abs(df['lon']) > 1.0)]
        print(f"Đã loại bỏ {initial_len - len(df)} dòng dữ liệu GPS lỗi (0,0)")

        # 2. RESET INDEX
        df = df.reset_index(drop=True)
        # ------------------------------

        return df
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return None

if __name__ == "__main__":
    FILE_PATH = r'Data_05052025_18401919_signal_loss.csv'
    EXPORT_FILE_PATH = r'final_comparison_3.csv'

    df = load_data(FILE_PATH)


    if df is not None:
        print(f"Đã load {len(df)} dòng dữ liệu.")

        # Init parameters
        Q_kf = np.diag([1e-12, 1e-12, 0.5**2, 2.0**2])
        gps_err = 4.5e-5 * 0.5
        R_kf = np.diag([gps_err**2, gps_err**2])
        R_gyro = (0.05)**2
        N = 100

        x0 = np.array([df['lat'].iloc[0], df['lon'].iloc[0], 0.0, 0.0])
        P0 = np.diag([1e-6, 1e-6, 1.0, 1.0])

        kf_temp = KalmanFilter(x0, P0, Q_kf, R_kf)
        pf = RBPF(N, R_gyro, R_kf, kf_temp)

        results = []
        print("Đang xử lý...")

        # Vì đã reset_index, i bây giờ chạy từ 0 -> len(df)-1 khớp với iloc
        for i, row in df.iterrows():
            dt = row['dt']
            pf.predict(row['gyro_z'], row['acc_n'], row['acc_e'], dt)

            if i > 0 and (row['lat'] != df['lat'].iloc[i-1] or row['lon'] != df['lon'].iloc[i-1]):
                pf.update(row['lat'], row['lon'])
            elif i == 0:
                pf.update(row['lat'], row['lon']) # Luôn update điểm đầu tiên

            heading, state = pf.get_estimate()
            results.append([
                row['time'], row['lat'], row['lon'],
                state[0], state[1], state[2], state[3], heading
            ])

            if i % 1000 == 0: print(f"Processing {i}/{len(df)}")

        cols = ['Time', 'Lat_Raw', 'Lon_Raw', 'Lat_Est', 'Lon_Est', 'Vel_N', 'Vel_E', 'Heading']
        res_df = pd.DataFrame(results, columns=cols)
        res_df.to_csv(EXPORT_FILE_PATH, index=False)
        print("Đã xuất file: " + EXPORT_FILE_PATH)