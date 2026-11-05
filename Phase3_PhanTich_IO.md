# PHASE 3 — PHÂN TÍCH I/O CỦA SERVO ỨNG VIÊN SO VỚI HD1910

[README](README.md) · [Phase 1 – CAD](Phase1_CAD_HocServo.md) · [Phase 2 – Mô phỏng tải](Phase2_MoPhong_TaiServo.md) · [Phase 3 – Phân tích I/O](Phase3_PhanTich_IO.md) · [Phase 4 – Độ chế](Phase4_PhuongAn_DoChe.md) · [Phase 5 – Train](Phase5_Train_Policy.md) · [Phase 6 – Phần cứng & chạy thật](Phase6_PhanCung_ChayThat.md) · [Checklist](CHECKLIST.md)

---

> **Trạng thái:** khung phân tích (05/11/2026). Các ô về HD1910 và về bo zin của ứng viên phải xác minh bằng tài liệu hoặc đo thật trước khi chốt.
> **Đầu vào:** ứng viên đã qua tải ở [Phase 2](Phase2_MoPhong_TaiServo.md).
> **Đầu ra:** danh sách những gì ứng viên còn thiếu để train và chạy policy, cùng phương án khắc phục được chọn để làm ở [Phase 4](Phase4_PhuongAn_DoChe.md).

## 3.1. Policy cần gì từ actuator
Kiến trúc theo [microduck_rl](https://github.com/pollen-robotics/microduck_rl) và [xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl):
* Policy chạy ở **50 Hz**, xuất ONNX.
* **Action** là góc mục tiêu của từng khớp, gửi xuống servo.
* **Vòng PD bám góc chạy ngay trong firmware servo.** Ở XGO, gain đặt qua bus: KP 6 / KD 20 khi chạy (theo [docs/BOM.md](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/docs/BOM.md#values-used-by-xgo-duck)).
* Trong sim, hành vi của servo, gồm cả vòng P của firmware (`kp_fw=5`), được mô phỏng bằng mô hình **BAM** đã nhận dạng ([`1910_m6.json`](https://github.com/LuwuDynamics/xgoduck_rl/blob/main/src/mjlab_microduck/robot/xgoduck/params/1910_m6.json)). Mô hình gồm `kt`, `R`, `armature`, ma sát Stribeck và độ trễ lệnh khoảng 6 ms.
* **Observation:** gồm góc khớp, vận tốc khớp, action trước đó và IMU. *Danh sách chính xác cần đối chiếu code `xgoduck_rl`.*

Hệ quả: điều kiện quan trọng không phải là "chỉnh được gain" mà là **hành vi actuator cố định, lặp lại được và nhận dạng được bằng BAM**, sao cho sim giống thật.

Từ đó, mỗi actuator phải đáp ứng được:

| Yêu cầu | Vì sao cần |
|---|---|
| **R1. Đọc được góc khớp** ở ≥ tần số policy | Là observation chính |
| **R2. Có vận tốc khớp** (đo trực tiếp hoặc đạo hàm từ góc) | Là observation và cũng là thành phần D của vòng PD |
| **R3. Vòng bám vị trí có gain biết trước, cố định và mô hình hóa được** (tốt nhất là chỉnh được) | Policy học với một actuator cụ thể, cụ thể là mô hình BAM. Gain thật khác sim thì policy chạy sai |
| **R4. Đủ mô-men và tốc độ** | Đã kiểm ở Phase 2 |
| **R5. Biết hoặc giới hạn được dòng/mô-men** | Chống cháy khi đứng giữ tải lâu, và để làm System ID |
| **R6. Độ trễ lệnh → chuyển động đủ nhỏ và ổn định** | Độ trễ là yếu tố sim2real nặng nhất (§5.2) |
| **R7. Hành vi lặp lại được giữa 15 con** | Một policy dùng chung cho mọi khớp cùng loại |

## 3.2. So sánh HD1910 với MG92B zin

| Yêu cầu | HD1910 (servo bus) | MG92B zin (servo RC) |
|---|---|---|
| Lệnh vào | Lệnh vị trí qua bus TTL half-duplex, daisy-chain, 38.4 kbit/s – 1 Mbit/s (XGO dùng 1 Mbit/s), ID 0–253 | Xung PWM servo RC chuẩn (độ rộng xung ↔ góc) |
| R1 Góc | Encoder từ **12-bit** (0–4095 / 360°, khoảng 0.088°/bước), đọc qua bus | **Không có.** Chiết áp chỉ nối vào MCU bên trong servo (bo MG995 dùng PIC12F675, §4.3.1; MG92B cần xác nhận) |
| R2 Vận tốc | *Cần tra bảng thanh ghi* ([giao thức Feetech](https://mantech.co.za/datasheets/products/Feetech%20Smart%20Servo%20Communication%20Protocol.pdf)) | **Không có** |
| R3 Gain PD | **Chỉnh được qua bus** (XGO đặt KP/KD lúc chạy), đã có mô hình BAM | Không chỉnh được. Vòng điều khiển cố định trong firmware zin, **chưa có mô hình** |
| R4 Mô-men | Stall 9 / 12 / 15, rated 2.2 / 3.0 / 3.7 kgf·cm ở 4.8 / 6 / 7.4V; MJCF giới hạn ±1.04 N·m | Thấp hơn nhiều (§4.1.1). Kết luận theo Phase 2 |
| R5 Dòng/tải | *Cần tra bảng thanh ghi*. Datasheet: stall 1.2 / 1.6 / 2.0 A | **Không có** |
| R6 Độ trễ | BAM nhận dạng `command_delay` khoảng 6 ms (1 con, điều kiện đo của XGO) | Phụ thuộc chu kỳ xung lệnh và vòng PIC. *Đo* |
| R7 Lặp lại | Servo đóng gói sẵn; XGO vẫn hiệu chuẩn encoder từng con | Chiết áp và hộp số rẻ, sai khác lớn. Phải hiệu chuẩn từng con (§4.5.1) |
| Cơ khí | Hộp số 1:320, backlash ≤0.5°, spline 25T, thiết kế cho khung XGO | Trục đơn chịu uốn kém (§4.1.2), backlash và ma sát (§4.1.3) |

Nguồn cột HD1910: datasheet nhà sản xuất do XGO chép lại và mô hình BAM của xgoduck_rl (xem [README §6](README.md#6-nguồn-tham-khảo)), sai số ±10%.

**Việc còn phải làm:**
* Tra bảng thanh ghi Feetech để biết HD1910 có trả về vận tốc, tải và dòng không.
* Đọc code `xgoduck_rl` để có danh sách observation chính xác.
* Tháo 1 MG92B của dự án để đối chiếu linh kiện bo zin (§4.3.1, §4.3.3).

## 3.3. Danh sách thiếu hụt (gap) và hướng khắc phục

| Gap | Mô tả | Hướng khắc phục |
|---|---|---|
| G1 | Không đọc được góc (R1) | Đưa dây wiper chiết áp ra ADC của MCU trung tâm (cả A, B, C) |
| G2 | Không có vận tốc (R2) | Đạo hàm góc + lọc thông thấp (§5.2). Cần ADC ít nhiễu (Bước A3, A4) |
| G3 | Vòng điều khiển zin chưa biết và không chỉnh được (R3) | Tự chạy vòng PD trên MCU, nghĩa là bỏ firmware zin (A, A′ hoặc B). Hoặc giữ firmware zin rồi nhận dạng bằng BAM (C, chưa chắc làm được) |
| G4 | Không biết dòng (R5) | Shunt đo dòng: trên bo trung tâm (A) hoặc trong servo (B5 của §4.3.4) |
| G5 | Mô-men thấp (R4) | Quá áp có giới hạn dòng (§4.1.1). **Chỉ khi Phase 2 cho phép** |
| G6 | Cơ khí yếu, backlash | U-bracket (§4.1.2), PTFE + shim (§4.1.3), Domain Randomization (§5.2) |
| G7 | Sai khác giữa các con (R7) | Hiệu chuẩn $K_{ADC}$/offset từng con (§4.5.1), System ID (§4.5.3) |

## 3.4. Ma trận phương án

| | **A. Tháo cả bo zin, cầu H ở bo trung tâm** (§4.2) | **A′. Tháo bo zin, thay bo thông minh trong từng servo** (SMS MOD, §4.2) | **B. Gỡ PIC, giữ cầu H** (§4.3) | **C. Giữ bo zin, hàn thêm dây chiết áp** (§4.4) |
|---|---|---|---|---|
| G1 Góc | ✅ | ✅ | ✅ | ✅ |
| G3 Chỉnh PD | ✅ | ✅ | ✅ | ⚠️ cố định trong firmware zin; chỉ dùng được nếu nhận dạng được bằng BAM |
| G4 Dòng | ✅ shunt trên bo trung tâm | ✅ shunt 0.33 Ω + PGA nội, DRV8872 có giới hạn dòng | ✅ nếu làm B5 | ❌ |
| G5 Quá áp | ✅ có giới hạn dòng | ✅ SMS MOD cấp thẳng 2S | ⚠️ tùy áp chịu của linh kiện zin | ❌ bo zin định mức 5.0–6.6V |
| Bo trung tâm | MCU + 15 cầu H + đo dòng | Chỉ cần bus truyền thông, giống HD1910 | MCU 30 PWM + 15 ADC | MCU 15 PWM servo + 15 ADC |
| Độ khó / rủi ro | Bo driver lớn, chi phí | Phải làm 15 bo nhỏ vừa lọt thân MG92B; đã có người làm (SMS MOD) | Linh kiện zin chưa rõ thông số, dễ chập cầu H | Thấp nhất, nhưng phải mô hình hóa vòng zin trong sim |

**Cách chốt:**
* Phương án C rẻ và nhanh nhất. Nhưng nó **không đáp ứng R3**, nên chỉ dùng được nếu chấp nhận train policy với actuator có vòng PD cố định, và đo được vòng đó đủ tốt để đưa vào sim. Đây là giả thuyết, cần thử.
* **Servo mỏ không nằm trong policy RL** (điều khiển riêng qua console). Yêu cầu R1–R3, R6 về RL **không áp dụng** cho khớp này, chỉ cần đủ tải và bám được góc lệnh. Vậy MG90S/MG92B **giữ nguyên bo zin** (không độ) hoặc phương án C là đủ cho mỏ, rẻ nhất.
* Nếu cần R3/R5 thì chọn giữa A, A′ và B. A′ giữ được kiến trúc bus giống HD1910/XGO, nên thay đổi phía runtime ít nhất, nhưng chi phí 15 bo cần tính. Tiêu chí chính: tổng chi phí bo trung tâm, và việc linh kiện zin có chịu được 2S hay không (§4.3.3).
* So tổng chi phí của phương án chọn với HD1910 (xem 🟡 trong [Checklist](CHECKLIST.md)). Nếu không rẻ hơn đáng kể thì dùng HD1910.

## 3.5. Điều kiện xong Phase 3
- [ ] Đã điền đủ bảng §3.2 bằng số liệu có nguồn hoặc số đo.
- [ ] Đã chốt phương án (A/A′/B/C) cho từng nhóm khớp (chân / đầu), có ghi lý do.
- [ ] Đã so tổng chi phí với HD1910.

---

← [Phase 2](Phase2_MoPhong_TaiServo.md) · [Phase 4](Phase4_PhuongAn_DoChe.md) →
