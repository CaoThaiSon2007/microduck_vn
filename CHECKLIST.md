# CHECKLIST LỖI CẦN NÉ — THEO TỪNG PHASE

[README](README.md) · [Phase 1 – CAD](Phase1_CAD_HocServo.md) · [Phase 2 – Mô phỏng tải](Phase2_MoPhong_TaiServo.md) · [Phase 3 – Phân tích I/O](Phase3_PhanTich_IO.md) · [Phase 4 – Độ chế](Phase4_PhuongAn_DoChe.md) · [Phase 5 – Train](Phase5_Train_Policy.md) · [Phase 6 – Phần cứng & chạy thật](Phase6_PhanCung_ChayThat.md) · [Checklist](CHECKLIST.md)

---

> Tổng hợp sau review 03/11/2026, cập nhật 05/11/2026.
> 🔴 nặng: làm sai là hỏng servo hoặc robot không chạy, thường phải làm lại cả 15 con. 🟠 trung bình: không hỏng ngay nhưng tốn công debug. 🟡 số liệu cần kiểm chứng trước khi dùng.

## Phase 1 — CAD
- [ ] 🔴 **Kiểm tra số răng spline horn** của ứng viên trước khi mua horn hoặc vẽ CAD. (§4.1.2)
- [ ] 🔴 **Giữ nguyên trục khớp của XGO-Duck** khi sửa hốc. Đổi trục khớp thì kết quả Phase 2 giữa các ứng viên không còn so được. (§1.2)
- [ ] 🟠 So `range` khớp trong MJCF với hành trình chốt chặn của servo. Đầu gối và hông pitch thường cần gập sâu. (§1.2, Bước A2)
- [ ] 🟠 *(MG92B)* Chừa chỗ cho U-bracket, vòng bi, chốt trục giả, nắp đáy (chứa bo zin nếu chọn phương án B) và đường luồn bó dây. (§1.2, §4.1.2, §4.3.5)
- [ ] 🟡 Khối lượng chi tiết in 3D phải lấy từ **cân bản in thật**, không dùng số CAD tự tính theo vật đặc. (§1.3)
- [ ] 🟡 Kích thước servo đo bằng thước kẹp trên con thật. (§1.1)
- [ ] 🔴 Cơ khí XGO **chỉ có STL**. Phải vẽ lại các chi tiết chứa servo trước khi in cho ứng viên khác. Chi tiết vẽ lại vẫn chịu giấy phép phi thương mại, share-alike của mô hình 3D upstream. (§1.0)

## Phase 2 — Mô phỏng tải
- [ ] 🔴 **Chạy Phase 2 trước khi mua đủ 15 servo.** Nếu tải tĩnh đã vượt khả năng servo thì phải đổi servo, train lại policy không cứu được. (§2.5, §4.1.1)
- [ ] 🔴 MJCF của XGO đặt `forcerange` ±1.04 N·m. **Nới giới hạn này** khi tính tải động, nếu không mô-men bị cắt và nhìn như "đủ". (§2.3)
- [ ] 🟠 Chạy `static_torque.py` với `--foot-half` (kích thước đế chân đo trên CAD) để kiểm tra CoP. Tư thế có CoP ngoài đế chân thì loại. (§2.2)
- [ ] 🟠 Đứng 2 chân thì kiểm tra chéo bằng sim có tiếp xúc, vì nghiệm min-norm chưa chắc khớp thực tế. (§2.2)
- [ ] 🟡 τ_stall và ω₀ đem so phải là **số đo trên bàn thử**, đo ở áp pin thật khi có tải, không lấy từ trang bán hàng. (§2.4)
- [ ] 🟡 Ngưỡng $\tau_{peak}$/$\tau_{RMS}$ theo % stall là kinh nghiệm thực hành. Dự án phải tự chốt. (§2.3)

## Phase 3 — Phân tích I/O
- [ ] 🟠 Xác định rõ policy cần gì (R1–R7) trước khi chọn phương án. Phương án C không chỉnh được PD. (§3.1, §3.4)
- [ ] 🟡 Thông số HD1910 lấy từ datasheet nhà sản xuất do XGO chép lại (±10%), dự án chưa tự đo. Bảng thanh ghi (vận tốc, tải, dòng) chưa tra. Một trang nhà bán ghi "10 kg·cm", lệch với datasheet. (§3.2, README §6.3)
- [ ] 🟡 Bảng linh kiện bo zin ở §4.3.1 lấy từ bài reverse-engineering **MG995**, không phải MG92B. Tháo 1 MG92B của dự án để đối chiếu MCU, cầu H, transistor và LDO trước khi chọn phương án B hoặc mua đủ 15 con. (§4.3.1, §4.3.3)
- [ ] 🟡 Giá HD1910 về VN, so với tổng chi phí phương án độ (đã cộng bo driver, pin, MCU), mới biết có tiết kiệm thật không. (§3.4, §6.1)

## Phase 4 — Độ chế & kiểm thử servo
- [ ] 🔴 **Cảm biến dòng + bù áp pin** cho từng kênh. Giới hạn duty cố định không phải giới hạn dòng; pin đầy $8.4\text{V}$ × $80\%$ là quá áp thường trực. (§4.1.1)
- [ ] 🔴 **Hiệu chuẩn $K_{\text{ADC}}$ + offset từng servo**, không dùng $4096/\pi$. (§4.5.1)
- [ ] 🔴 **Trục giả dùng chốt thép h6 / ốc vai**, không dùng ren M3 lọt vòng bi. (§4.1.2, §6.1)
- [ ] 🔴 **Chừa khe hở chống bó khớp** ở gối phụ, và đo dòng không tải lại sau khi lắp khung. (§4.1.2, §4.5.2)
- [ ] 🔴 *(Phương án B)* **Firmware cấm `DRV_A` và `DRV_B` cùng mức cao**, có dead time khi đảo chiều và điện trở kéo xuống trên mỗi đường kích. Sai là chập cầu H. (§4.3.4, B2/B6)
- [ ] 🔴 *(Phương án B)* **Tra áp vào tối đa của LDO và Vds/Vgs của MOSFET zin** trước khi cắm pin 2S. (§4.3.3)
- [ ] 🔴 *(Phương án C)* Bo zin định mức 5.0–6.6V, **không cấp thẳng 2S**. (§4.4)
- [ ] 🟠 **Chốt MCU trước khi hàn servo.** A: 15 ADC dùng được thật + 15 cầu H + 15 kênh dòng. B: 30 PWM 3.3V + 15 ADC (+15 ADC dòng). Cẩn thận với MCU có ADC kém, ví dụ ESP32: ADC2 xung đột khi bật WiFi, ADC phi tuyến. (§6.1, §4.3.2)
- [ ] 🟠 Rail cấp chiết áp = VREF của ADC (ratiometric). (Bước A4)
- [ ] 🟠 Xoắn đôi dây motor; PWM $\geq 20\text{ kHz}$ (phương án B: chỉ khi tầng kích zin chịu được, §4.3.3); lấy mẫu ADC đồng bộ tâm PWM. (Bước A3)
- [ ] 🟠 Cố định chế độ brake/coast của cầu H giữa System ID và chạy thật. (Bước A3, §4.5.3)
- [ ] 🟠 Thử chiều quay bằng áp thấp, nhấp ngắn; firmware có watchdog chống phản hồi dương. (Bước A5)
- [ ] 🟠 Đo dòng không tải bằng cách chạy **vòng kín**, không cấp DC thẳng vào motor. (§4.5.2)
- [ ] 🟠 *(Phương án B)* Đo tần số PWM gốc và thời gian tắt P-FET trước khi chọn tần số PWM; xác nhận cầu H chỉ coast hay có brake. (§4.3.3)
- [ ] 🟡 Dòng không tải baseline, backlash: đo trên servo mẫu thay cho số ước lượng. (§4.1.3, §4.5.2)

## Phase 5 — Train policy & mô phỏng
- [ ] 🔴 **Domain Randomization viết trong code train**, có random latency và `armature`. (§5.2)
- [ ] 🔴 Giới hạn mô-men trong sim lấy theo **số đo thật**, có giới hạn phụ thuộc vận tốc. Mỗi ứng viên có file BAM riêng, không dùng `1910_m6.json` cho servo khác. (§5.1)
- [ ] 🔴 Không dùng lại policy của XGO hoặc Microduck cho robot đã đổi servo. Phải train lại. (§5)
- [ ] 🟠 Chế độ brake/coast trong sim khớp với phần cứng. (§5.1, §4.3.3)
- [ ] 🟠 Hệ số lọc $\alpha$ tính lại theo $\Delta t$ mỗi khi đổi tần số vòng lặp. (§5.2)
- [ ] 🟠 Kiểm tra lại tải khi chạy policy, không chỉ khi chạy gait mẫu. (§5.3)
- [ ] 🟡 Dải `frictionloss`/`damping` thu hẹp theo số đo System ID. (§5.2, §4.5.3)

## Phase 6 — Phần cứng & chạy thật
- [ ] 🔴 Treo robot và giới hạn dòng khi chạy lần đầu; kiểm tra dấu và offset từng khớp so với sim. (§6.3)
- [ ] 🟠 Căn horn để tư thế đứng nằm giữa hành trình chiết áp. Lệch 1 răng spline là mất dải một phía. (§6.2, Bước A2)
- [ ] 🟠 Dây `VBAT`/`PGND` chung cả chi chọn tiết diện theo dòng stall đo được, không dùng cỡ dây tín hiệu. (§4.3.5)
- [ ] 🟠 Cân lại chi tiết in thật; lệch so với MJCF thì chạy lại Phase 2. (§6.2)
- [ ] 🟡 Cập nhật giá BOM khi mua; đơn giá hiện tại là ước tính. (§6.1)

---

← [Phase 6](Phase6_PhanCung_ChayThat.md)
