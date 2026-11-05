# PHASE 6 — MUA / GIA CÔNG PHẦN CỨNG & CHẠY THẬT

[README](README.md) · [Phase 1 – CAD](Phase1_CAD_HocServo.md) · [Phase 2 – Mô phỏng tải](Phase2_MoPhong_TaiServo.md) · [Phase 3 – Phân tích I/O](Phase3_PhanTich_IO.md) · [Phase 4 – Độ chế](Phase4_PhuongAn_DoChe.md) · [Phase 5 – Train](Phase5_Train_Policy.md) · [Phase 6 – Phần cứng & chạy thật](Phase6_PhanCung_ChayThat.md) · [Checklist](CHECKLIST.md)

---

> **Trạng thái:** mới có BOM nháp cho phương án MG92B.
> **Đầu vào:** ứng viên và phương án đã chốt (Phase 2–4), policy đã qua sim (Phase 5).

## 6.1. Bảng dự toán vật tư (BOM) — nháp cho phương án MG92B
> BOM dưới đây viết cho MG92B. Nếu Phase 2–3 chốt ứng viên hoặc phương án khác thì lập lại. Mọi giá là ước tính, cần cập nhật khi mua.

| STT | Hạng mục vật tư | Quy cách kỹ thuật | Số lượng | Đơn giá ước tính (VNĐ) | Thành tiền (VNĐ) | Ghi chú / Nguồn mua (TP.HCM / Shopee) |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | **Servo MG92B** | 14g, Nhông kim loại, Động cơ Coreless, $3.5\text{ kg}\cdot\text{cm}$ | 15 cái (hoặc 10 chân + 5 MG90S đầu) | $65.000$ | $975.000$ | Chọn loại bánh răng đồng/thép chuẩn, có vòng bi cổ trục |
| 2 | **Vòng bi mini đỡ lưng** | **MR63ZZ** ($3\times 6\times 2.5\text{ mm}$) hoặc **623ZZ** ($3\times 10\times 4\text{ mm}$) | 20 vòng | $2.500$ | $50.000$ | Làm gối đỡ trục phụ mặt đáy (Dual-support) |
| 3 | **Chốt làm trục giả** | **Chốt thép $\Phi 3\text{ mm}$ dung sai h6 (dowel pin)** hoặc **ốc vai (shoulder screw) thân trơn $\Phi 3$** | 20 con | $500$ | $10.000$ | ⚠️ Không dùng phần ren ốc M3 lọt vòng bi (ren $<\Phi 3$ → lỏng, cào nát lòng bi; đầu ốc chìm $\approx\Phi 5.5$ không lọt lỗ $3\text{ mm}$). Giá cần cập nhật theo loại chốt |
| 4 | **Dây cáp tín hiệu/nguồn** | Dây Silicon mềm **26AWG** (cho Motor) & **28AWG/30AWG** (cho Potentiometer) | 10 mét | $5.000$ | $50.000$ | Dây silicon chịu uốn gập liên tục ở khớp háng/gối |
| 5 | **Tụ gốm chống nhiễu** | Tụ Ceramic **104 ($0.1\ \mu\text{F}$)** chân cắm hoặc SMD 0805 | 20 con | $200$ | $4.000$ | Hàn trực tiếp lên 2 cực động cơ DC |
| 6 | **Mỡ bôi trơn hộp số** | **Chỉ dùng mỡ PTFE (Teflon)** — không dùng mỡ trắng Lithium (đặc, gây dính răng ở tốc độ thấp, chính là loại cần loại bỏ ở §4.1.3) | 1 hũ nhỏ | $25.000$ | $25.000$ | Giảm ma sát tĩnh (Stiction) hộp số |
| 7 | **Bo driver trung tâm** | *Phương án A:* MCU (≥ 15 kênh ADC dùng được thật) + 15 cầu H + 15 kênh cảm biến dòng (shunt/driver có chân sense) + mạch đo áp pin. *Phương án B:* MCU 30 PWM + 15 ADC (+15 ADC dòng) + mạch đo áp pin, không cần cầu H (§4.3.2) | 1 bộ | *Chưa báo giá* | *Chưa tính* | Xem §4.1.1, §4.3 và [Checklist](CHECKLIST.md) |
| 8 | **Pin + nguồn logic + connector** | Pin 2S (LiPo, hoặc 18650 như XGO-Duck), regulator cho logic, rail $3.3\text{V}$ tham chiếu ADC, connector | 1 bộ | *Chưa báo giá* | *Chưa tính* | |
| **TỔNG (mới gồm mục 1–6)** | | | **15 khớp** | | **$1.114.000\text{ ₫}$** | ⚠️ Chưa gồm mục 7–8. HD1910 là servo bus đã có sẵn driver, encoder và bộ điều khiển, nên chỉ so được giá khi cộng đủ mục 7–8. Giá HD1910 về VN phải tra lại |

## 6.2. Gia công & lắp ráp
1. In các chi tiết theo CAD đã chốt (Phase 1). Cân lại và so với khối lượng đã đưa vào MJCF (§1.3). Lệch nhiều thì cập nhật MJCF rồi chạy lại Phase 2.
2. Độ đủ 15 servo theo SOP của phương án đã chọn (§4.2 / §4.3 / §4.4). Mỗi con qua bàn thử §4.5 trước khi lắp.
3. Khi lắp horn, căn **tư thế đứng nằm giữa hành trình chiết áp** (Bước A2 ở §4.2).
4. Đi dây theo chi (Bước A4 / §4.3.5). Dây nguồn công suất chọn tiết diện theo dòng stall đo được.

## 6.3. Chạy thật lần đầu
1. **Treo robot**, chân không chạm đất. Nguồn giới hạn dòng.
2. Thử **từng khớp**: chiều quay, chiều tăng ADC, dấu và offset so với sim (Bước A5). Watchdog phản hồi dương phải đang bật.
3. Đứng yên trên sàn: đo dòng từng khớp, rồi so với tải tĩnh dự đoán ở §2.2. Lệch nhiều nghĩa là MJCF hoặc mô hình actuator sai, phải quay lại sửa.
4. Chạy policy ở tốc độ thấp, có người giữ dây an toàn, rồi mới tăng dần.
5. Theo dõi nhiệt servo sau vài phút đi, so với $\tau_{RMS}$ dự đoán (§2.3).

---

← [Phase 5](Phase5_Train_Policy.md) · [Checklist](CHECKLIST.md) →
