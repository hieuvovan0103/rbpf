# Rao-Blackwell Particle Filter (RBPF)


## 1. RBPF là gì?

**Rao-Blackwell Particle Filter (RBPF)** là một biến thể nâng cao của **Particle Filter (PF)**, được thiết kế để cải thiện độ chính xác và giảm phương sai của ước lượng trong các bài toán suy luận trạng thái động. Ý tưởng cốt lõi của RBPF là:

- **lấy mẫu (sampling)** cho phần trạng thái khó xử lý, thường là phần **phi tuyến** hoặc **phi Gaussian**;
- **tích phân giải tích (analytic marginalization)** cho phần trạng thái còn lại nếu phần đó có cấu trúc xử lý được, ví dụ bằng **Kalman Filter**, **Extended Kalman Filter (EKF)**, **HMM filter** hoặc các bộ lọc tối ưu hữu hạn chiều khác.

Nhờ áp dụng nguyên lý **Rao-Blackwellization**, RBPF thường cho kết quả tốt hơn Particle Filter chuẩn khi mô hình có thể tách thành phần “khó” và phần “có thể giải chính xác hoặc gần chính xác”.

---

## 2. Ý tưởng hoạt động

Thay vì lấy mẫu toàn bộ vector trạng thái \(x_k\), RBPF chia trạng thái thành hai phần:

- \(x_k^p\): phần được biểu diễn bằng hạt (particles)
- \(x_k^m\): phần được khử tích phân bằng công thức giải tích

Khi đó, phân bố hậu nghiệm có thể được viết dưới dạng:

```math
p(x_{0:k}^p, x_k^m \mid z_{1:k}) = p(x_k^m \mid x_{0:k}^p, z_{1:k}) \; p(x_{0:k}^p \mid z_{1:k})
```

Điều này có nghĩa là:

1. Ta chỉ cần lấy mẫu cho phần \(x^p\);
2. Với mỗi particle, phần \(x^m\) được ước lượng bằng một bộ lọc giải tích;
3. Trọng số particle được cập nhật theo xác suất quan sát;
4. Thực hiện resampling để tránh suy giảm hạt.

---

## 3. Vì sao RBPF hiệu quả?

RBPF hiệu quả vì nó giảm số chiều cần lấy mẫu trực tiếp. Trong Particle Filter thông thường, khi số chiều trạng thái tăng, số lượng particle cần thiết tăng rất nhanh. RBPF khắc phục điều này bằng cách:

- giảm độ phức tạp của không gian lấy mẫu;
- giảm phương sai của bộ ước lượng;
- cải thiện độ ổn định số;
- tận dụng được cấu trúc tuyến tính/Gaussian nếu mô hình cho phép.

Nói ngắn gọn, **RBPF thường chính xác hơn PF chuẩn với cùng số lượng hạt**.

---

## 4. Quy trình tổng quát của RBPF

```text
Input: particles {x_{0:k-1}^{p,(i)}, w_{k-1}^{(i)}} for i = 1,...,N
For each time step k:
    1. Propagate particle state x_k^{p,(i)}
    2. For each particle, update marginalized state x_k^m using analytic filter
    3. Compute importance weight w_k^{(i)}
    4. Normalize weights
    5. Resample if needed
Output: posterior estimate of the system state
```

---

## 5. Ưu điểm

- Chính xác hơn Particle Filter cơ bản trong nhiều bài toán thực tế.
- Giảm phương sai nhờ áp dụng định lý Rao-Blackwell.
- Tận dụng được cấu trúc mô hình hỗn hợp: phi tuyến + tuyến tính/Gaussian.
- Phù hợp với các hệ thống có trạng thái ẩn phức tạp nhưng vẫn có một phần mô hình giải tích được.

---

## 6. Hạn chế

- Cài đặt phức tạp hơn Particle Filter thông thường.
- Cần xác định rõ phần trạng thái nào có thể marginalize.
- Hiệu quả phụ thuộc mạnh vào cấu trúc mô hình.
- Có thể tốn tài nguyên nếu số particle lớn và mỗi particle cần một bộ lọc con riêng.

---

## 7. Ứng dụng phổ biến

RBPF được dùng rộng rãi trong các lĩnh vực sau:

- **Robot localization và SLAM**
- **Target tracking / object tracking**
- **Navigation systems**
- **Sensor fusion**
- **Dynamic Bayesian Networks (DBNs)**
- **Nonlinear state estimation**

Một ứng dụng rất nổi tiếng là **RBPF-SLAM**, trong đó quỹ đạo robot được biểu diễn bằng particle còn bản đồ môi trường được cập nhật bằng mô hình xác suất có điều kiện.

---

## 8. So sánh RBPF và Particle Filter chuẩn

| Tiêu chí | Particle Filter | Rao-Blackwell Particle Filter |
|---|---:|---:|
| Lấy mẫu toàn bộ trạng thái | Có | Không hoàn toàn |
| Tận dụng cấu trúc tuyến tính/Gaussian | Không | Có |
| Phương sai ước lượng | Cao hơn | Thấp hơn |
| Độ chính xác với cùng số particle | Thấp hơn | Cao hơn |
| Độ phức tạp cài đặt | Thấp hơn | Cao hơn |

---

## 9. Ví dụ mô tả ngắn

Giả sử trạng thái hệ thống gồm:

- vị trí và hướng chuyển động của robot (phi tuyến)
- sai số cảm biến hoặc một phần động học tuyến tính (có thể mô hình Gaussian)

Thay vì lấy mẫu toàn bộ trạng thái, RBPF sẽ:

- dùng **particles** để theo dõi quỹ đạo robot;
- dùng **Kalman Filter** cho phần trạng thái tuyến tính;
- kết hợp hai phần để tạo ra ước lượng hậu nghiệm tốt hơn.

---

## 10. Khi nào nên dùng RBPF?

RBPF phù hợp khi:

- bài toán có **mô hình hỗn hợp**, gồm phần khó lấy mẫu và phần có thể giải tích;
- Particle Filter chuẩn cần quá nhiều hạt mới đạt độ chính xác mong muốn;
- cần cân bằng giữa **độ chính xác** và **chi phí tính toán**;
- bài toán có cấu trúc điều kiện đủ tốt để áp dụng Kalman/EKF/HMM trong từng particle.

---

## 11. Từ khóa liên quan

`particle filter` · `rao-blackwellization` · `bayesian filtering` · `dynamic bayesian network` · `state estimation` · `robotics` · `slam` · `tracking` · `sensor fusion`

---

## 12. Tài liệu tham khảo gợi ý

1. Doucet, A., de Freitas, N., Murphy, K., & Russell, S. *Rao-Blackwellised Particle Filtering for Dynamic Bayesian Networks*.
2. Särkkä, S. *Lecture Notes on Particle Filtering*.
3. Các tài liệu về **RBPF-SLAM**, **Monte Carlo Localization**, và **Bayesian State Estimation**.

---

## 13. Kết luận

RBPF là một phương pháp lọc Bayes mạnh mẽ cho các hệ động phi tuyến, đặc biệt hiệu quả khi mô hình có thể tách thành phần lấy mẫu và phần giải tích. So với Particle Filter truyền thống, RBPF giúp giảm phương sai, tăng độ chính xác và tận dụng tốt hơn cấu trúc xác suất của hệ thống. Vì vậy, đây là một công cụ rất quan trọng trong robot, theo dõi mục tiêu, điều hướng và suy luận trên mô hình động.
