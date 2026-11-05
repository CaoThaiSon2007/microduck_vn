# PHASE 4 — PHƯƠNG ÁN KHẮC PHỤC: ĐỘ CHẾ SERVO MG92B

[README](README.md) · [Phase 1 – CAD](Phase1_CAD_HocServo.md) · [Phase 2 – Mô phỏng tải](Phase2_MoPhong_TaiServo.md) · [Phase 3 – Phân tích I/O](Phase3_PhanTich_IO.md) · [Phase 4 – Độ chế](Phase4_PhuongAn_DoChe.md) · [Phase 5 – Train](Phase5_Train_Policy.md) · [Phase 6 – Phần cứng & chạy thật](Phase6_PhanCung_ChayThat.md) · [Checklist](CHECKLIST.md)

---

> **Đầu vào:** phương án được chọn ở [Phase 3](Phase3_PhanTich_IO.md) (§3.4).
> **Đầu ra:** servo đã độ qua bàn thử (§4.5), cùng thông số actuator đo được (§4.5.3) để đưa vào [Phase 5](Phase5_Train_Policy.md).
>
> Phương án A, B, C khác nhau ở phần điện. §4.1 (cơ khí và giới hạn mô-men) và §4.5 (kiểm thử) dùng chung cho cả ba.

## 4.1. Ba "tử huyệt" của xác MG92B và giải pháp chung

Để xác MG92B chịu được tải động và chạy được policy Reinforcement Learning, quá trình độ chế phải có 3 nâng cấp bắt buộc dưới đây. Mô-men **cần đạt** không lấy theo servo tham chiếu nào, mà là tải tính ra từ CAD ở **Phase 2**. Mốc so sánh là HD1910 của XGO-Duck. Theo datasheet nhà sản xuất (do XGO chép lại, ±10%), ở $6\text{V}$: stall $12\text{ kgf}\cdot\text{cm} \approx 1.18\text{ N}\cdot\text{m}$, rated $3.0\text{ kgf}\cdot\text{cm} \approx 0.29\text{ N}\cdot\text{m}$. Dự án chưa tự đo.

### 4.1.1. Tử huyệt 1: Thiếu mô-men xoắn (MG92B $\approx 0.35\text{ N}\cdot\text{m}$ danh định) $\rightarrow$ Giải pháp "Direct H-Bridge Overvolting + Current Limiting"
* **Nguyên lý:** bo zin của MG92B gồm PIC12F675 và một cầu H làm từ MOSFET rời (xem §4.3.1), định mức nguồn $5.0 - 6.6\text{V}$, stall $3.1 / 3.5\text{ kgf}\cdot\text{cm}$ ở $5 / 6\text{V}$ (trang TowerPro, xem [Nguồn tham khảo](README.md#6-nguồn-tham-khảo)).
  * Phương án A: tháo cả bo và dẫn thẳng 2 cực motor (`M+`, `M-`) về **Centralized Driver Board**.
  * Phương án B: giữ cầu H zin.
  * Cả hai phương án đều cấp nguồn motor trực tiếp từ **pin 2S** ($7.4\text{V}$ danh định, $8.4\text{V}$ khi đầy).
* **Tính toán an toàn:**
  * Ước lượng mô-men kẹt (stall) tỉ lệ tuyến tính theo điện áp hiệu dụng đặt lên motor:
    $$\tau_{\text{peak}} \approx 0.35 \times \frac{7.4}{6.0} \approx 0.43\text{ N}\cdot\text{m} \quad (\text{ở } 7.4\text{V};\ \approx 0.49\text{ N}\cdot\text{m ở } 8.4\text{V})$$
  * ⚠️ **Kết luận thẳng:** kể cả khi quá áp, MG92B vẫn **thấp hơn nhiều** so với HD1910 mà khung XGO được thiết kế cho. Kết luận đạt hay không phải theo **Phase 2**:
    * Nếu $\tau_{\text{peak}}$, $\tau_{\text{RMS}}$ cần thiết nằm dưới ngưỡng tính theo torque **đo thật** (§4.5.3, §2.4): khai báo giới hạn đó vào MuJoCo rồi train policy.
    * Nếu **tải tĩnh** (§2.2) đã vượt khả năng servo: train lại policy **không cứu được**, vì robot không đứng nổi. Khi đó phải đổi servo cho các khớp đó hoặc sửa hình học chân.
* **Bẫy "giới hạn duty" (lỗi đã mắc trong bản trước):**
  * Giới hạn duty cố định $80\%$ **không phải giới hạn dòng**. Với pin $7.4\text{V}$: $80\% \to \approx 5.9\text{V}$ hiệu dụng ≈ áp zin, gần như không tăng lực. Với pin đầy $8.4\text{V}$: $80\% \to \approx 6.7\text{V}$ **liên tục** → quá áp thường trực, nhiệt $\propto V^2$ gấp $\approx 2$ lần so với $6\text{V}$.
  * Robot đứng yên = các khớp chân giữ tải ở trạng thái gần stall liên tục → đây mới là lúc cháy motor, không phải lúc bật nhảy.
* **Giải pháp đúng trên firmware:**
  1. **Bù điện áp pin:** đo $V_{\text{bat}}$ liên tục, tính $\text{duty} = V_{\text{target}} / V_{\text{bat}}$ để điện áp hiệu dụng không đổi khi pin tụt. Nếu không, gain cơ cấu chấp hành thay đổi theo mức pin → policy RL chạy sai.
  2. **Giới hạn dòng thật:** mỗi kênh có shunt hoặc driver có chân cảm biến dòng; firmware giới hạn dòng liên tục và cho phép dòng đỉnh ngắn hạn (ví dụ $< 200\text{ ms}$ cho Push-off), kèm bảo vệ nhiệt theo $I^2t$. Ngưỡng dòng cụ thể **đo thực tế** trên 1 servo mẫu trước khi chốt.

### 4.1.2. Tử huyệt 2: Trục đơn chịu mô-men uốn kém $\rightarrow$ Giải pháp "Dual-Bearing U-Bracket (Khung chữ U 2 gối đỡ)"
* **Nguyên lý:** Không bao giờ lắp chân Microduck theo kiểu gá lệch 1 bên (Cantilever). Toàn bộ 10 khớp chân phải được kẹp giữa khung chữ U in 3D.
* **Thiết kế cơ khí trên CAD (SolidWorks):**
  1. Tại **mặt đáy vỏ nhựa của MG92B**, xác định chính xác tâm của trục bánh răng chính (Output Shaft) chiếu xuống đáy vỏ.
  2. Thiết kế nắp đáy in 3D thay thế nắp đáy zin của MG92B, tích hợp **chốt thép $\Phi 3$ h6 hoặc ốc vai thân trơn** đồng tâm với trục chính. ⚠️ Không dùng phần ren ốc M3 làm trục lọt vòng bi.
  3. Trên càng sau của khung chữ U (U-Bracket), tạo hốc lắp **vòng bi MR63ZZ ($3\times 6\times 2.5\text{ mm}$)**.
  4. Khi lắp servo vào khung, mặt trước bắt vào đĩa Servo Horn, mặt sau lọt vào lòng vòng bi MR63ZZ. Lực bẻ ngang (Radial/Bending Load) khi chân dậm đất được **chia** giữa trục ra và gối phụ (dầm 2 gối) — giảm mạnh mô-men uốn lên trục MG92B nhưng **không triệt tiêu $100\%$**.
* ⚠️ **Lưu ý bắt buộc:**
  * **Số răng horn:** kiểm tra spline thực tế của MG92B trước khi mua horn / vẽ CAD. $25\text{T}$ là spline servo cỡ standard (loại MG996R); servo micro cỡ MG9x thường là $20\text{T}/21\text{T}$.
  * **Bó khớp do lệch tâm:** "đồng tâm tuyệt đối" khi khoan tay/in 3D là không thực tế. Trục đỡ 2 đầu mà lệch tâm sẽ bó cứng → ma sát và dòng tăng vọt. Chừa khe hở hướng kính nhỏ cho ổ vòng bi hoặc làm gối hơi mềm, và **đo lại dòng không tải sau khi lắp vào U-bracket** (§4.5.2).

### 4.1.3. Tử huyệt 3: Độ rơ bánh răng (Backlash — ước lượng $\sim 1.5^\circ$, cần đo thực tế) & Ma sát tĩnh $\rightarrow$ Giải pháp "Cơ khí + Domain Randomization"
* **Xử lý phần cứng:**
  * Mở nắp hộp số MG92B, vệ sinh lớp mỡ đặc rẻ tiền (thường gây dính răng ở tốc độ thấp) và bôi một lớp mỏng **mỡ PTFE (Teflon)**.
  * Chêm một vòng đệm nhựa mỏng (Shim washer $0.1 - 0.2\text{ mm}$) vào trục bánh răng trung gian nếu phát hiện bánh răng bị rơ dọc trục.
* **Xử lý phần mềm (lọc vận tốc, Domain Randomization):** xem §5.2 ở [Phase 5](Phase5_Train_Policy.md).

---

## 4.2. Phương án A: tháo cả bo zin (SOP 6 bước)

Tham khảo đã có người làm trên chính MG92B: [pat92fr — "Smarter Micro Servo (SMS) MOD"](https://hackaday.io/project/176678) ([hướng dẫn](https://hackaday.io/project/176678/instructions)). Bài này mở vỏ, rồi hàn 2 dây ra motor và 3 dây ra chiết áp.

> **Biến thể A′: driver nằm trong từng servo (theo SMS MOD).** Vẫn tháo bo zin như các bước dưới đây, nhưng không kéo `M+`/`M−` về bo trung tâm. Thay vào đó, mỗi servo có một bo nhỏ riêng.
> * **Linh kiện theo nguồn:**
>   * MCU [STM32G431KB](https://www.st.com/en/microcontrollers-microprocessors/stm32g431kb.html) (Cortex-M4, 150 MHz).
>   * Driver [DRV8872](https://www.ti.com/lit/ds/symlink/drv8872.pdf) ở chế độ PWM có giới hạn dòng, đặt 1 A.
>   * Shunt 0.33 Ω, tín hiệu qua op-amp nội (PGA ×8) vào ADC 12-bit.
>   * Chiết áp zin giữ làm cảm biến vị trí tuyệt đối.
>   * Cấp thẳng LiPo 2S (6.5–10 V).
> * **Ưu điểm:** dây về thân chỉ còn bus truyền thông và nguồn, giống kiến trúc HD1910 / XGO. Đáp ứng G1–G5 (§3.4).
> * **Cần thêm:**
>   * Thiết kế và gia công 15 bo vừa lọt thân MG92B.
>   * Viết firmware vòng PD + giao thức bus.
>   * Kiểm tra bo SMS MOD có công bố file thiết kế và giấy phép không trước khi dùng lại.
> * Các bước A1, A3 (tụ 104, xoắn dây motor ngắn trong vỏ), A5, A6 vẫn áp dụng. Bước A4 (gom dây theo chi) được thay bằng đi dây bus.

Thực hiện lần lượt trên 1 con servo mẫu để kiểm tra trước khi làm hàng loạt cho 14 con còn lại:

#### Bước A1: Kiểm tra sống (Pre-flight Check) & Đưa về góc giữa ($90^\circ$)
1. Cắm MG92B còn zin vào mạch test servo, cấp xung $1500\ \mu\text{s}$ để trục về đúng vị trí trung tâm ($90^\circ$ - giữa hành trình của chiết áp).
2. Dùng bút dạ đánh dấu một vạch thẳng hàng giữa trục đồng và vỏ nhựa để làm mốc Zero vật lý.

#### Bước A2: Tháo vỏ và loại bỏ bo mạch PWM zin
> Phương án thay thế: giữ bo zin, chỉ gỡ PIC và dùng lại cầu H có sẵn → xem **§4.3**.

1. Tháo 4 ốc dài ở mặt đáy MG92B, rút nắp đáy ra.
2. Dùng mỏ hàn nhả mối hàn tại **2 chân động cơ DC** và **3 chân chiết áp (Potentiometer)** để lấy bo mạch điều khiển PWM màu xanh ra ngoài (giữ lại bo mạch này nếu muốn tận dụng các linh kiện SMD).
3. **Lưu ý về chốt chặn cơ khí (Mechanical Stop):**
   * **Nên giữ nguyên chốt chặn trên bánh răng chính** đối với 10 khớp chân để bảo vệ chiết áp không bị quay quá giới hạn khi code lỗi — **với điều kiện** dải khớp trong MJCF/URDF (`range`) thật sự nằm gọn trong hành trình cơ của servo. ⚠️ Kiểm tra `range` của từng khớp trước (đầu gối, hông pitch thường cần gập sâu hơn $\pm 60^\circ$, ví dụ khi ngồi xuống/đứng dậy).
   * Khi cắm horn, căn sao cho **tư thế đứng nằm giữa hành trình chiết áp**. Mỗi răng spline lệch khoảng $15^\circ - 18^\circ$ → cắm lệch 1 răng là mất dải một phía.
   * Riêng khớp `Head_Yaw` (xoay cổ trái/phải), nếu muốn xoay rộng hơn, có thể dùng kìm cắt nhựa cắt bỏ vấu chặn trên bánh răng chính.

#### Bước A3: Xử lý chống nhiễu điện từ (EMI Filtering) tại động cơ
1. Hàn trực tiếp 1 tụ gốm **104 ($0.1\ \mu\text{F}$)** nối ngang qua 2 cực `M+` và `M-` của động cơ DC ngay sát đáy motor.
2. *Tác dụng:* Giảm tia lửa điện chổi than khi băm xung PWM tần số cao từ bo mạch trung tâm, giúp tín hiệu Analog đọc từ chiết áp đi cạnh bên bớt nhiễu (ADC Jitter).
3. ⚠️ Tụ 104 **không đủ một mình**. Bắt buộc kết hợp:
   * **Xoắn đôi** 2 dây motor `M+`/`M-` suốt chiều dài bó dây (dây motor và dây pot đi chung ống gen là nguồn nhiễu chính).
   * PWM motor $\geq 20\text{ kHz}$; **lấy mẫu ADC đồng bộ với tâm chu kỳ PWM** (lúc dòng ít chuyển mạch nhất).
   * **Chọn cố định chế độ giảm dòng của cầu H** (slow decay/brake hoặc coast) — chế độ này làm đổi động lực học khớp (hãm back-EMF), nên phải giữ nguyên giữa lúc System ID và lúc chạy thật.

#### Bước A4: Đi dây theo cấu trúc "Gom Bus Theo Chi" (Limb-Harness Wiring)
Thay vì kéo $15 \times 5 = 75$ sợi dây về bụng vịt, ta gom đường nguồn `3.3V_ADC` và `AGND` của các chiết áp theo từng cụm chi (Chân trái 5 khớp, Chân phải 5 khớp, Cổ 5 khớp):

* **Tại mỗi Servo:** Hàn ra 1 bó dây ngắn gồm:
  * **2 dây Silicon 26AWG (Đỏ / Đen):** Cực `M+` và `M-` của động cơ DC.
  * **1 dây Silicon 28AWG (Vàng hoặc Trắng):** Chân giữa (**Wiper / Signal**) của chiết áp.
  * **2 dây Silicon 28AWG (Cam / Xanh):** Chân `VCC (3.3V)` và `GND` của chiết áp (2 dây này được nối bắc cầu Daisy-chain từ servo mắt cá $\rightarrow$ đầu gối $\rightarrow$ háng trên cùng 1 chân).
* **Số lượng dây đi qua khớp háng mỗi chân về Bo mạch chủ:**
  $$\text{Tổng số dây 1 chân} = (5 \times 2\text{ dây Motor}) + (5 \times 1\text{ dây Wiper}) + 2\text{ dây nguồn Pot chung} = \mathbf{17\text{ sợi}}$$
  *(Bọc gọn trong 1 ống gen lưới xác rắn $\Phi 6\text{ mm}$ cực kỳ thẩm mỹ và dẻo dai).*
* ⚠️ **Rail `3.3V_ADC` cấp cho chiết áp phải chính là điện áp tham chiếu (VREF) của ADC trên MCU** (đo kiểu ratiometric). Không dùng một LDO riêng cho pot — góc đọc sẽ trôi theo nhiệt độ và tải.

#### Bước A5: Quy ước chiều quay và chiều tăng ADC (Polarity Standardization)
1. **Rất quan trọng:** Khi cấp điện áp dương vào `M+` (và GND vào `M-`), nếu trục servo quay theo chiều kim đồng hồ (CW), thì điện áp ở chân giữa chiết áp (`Wiper`) **phải tăng dần** từ $0\text{V} \rightarrow 3.3\text{V}$.
2. Nếu thấy điện áp chiết áp giảm khi cấp dương vào `M+`, phải **đảo lại 2 dây bìa (`3.3V` và `GND`) của chiết áp** (hoặc đảo 2 dây `M+`/`M-`) ngay lúc hàn để cả 15 con servo có cùng một chiều quy ước vật lý (Positive PWM $\rightarrow$ Positive $\Delta \text{ADC}$). Điều này giúp tránh hiện tượng **phản hồi dương (Positive Feedback)** làm servo quay vọt kịch kim gãy răng ngay lần đầu bật nguồn chạy PID!
3. ⚠️ Khi thử chiều quay (chưa có vòng phản hồi): chỉ cấp **áp thấp, nhấp ngắn** — cấp lâu sẽ đâm vào chốt chặn và kẹt motor.
4. **Lớp bảo vệ thứ hai trên firmware (watchdog):** nếu sai số vị trí tăng theo đúng chiều đang đẩy PWM trong một khoảng thời gian ngắn → cắt PWM khớp đó và báo lỗi. Không chỉ dựa vào quy ước đi dây.
5. Dấu (sign) và offset của từng khớp so với trục khớp trong MuJoCo (khớp trái/phải đối xứng) lưu trong **bảng cấu hình firmware**, không xử lý bằng cách đảo dây.

#### Bước A6: Đóng vỏ đáy có tích hợp gối đỡ lưng (Dual-Support Backplate)
1. Khoét lỗ luồn dây gọn gàng ở hông vỏ nhựa, thắt một nút gút nhỏ bên trong hoặc nhỏ keo nhiệt/keo AB chống đứt mối hàn khi dây bị kéo căng (Strain Relief).
2. Lắp nắp đáy (đã gắn chốt trục giả $\Phi 3\text{ mm}$ đồng tâm với trục chính) và siết chặt 4 ốc.

---

## 4.3. Phương án B: gỡ PIC, giữ lại cầu H trên bo zin (thay cho Bước A2–A4)

> **Trạng thái:** đề xuất (05/11/2026), chưa thử trên servo thật. Đây là phương án thay thế cho SOP §4.2 (phương án A). Bước A1, A5 và §4.5 giữ nguyên. Riêng Bước A6: bo zin vẫn nằm trong vỏ, nên nắp đáy in 3D phải chừa đủ chỗ cho bo và dây ra.

### 4.3.1. Cơ sở
Nguồn: [Will — "127 TowerPro Servos, one I2C interface"](https://hackaday.io/project/6748-127-towerpro-servos-one-i2c-interface), Hackaday.io.

> ⚠️ Bài này reverse-engineer **TowerPro MG995** (servo cỡ standard), **không phải MG92B**. Tác giả chỉ ghi "và các dòng anh em". Bo của MG92B có thể giống về nguyên lý nhưng **chưa có bằng chứng**. Phải tháo 1 MG92B của dự án để đối chiếu (§4.3.3, mục 5).

Bo zin của MG995 theo bài trên:

| Thành phần | Linh kiện (theo nguồn) |
|---|---|
| MCU | PIC12F675. Mã chip bị cạo; lúc đầu tác giả đoán là PIC12F510, sau đó PICkit2 tự nhận diện qua ICSP là PIC12F675 |
| Dao động | Ceramic resonator 8 MHz, nối giữa pin 2 và pin 3 của PIC |
| Driver công suất | 2 gói SOIC-8 chứa MOSFET, ghép thành full H-bridge. Tác giả **đoán** là loại cặp N+P giống IRF7309, chưa xác nhận mã |
| Transistor phụ | 2 transistor 3 chân, theo tác giả dùng để **dịch mức** tín hiệu từ PIC |
| Nguồn MCU | LDO tuyến tính 3.3V |
| Phản hồi vị trí | Chiết áp, đưa vào ADC của PIC |
| Khác | Mã các IC SOIC-8 đều bị cạo. Có tụ trên pin 7 của PIC làm chậm tín hiệu PGD khi nạp ICSP |

Tham khảo thêm: [pat92fr — "Smarter Micro Servo (SMS) MOD"](https://hackaday.io/project/176678/instructions) hack **chính MG92B**. Bài này mở vỏ và hàn 2 dây ra motor, 3 dây ra chiết áp (cùng hướng với phương án A, §4.2), nhưng phần hướng dẫn không ghi linh kiện của bo zin.

Cầu H làm bằng **linh kiện rời**, tách khỏi MCU. Vậy có thể **bỏ riêng PIC, giữ lại cầu H**, rồi điều khiển cầu H trực tiếp từ bo trung tâm.

### 4.3.2. So sánh với phương án A (tháo cả bo)

| | Phương án A (§4.2) | **Phương án B** |
|---|---|---|
| Cầu H | 15 cầu H trên bo trung tâm | Dùng cầu H có sẵn trong từng servo |
| Bo trung tâm cần | 30 PWM + 15 ADC + 15 cầu H (+15 ADC dòng) | **30 PWM 3.3V + 15 ADC** (+15 ADC dòng nếu làm shunt, xem §4.3.4, bước B5) |
| Tản nhiệt công suất | Tập trung ở bụng | Phân tán ở từng servo, giống servo zin |
| Chế độ cầu H | Tự chọn brake/coast | Phụ thuộc cách nối gate, có thể **chỉ có coast** (xem §4.3.3) |
| Tần số PWM | Tự chọn, ≥ 20 kHz | Bị giới hạn bởi tầng dịch mức, **phải đo** |
| Số dây mỗi servo | 5 (M+, M−, wiper, pot VCC, pot GND) | 7 (DRV_A, DRV_B, wiper, pot VCC, pot GND, VBAT, PGND), 8 nếu có ISENSE. Nguồn pot và nguồn công suất nối daisy-chain theo chi (xem §4.3.5) |
| Rủi ro chính | Chi phí và kích thước bo driver | Linh kiện zin chưa rõ thông số, chập cầu H nếu firmware lỗi |

Gợi ý MCU (chưa chốt): STM32G474, hoặc chia 3 node, mỗi node lo 1 chi 5 khớp. Phương án A cũng dùng được hai lựa chọn này. Với phương án B, phần công suất không còn nằm trên bo trung tâm.

### 4.3.3. Ràng buộc kỹ thuật phải xác minh trước khi độ

1. **Sơ đồ kích gate.** Truy 4 chân gate của 2 IC MOSFET để biết mỗi chân PIC đang kích gì. Hai trường hợp:
   * **Kích chéo** (hay gặp): mỗi chân bật cùng lúc N-FET dưới của nhánh này và P-FET trên của nhánh kia. Khi đó:
     * **Cấm kéo 2 đường lên mức cao cùng lúc**, vì sẽ chập Vbat xuống GND qua cả 2 nhánh.
     * **Không có chế độ brake.** Muốn brake phải bật cả 2 N-FET dưới, nhưng ở cách nối này thì 2 P-FET cũng bật theo. Cầu H chỉ chạy được kiểu **coast**. Mô hình damping trong MuJoCo và System ID phải theo chế độ coast.
   * **Kích riêng từng nhánh:** cần 4 đường điều khiển cho mỗi servo và phải tự chèn dead time trong mỗi nhánh. Không khuyến nghị.
2. **Tần số PWM tối đa.** Nếu P-FET được tắt bằng điện trở kéo lên, sườn tắt sẽ chậm. Đẩy PWM lên cao có thể làm P-FET nóng, vì nó nằm lâu trong vùng tuyến tính. Lấy tần số PWM gốc của PIC làm mốc an toàn, rồi tăng dần và theo dõi nhiệt. Mục tiêu ≥ 20 kHz ở Bước A3 **chỉ áp dụng khi đo thấy tầng kích chịu được**.
3. **Mức logic.** PIC chạy ở 3.3V, nên N-FET trên bo đã được kích bằng 3.3V. MCU trung tâm 3.3V dùng trực tiếp được. Vẫn phải đo dạng sóng gate để chắc chắn N-FET mở hoàn toàn.
4. **Áp chịu đựng khi chạy 2S (8.4V):**
   * **LDO 3.3V:** nhiều LDO cỡ nhỏ chỉ chịu được áp vào khoảng 6V. Tra mã LDO. Nếu không đủ thì gỡ LDO (sau khi bỏ PIC, LDO chỉ còn nuôi chiết áp, mà chiết áp sẽ chuyển sang rail VREF ở bước B4 của §4.3.4).
   * **IC MOSFET:** tra Vds và Vgs tối đa. P-FET phía trên chịu Vgs xấp xỉ −Vbat khi dẫn.
   * **Transistor dịch mức:** tra Vce tối đa.
5. **Mạch đang có:** bài nguồn ở §4.3.1 reverse-engineer **MG995**, không phải MG92B. Bo MG92B có thể dùng MCU, MOSFET và LDO khác. **Tháo 1 con, chụp mã IC, đối chiếu bảng §4.3.1 trước khi mua đủ 15 con.**

### 4.3.4. SOP phương án B

**Bước B0: Đo trên servo còn zin (trước khi gỡ bất cứ thứ gì)**
1. Cấp nguồn 5–6V (trong dải định mức 5.0–6.6V), cấp xung servo. Dùng scope đo 2 chân PIC nối vào tầng công suất. Ghi lại tần số PWM, mức logic, dạng xung khi đảo chiều (có khoảng chết không).
2. Đo áp 2 đầu chiết áp để xác nhận chiết áp được cấp từ LDO 3.3V.
3. Đo dòng không tải để có baseline cho §4.5.2.

**Bước B1: Truy mạch và tra datasheet**
1. Đọc mã 2 IC MOSFET, 2 transistor và LDO. Tra datasheet theo các mục ở 3B.3.
2. Đối chiếu sơ đồ chân PIC12F675 (DIP/SOIC-8): pin 1 VDD, pin 8 VSS, pin 2 GP5/OSC1, pin 3 GP4/OSC2, pin 4 GP3 (chỉ vào), pin 5–7 GP2/GP1/GP0 (có ADC).
   * Dự đoán: pin 2–3 nối resonator, pin 4 nhận xung lệnh, pin 5–7 gồm 1 chân đọc chiết áp và 2 chân kích cầu H. **Phải đo thông mạch để xác nhận.**
3. Vẽ lại sơ đồ nguyên lý phần công suất, lưu vào thư mục dự án để làm chuẩn cho 14 con còn lại.

**Bước B2: Gỡ PIC**
1. Khò gỡ PIC. Giữ nguyên resonator, hoặc gỡ luôn vì không còn dùng.
2. Thêm **điện trở kéo xuống** (ví dụ 10 kΩ, chọn lại theo sơ đồ đã truy) từ mỗi pad kích cầu H xuống GND ngay trên bo servo. Lý do: khi MCU trung tâm đang reset hoặc chưa cấu hình chân, đường kích bị thả nổi và có thể tự bật cầu H.

**Bước B3: Hàn dây ra**
* 2 dây tín hiệu kích cầu H (`DRV_A`, `DRV_B`) hàn vào pad cũ của PIC.
* 1 dây wiper hàn vào pad ADC cũ của PIC (hoặc thẳng vào chân giữa chiết áp).
* 2 dây nguồn công suất `VBAT` / `PGND` giữ ở vị trí dây nguồn zin.
* Giữ tụ 104 trên motor, xoắn đôi 2 dây kích cùng 1 dây GND nếu đi xa (theo Bước A3).

**Bước B4: Chuyển chiết áp sang rail VREF**
1. Cắt đường cấp từ LDO vào đầu trên của chiết áp.
2. Cấp chiết áp từ rail `3.3V_ADC` = VREF của bo trung tâm (ratiometric, như Bước A4).
3. Chân GND của chiết áp nối về `AGND`. Không đi chung với `PGND` của motor trên suốt bó dây. Nếu trên bo zin GND chiết áp đã dính với GND công suất, chỉ được nối AGND và PGND tại **một điểm** trên bo trung tâm.

**Bước B5 (tùy chọn, nên làm): Shunt đo dòng**
* Nếu source của 2 N-FET dưới chung một nút GND, cắt mạch tại đó và chèn điện trở shunt. Chọn giá trị theo dòng stall đo được và dải ADC.
* Kéo thêm 1 dây `ISENSE` về bo trung tâm (qua RC lọc). Đây là cách đáp ứng mục 🔴 "cảm biến dòng" của checklist mà không cần cảm biến dòng trên bo trung tâm.

**Bước B6: Firmware**
1. Logic điều khiển theo kiểu IN/IN: `DRV_A` = PWM, `DRV_B` = 0 → quay một chiều. Đổi vai trò → quay chiều ngược lại. Cả hai bằng 0 → coast.
2. **Khóa phần mềm:** không bao giờ cho `DRV_A` và `DRV_B` cùng mức cao, kể cả khi lỗi. Khi đổi chiều, tắt cả hai rồi chờ một khoảng dead time (đo theo thời gian tắt P-FET ở Bước B0/B1) mới bật bên kia. Nếu MCU có timer với dead-time/complementary output, cấu hình phần cứng để loại trừ hai kênh này.
3. Lấy mẫu ADC đồng bộ với PWM như Bước A3.

**Bước B7: Thử lần đầu**
* Nguồn đa năng giới hạn dòng thấp, áp thấp, nhấp ngắn (như Bước A5). Kiểm tra chiều quay và chiều tăng ADC.
* Sờ nhiệt IC MOSFET sau vài phút giữ tải ở tần số PWM định dùng.
* Đo lại dòng không tải, so với baseline ở Bước B0.

### 4.3.5. Đi dây theo chi
Mỗi servo: `DRV_A`, `DRV_B`, `WIPER`, (`ISENSE`), cộng nguồn công suất. Nguồn chiết áp `3.3V_ADC`/`AGND` và nguồn công suất `VBAT`/`PGND` đều có thể nối Daisy-chain theo từng chi.

$$\text{Số dây 1 chân} = 5 \times (2\ \text{DRV} + 1\ \text{WIPER}) + 2\ \text{nguồn pot} + 2\ \text{nguồn công suất} = \mathbf{19\text{ sợi}}\ (24\text{ nếu có ISENSE})$$

* Dây `VBAT`/`PGND` chung cả chi phải chọn tiết diện theo tổng dòng của 5 servo (lấy dòng stall đo được ở §4.5.3), không dùng cỡ 28AWG như dây tín hiệu.
* Kiểm tra chỗ luồn bó dây qua U-bracket và khớp háng trước khi vẽ CAD.

---

## 4.4. Phương án C: giữ bo zin, chỉ hàn thêm dây chiết áp

> **Trạng thái:** ý tưởng (05/11/2026), chưa đánh giá chi tiết, chưa thử.

* **Cách làm:**
  * Giữ nguyên bo zin, PIC và cầu H. Vẫn điều khiển servo bằng xung servo RC như bình thường.
  * Hàn thêm 1 dây từ chân giữa (wiper) của chiết áp ra ADC của MCU trung tâm để đọc góc.
* **Đáp ứng:** chỉ có G1 (đọc góc), và G2 qua đạo hàm. Không đáp ứng G3, G4, G5 (§3.4).
* **Cần xác minh trước khi chọn:**
  1. Chiết áp đang được cấp từ LDO 3.3V trên bo zin (B0 ở §4.3.4). Rail này **khác VREF** của ADC trung tâm, nên phép đo không ratiometric và góc đọc có thể trôi. Có hai cách xử lý: đo thêm rail đó để bù, hoặc chấp nhận sai số.
  2. Nối GND giữa servo và bo trung tâm: dòng motor đi chung GND với tín hiệu wiper, nên phải kiểm tra nhiễu ADC.
  3. **Đo vòng điều khiển của PIC** (đáp ứng bước, độ trễ, deadband) đủ tốt để mô hình hóa trong MuJoCo. Đây là điều kiện để policy chạy được (§3.4).
  4. Bo zin định mức 5.0–6.6V, nên phải có nguồn hạ áp riêng cho servo. Không cấp thẳng 2S.

---

## 4.5. Kiểm thử & hiệu chuẩn từng servo sau khi độ (Benchmark & Calibration)

Trước khi lắp 15 servo lên khung in 3D của Microduck, từng servo sau khi độ phải vượt qua bài kiểm tra trên bàn test (Test Jig):

### 4.5.1. Kiểm tra tuyến tính chiết áp (Potentiometer Linearity Test)
   * Cấp $3.3\text{V}$ vào chiết áp, xoay trục qua các mốc $-60^\circ, 0^\circ, +60^\circ$.
   * Đọc giá trị ADC 12-bit ($0 - 4095$): Đảm bảo không có điểm nhảy vọt (Dead spot).
   * ⚠️ **Không dùng $K_{\text{ADC}} = 4096/\pi \approx 1300\text{ bước/rad}$.** Công thức đó giả định $180^\circ$ cơ khí quét hết $0 - 3.3\text{V}$, nhưng chiết áp servo có hành trình điện rộng hơn $180^\circ$, nên dải cơ chỉ dùng một phần dải ADC. Phải **đo $K_{\text{ADC}}$ và offset riêng cho từng servo** tại 3 mốc $-60^\circ, 0^\circ, +60^\circ$ (hồi quy tuyến tính) và lưu vào bảng hiệu chuẩn firmware.
### 4.5.2. Đo dòng không tải — đo 2 lần
   * Nguồn đa năng $6\text{V}$, giới hạn dòng $0.5\text{A}$, cấp cho tầng công suất.
   * **Không cấp DC thẳng vào motor để đo.** Chốt chặn vẫn còn, nên làm vậy servo sẽ đâm vào chốt và kẹt (xem Bước A5).
   * Cách đo đúng: chạy servo **vòng kín** qua lại trong hành trình, ví dụ sin $\pm 45^\circ$ chậm, rồi đo dòng trung bình.
   * **Lần 1:** servo rời, sau khi độ xong. **Lần 2:** sau khi đã lắp vào U-bracket có gối đỡ — để bắt lỗi bó khớp do lệch tâm (§4.1.2).
   * Ngưỡng dòng không tải chuẩn (bản trước ghi $80 - 150\text{ mA}$, ngưỡng lỗi $> 300\text{ mA}$ — **chưa có nguồn kiểm chứng**): đo trên servo zin mẫu để lấy baseline, sau đó so các servo đã độ với baseline. Dòng tăng rõ so với baseline $\rightarrow$ hộp số kẹt, nắp vỏ siết lệch hoặc gối đỡ lệch tâm, cần mở ra chỉnh lại.
### 4.5.3. Đo đạc thông số thực tế cho MuJoCo (Actuator System ID)
   * Dùng 1 servo đã độ gắn cánh tay đòn (ghi rõ chiều dài tay đòn) mang quả nặng chuẩn $100\text{g}$, chạy script phát sóng hình sin tần số biến thiên (Chirp signal) từ bo mạch điều khiển để thu thập dữ liệu $(u_{\text{PWM}}, V_{\text{bat}}, I, q, \dot{q})$.
   * Khớp các thông số: `kp`, `kv`, `frictionloss`, **`armature`**, và **giới hạn torque phụ thuộc vận tốc** (do back-EMF) — đưa vào MuJoCo trước khi huấn luyện chính sách bước đi.
   * Đo thêm: **độ rơ (backlash)** thực tế, **độ trễ** từ lúc gửi lệnh đến lúc khớp phản ứng, và **dòng stall** để chốt ngưỡng giới hạn dòng ở §4.1.1.
   * Giữ nguyên chế độ giảm dòng cầu H, tần số PWM và tần số vòng lặp PD giống hệt lúc chạy thật.

---

← [Phase 3](Phase3_PhanTich_IO.md) · [Phase 5](Phase5_Train_Policy.md) →
