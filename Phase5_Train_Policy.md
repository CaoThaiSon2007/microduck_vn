# PHASE 5 — TRAIN POLICY & MÔ PHỎNG VỚI ACTUATOR THẬT

[README](README.md) · [Phase 1 – CAD](Phase1_CAD_HocServo.md) · [Phase 2 – Mô phỏng tải](Phase2_MoPhong_TaiServo.md) · [Phase 3 – Phân tích I/O](Phase3_PhanTich_IO.md) · [Phase 4 – Độ chế](Phase4_PhuongAn_DoChe.md) · [Phase 5 – Train](Phase5_Train_Policy.md) · [Phase 6 – Phần cứng & chạy thật](Phase6_PhanCung_ChayThat.md) · [Checklist](CHECKLIST.md)

---

> **Trạng thái:** chưa bắt đầu.
> **Đầu vào:** MJCF của ứng viên đã chốt (Phase 1), thông số actuator đo được (§4.5.3).
> **Đầu ra:** policy chạy ổn trong sim với giới hạn servo thật, sẵn sàng đưa lên robot ở [Phase 6](Phase6_PhanCung_ChayThat.md).
>
> **Pipeline:** dùng lại [microduck_rl](https://github.com/pollen-robotics/microduck_rl) (Pollen, bản gốc) hoặc nhánh [xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl) (đã chỉnh cho hình học XGO và servo 1910). Cả hai gồm:
> * Train PPO trên [mjlab](https://github.com/mujocolab/mjlab) (MuJoCo Warp).
> * Mô hình actuator [BAM](https://github.com/Rhoban/bam).
> * Domain Randomization và mô phỏng backlash.
> * Xuất ONNX chạy ở 50 Hz.
> * Task chính: `Velocity`, `StandUp`, `SitStand`…
>
> ⚠️ Theo [UPSTREAM.md của XGO](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/UPSTREAM.md): **không dùng lại policy của robot khác** chỉ vì tensor trùng kích thước. Actuator, hình học và calibration khác nhau thì phải train lại.

## 5.1. Đưa mô hình actuator thật vào MuJoCo
* **Cách làm theo xgoduck_rl:** mỗi loại servo có một file tham số BAM.
  * Với HD1910, file `1910_m6.json` gồm `kt`, `R`, `armature`, các hệ số ma sát (Stribeck, phụ thuộc tải), `command_delay`.
  * Thông số chạy được khai báo trong `xgoduck_constants.py`, ví dụ `kp_fw=5.0`.
  * Với servo độ: nhận dạng bằng BAM (§4.5.3) để ra file JSON tương đương, ví dụ `mg92b_<phương án>.json`. Sau đó thay vào cấu hình actuator.
* **Giới hạn mô-men:** lấy theo số **đo được** (§2.5, §4.5.3), không lấy theo datasheet. Có thêm **giới hạn mô-men phụ thuộc vận tốc** do back-EMF. BAM mô hình hóa phần này qua `kt`, `R` và áp nguồn.
* **Các thông số khớp:** `kp`, `kv`, `frictionloss`, `damping`, `armature` lấy theo System ID (§4.5.3).
* **Chế độ cầu H:** brake hoặc coast phải giống phần cứng. Phương án B có thể chỉ có coast (§4.3.3).
* **Phương án C:** mô hình hóa luôn vòng điều khiển của PIC đã đo (§4.4).
* **Tần số:** vòng PD và policy chạy đúng như chuẩn điều khiển ở [README](README.md) §5.2.

## 5.2. Sim2Real cho servo rẻ: lọc vận tốc & Domain Randomization
* Thêm bộ lọc thông thấp bậc 1 (Low-pass Filter) với tần số cắt $f_c = 35\text{ Hz}$ cho khâu đạo hàm vận tốc góc $\dot{q}$ đọc từ chiết áp để triệt tiêu gai nhiễu do độ rơ:
  $$\dot{q}_{\text{filtered}}[k] = \alpha \cdot \dot{q}_{\text{filtered}}[k-1] + (1 - \alpha) \cdot \frac{q[k] - q[k-1]}{\Delta t}, \qquad \alpha = e^{-2\pi f_c \Delta t}$$
  * $\alpha$ phụ thuộc tần số vòng lặp: ở $1\text{ kHz}$ ($\Delta t = 1\text{ ms}$), $\alpha \approx 0.80$. Đổi tần số vòng lặp là phải tính lại $\alpha$.
  * ⚠️ Vận tốc đạo hàm từ ADC rất nhiễu: ở $1\text{ kHz}$, 1 bước ADC ($\approx 0.0008\text{ rad}$) tương đương lượng tử vận tốc $\approx 0.8\text{ rad/s}$. Bộ lọc là cần nhưng chưa đủ — phải kết hợp chống nhiễu phần cứng (Bước A3, Bước A4).
* **Domain Randomization phải viết trong code train (env wrapper)** — MJCF `.xml` không có cú pháp khai báo dải ngẫu nhiên. Trong XML chỉ đặt giá trị danh định của `frictionloss`, `damping`, `armature` trên joint. Các dải random (giá trị ban đầu, cần thu hẹp theo số đo System ID ở §4.5.3):
  * `frictionloss`: khoảng $[0.02, 0.08]\text{ N}\cdot\text{m}$.
  * `damping`: khoảng $[0.005, 0.03]\text{ N}\cdot\text{m}\cdot\text{s/rad}$.
  * `armature` (quán tính rotor quy về khớp — rất lớn với hộp số tỉ số cao): random quanh giá trị đo được.
  * **Độ trễ (latency) action/observation:** random — thường là yếu tố sim2real nặng nhất, bản trước bỏ sót.
  * Cộng nhiễu quan sát vị trí khớp (Observation Noise): $\mathcal{U}(-0.03, +0.03)\text{ rad}$ ($\approx \pm 1.7^\circ$) để mạng Neural miễn nhiễm với độ rơ bánh răng.

## 5.3. Train & kiểm tra
1. Train policy trên MJCF của ứng viên (Phase 1), với mô hình BAM đo thật (§5.1) và Domain Randomization (§5.2). Train baseline HD1910 song song bằng `xgoduck_rl` để có mốc so sánh.
2. **Kiểm tra lại tải khi chạy policy:** chạy `dynamic_load.py` (§2.3) với policy thay cho quỹ đạo gait. Policy có thể đi kiểu khác gait mẫu. Nếu $\tau_{peak}$/$\tau_{RMS}$ vượt tiêu chí §2.3 thì phải phạt mô-men trong hàm reward hoặc đổi servo cho khớp đó.
3. Thử robustness: push recovery, mặt sàn nghiêng hoặc trơn, pin yếu (giảm giới hạn mô-men).

## 5.4. Điều kiện xong Phase 5
- [ ] Policy đi ổn trong sim với **giới hạn servo đo thật** và Domain Randomization bật.
- [ ] Tải khi chạy policy nằm trong tiêu chí §2.3.
- [ ] Policy đã export (ONNX) và chạy được ở đúng tần số mục tiêu trên phần cứng điều khiển dự kiến.

---

← [Phase 4](Phase4_PhuongAn_DoChe.md) · [Phase 6](Phase6_PhanCung_ChayThat.md) →
