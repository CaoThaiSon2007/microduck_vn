# MICRODUCK-VN — TÀI LIỆU KỸ THUẬT

[README](README.md) · [Phase 1 – CAD](Phase1_CAD_HocServo.md) · [Phase 2 – Mô phỏng tải](Phase2_MoPhong_TaiServo.md) · [Phase 3 – Phân tích I/O](Phase3_PhanTich_IO.md) · [Phase 4 – Độ chế](Phase4_PhuongAn_DoChe.md) · [Phase 5 – Train](Phase5_Train_Policy.md) · [Phase 6 – Phần cứng & chạy thật](Phase6_PhanCung_ChayThat.md) · [Checklist](CHECKLIST.md)

---

## 1. Bối cảnh
* Dự án làm robot vịt hai chân 15 DOF kiểu Microduck.
* **Cơ khí và điện tử theo XGO-Duck** ([LuwuDynamics/xgoduck_hardware](https://github.com/LuwuDynamics/xgoduck_hardware)), gồm 15× servo bus Feetech HD1910, Arduino UNO Q kèm board mở rộng Luwu, pin 18650 8.4V.
* **Thuật toán:** theo bản gốc Microduck của Pollen Robotics. Runtime ở [microduck](https://github.com/pollen-robotics/microduck). Phần RL ở [microduck_rl](https://github.com/pollen-robotics/microduck_rl): train PPO trên mjlab (MuJoCo Warp), mô hình actuator bằng BAM, có Domain Randomization, xuất ONNX chạy ở 50 Hz.
  * XGO-Duck tách nhánh từ đó thành [xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl). Nhánh này có sẵn MJCF/URDF của XGO-Duck và mô hình BAM cho servo 1910.
  * Danh sách đầy đủ ở [§6.1](#61-dự-án--repo-tham-khảo).
* **HD1910** (HD-1910-C001 / HD1910M): stall 9/12/15 kgf·cm và rated 2.2/3.0/3.7 kgf·cm ở 4.8/6/7.4V, sai số ±10%.
  * Nguồn: bảng thông số nhà sản xuất (bản A/0, ngày 07/09/2026), do XGO chép lại trong [docs/BOM.md](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/docs/BOM.md#servo-supplier-specification-and-runtime-configuration).
  * Dự án chưa tự đo các số này.

## 2. Đề bài
Servo là khoản đắt nhất trong BOM. Dự án cần trả lời:

> **Có servo nào rẻ hơn HD1910 mà vẫn đủ tải để robot đứng và đi được, và sau khi độ thì đủ tín hiệu vào/ra để train và chạy policy RL không?**

Ứng viên đang xét là TowerPro MG92B (và MG90S cho đầu). Theo số danh định, MG92B yếu hơn HD1910 nhiều và không vừa hốc servo 34×20×23 mm của XGO. Vì vậy phải sửa CAD và tính tải trước khi kết luận.

## 3. Cách tiếp cận
Đi qua 6 phase. Mỗi phase có đầu ra cụ thể, và ứng viên nào trượt ở phase nào thì dừng ở phase đó:

| Phase | Nội dung | Đầu ra / điều kiện qua phase | Trạng thái |
|---|---|---|---|
| [**1. Model lại CAD**](Phase1_CAD_HocServo.md) | Sửa hốc servo của khung XGO-Duck cho từng ứng viên, gán khối lượng thật, xuất MJCF | Mỗi ứng viên 1 biến thể CAD + MJCF | Chưa bắt đầu |
| [**2. Mô phỏng tải**](Phase2_MoPhong_TaiServo.md) | Tính tải tĩnh và tải động trên MuJoCo, so với servo đo thật | Danh sách ứng viên đạt tải → Phase 3 | Script đã chạy được trên MJCF XGO, phương pháp tĩnh đã kiểm chứng; chưa có kết quả tải (thiếu kích thước đế chân, quỹ đạo, servo đo thật) |
| [**3. Phân tích I/O**](Phase3_PhanTich_IO.md) | So tín hiệu vào/ra của ứng viên với HD1910 theo những gì policy cần, đề ra phương án khắc phục | Bảng thiếu hụt + phương án được chọn → Phase 4 | Có khung phân tích |
| [**4. Phương án độ chế**](Phase4_PhuongAn_DoChe.md) | Độ servo: A (tháo bo zin, cầu H ở bo trung tâm), A′ (bo thông minh riêng trong từng servo, theo SMS MOD), B (gỡ PIC, giữ cầu H), C (giữ bo zin, hàn thêm dây chiết áp); kiểm thử và System ID | Servo đã độ qua bàn thử + thông số actuator cho sim | A, B có SOP; A′ có thiết kế tham khảo; C mới là ý tưởng |
| [**5. Train policy & mô phỏng**](Phase5_Train_Policy.md) | Đưa mô hình actuator đo được vào MuJoCo, train policy, kiểm tra tải lúc chạy policy | Policy chạy ổn trong sim với giới hạn servo thật | Chưa bắt đầu |
| [**6. Phần cứng & chạy thật**](Phase6_PhanCung_ChayThat.md) | Mua và gia công toàn bộ, lắp ráp, chạy thật | Robot đứng và đi ngoài đời | Có BOM nháp |

Các lỗi cần tránh được gom vào **[CHECKLIST.md](CHECKLIST.md)**, chia theo từng phase.

```
Phase 1 (CAD) → Phase 2 (tải) ─ trượt → đổi ứng viên / sửa hình học chân → Phase 1
                     │ đạt
                     ▼
              Phase 3 (I/O) → Phase 4 (độ chế + System ID) → Phase 5 (train) → Phase 6 (chạy thật)
```

## 4. Quy ước trong bộ tài liệu
* **Đánh số mục:** `§N.x` là mục thuộc Phase N. Ví dụ §2.2 nằm ở Phase 2, §4.3.1 nằm ở Phase 4.
* **Số liệu:** chỉ dùng số đã đo hoặc có nguồn. Số lấy từ nhà bán hoặc nguồn ngoài chưa đối chiếu phải ghi rõ **"chưa kiểm chứng"**, và có một mục 🟡 tương ứng trong Checklist.
* **Phần mềm CAD:** chỉ dùng SolidWorks, cùng phần mềm XGO dùng để xuất khối lượng. Xuất URDF bằng `sw_urdf_exporter`.
* **Múi giờ:** GMT+7.

## 5. Thông số chung của robot

### 5.1. Sơ đồ phân bổ 15 khớp
* **Cụm Chân Trái (Left Leg - 5 DOF):** `L_Hip_Yaw`, `L_Hip_Roll`, `L_Hip_Pitch`, `L_Knee_Pitch`, `L_Ankle_Pitch`.
* **Cụm Chân Phải (Right Leg - 5 DOF):** `R_Hip_Yaw`, `R_Hip_Roll`, `R_Hip_Pitch`, `R_Knee_Pitch`, `R_Ankle_Pitch`.
* **Cụm Thân Trên / Cổ & Đầu (Head/Neck - 5 DOF):** `Neck_Pitch`, `Head_Pitch`, `Head_Yaw`, `Head_Roll`, `Left/Right_Antenna` (hoặc Mỏ).

### 5.2. Chuẩn điều khiển mục tiêu
* Policy RL (ONNX) gửi góc mục tiêu ở $50\text{ Hz}$, giống microduck_rl / xgoduck_rl.
* Vòng PD bám góc chạy bên dưới policy:
  * Với HD1910, vòng này nằm trong firmware servo (XGO đặt KP 6 / KD 20).
  * Với servo độ (A, A′, B), vòng này do MCU tự chạy. Mục tiêu $500\text{ Hz} - 1\text{ kHz}$ (Compliant PD Control).
* Tên khớp trong sơ đồ 5.1 là tên quy ước của tài liệu. Trong MJCF của XGO, khớp có tên `left_hip_yaw`, `left_knee`, `left_ankle`, `neck_pitch`… (xem §1.3).
* Hai con số này là yêu cầu đầu vào cho Phase 3 (servo phải cho phép làm được) và Phase 5 (sim phải chạy đúng tần số này).

## 6. Nguồn tham khảo
> Ghi chú cột "Trạng thái":
> * **Đã đọc:** nội dung trang đã được mở và đối chiếu trong quá trình làm tài liệu.
> * **Link xác nhận tồn tại:** mới kiểm tra link còn sống (05/11/2026), chưa đọc kỹ nội dung.
>
> Số liệu lấy từ trang nhà bán đều coi là **chưa kiểm chứng** cho tới khi đo.

### 6.1. Dự án / repo tham khảo
| Nguồn | Dùng cho | Trạng thái |
|---|---|---|
**Microduck bản gốc (Pollen Robotics): nguồn thuật toán**

| Nguồn | Dùng cho | Trạng thái |
|---|---|---|
| [pollen-robotics/microduck](https://github.com/pollen-robotics/microduck) | Runtime trên robot: vòng điều khiển 50 Hz chạy policy cho 15 servo, trên RK3566. Robot khoảng 25 cm, 800 g | Đã đọc README |
| [pollen-robotics/microduck_rl](https://github.com/pollen-robotics/microduck_rl) | Train policy: mjlab + PPO, BAM, Domain Randomization, mô phỏng backlash, xuất ONNX 50 Hz. Có các task Velocity, StandUp, SitStand… (Phase 5) | Đã đọc README |
| [Pollen Robotics — Microduck](https://pollen-robotics.com/microduck/), [press kit](https://pollen-robotics.com/microduck/press-kit/) | Trang sản phẩm, giá 399 USD | Đã đọc |

**XGO-Duck (LuwuDynamics): nguồn cơ khí, điện tử, và nhánh RL cho servo 1910**

| Nguồn | Dùng cho | Trạng thái |
|---|---|---|
| [LuwuDynamics/xgoduck_hardware](https://github.com/LuwuDynamics/xgoduck_hardware) | Cơ khí và điện tử. ⚠️ Cơ khí **chỉ có file STL** (thư mục `structure/`), không có CAD tham số (§1.2) | Đã đọc |
| [xgoduck_hardware — docs/BOM.md](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/docs/BOM.md) | BOM, **bảng thông số HD-1910-C001** của nhà sản xuất, gain KP/KD runtime | Đã đọc |
| [xgoduck_hardware — UPSTREAM.md](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/UPSTREAM.md) | XGO-Duck kế thừa những gì từ Microduck; lưu ý giấy phép mô hình 3D | Đã đọc |
| [LuwuDynamics/xgoduck_runtime_arduino](https://github.com/LuwuDynamics/xgoduck_runtime_arduino) | Runtime/firmware trên Arduino UNO Q | Link xác nhận tồn tại |
| [LuwuDynamics/xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl) | Nhánh RL từ microduck_rl. Có **MJCF/URDF XGO-Duck** (`src/mjlab_microduck/robot/xgoduck/`), khối lượng xuất từ SolidWorks, mô hình BAM `1910_m6.json` (§1.3, §2.2, §5.1) | Đã đọc README và các file mô hình |
| [Arduino UNO Q — tài liệu chính hãng](https://docs.arduino.cc/hardware/uno-q/) | Phần cứng điều khiển của XGO | Link xác nhận tồn tại |

**Tham khảo thêm**

| Nguồn | Dùng cho | Trạng thái |
|---|---|---|
| [Animan-AI/DuckBuddy — wiki](https://github.com/Animan-AI/DuckBuddy/wiki) | Fork cộng đồng của Microduck | Đã đọc (qua tìm kiếm) |

### 6.2. Công cụ phần mềm
| Nguồn | Dùng cho |
|---|---|
| [MuJoCo](https://github.com/google-deepmind/mujoco) · [tài liệu](https://mujoco.readthedocs.io/en/stable/overview.html) | Mô phỏng (Phase 2, 5) |
| [ros/solidworks_urdf_exporter](https://github.com/ros/solidworks_urdf_exporter) | SolidWorks → URDF (§1.3) |
| [Rhoban/bam](https://github.com/Rhoban/bam) | Better Actuator Models: System ID servo (§2.4, §4.5.3) |
| [mujocolab/mjlab](https://github.com/mujocolab/mjlab) | Framework train RL mà microduck_rl và xgoduck_rl dùng (Phase 5) |

Mọi link ở 6.2 đều mới xác nhận tồn tại.

### 6.3. Servo
| Servo | Nguồn | Số liệu đã lấy / ghi chú |
|---|---|---|
| **TowerPro MG92B** | [Trang chính hãng TowerPro](https://www.towerpro.com.tw/product/mg92b/) (đã đọc) | Stall 3.1 kgf·cm @5V, 3.5 kgf·cm @6V; 22.8×12×31 mm; 13.8 g; 5.0–6.6V |
| **Feetech HD1910** (HD-1910-C001 / HD1910M) | **Thông số chính:** [XGO docs/BOM.md, chép lại datasheet nhà sản xuất A/0, 07/09/2026](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/docs/BOM.md#servo-supplier-specification-and-runtime-configuration) (đã đọc). Bản PDF gốc không có trong repo, repo chỉ ghi mã SHA-256.<br>**Mô hình BAM:** [xgoduck_rl `1910_m6.json`](https://github.com/LuwuDynamics/xgoduck_rl/blob/main/src/mjlab_microduck/robot/xgoduck/params/1910_m6.json) (đã đọc).<br>**Nhà bán:** [OpenELAB product](https://openelab.io/products/feetech-hd1910-microduck-coreless-servo) · [OpenELAB blog](https://openelab.io/blogs/learn/microduck-servo-choice-feetech-hd-1910-c001-diy-biped) · [AliExpress](https://www.aliexpress.us/item/3256813231229999.html) · [AliExpress (2)](https://www.aliexpress.us/item/3256813018618209.html) · [eBay](https://www.ebay.com/itm/178566077139) · [Amazon](https://www.amazon.com/Dual-Shaft-MicroDuck-Magnetic-Encoders-Coreless/dp/B0HMX63D8F) · [Amazon (2)](https://www.amazon.com/MicroDuck-Dual-Shaft-Magnetic-Encoders-Coreless/dp/B0HMX2NP9Q) | Mọi số dưới đây có sai số ±10%.<br>**Theo 4.8 / 6.0 / 7.4V:** stall 9 / 12 / 15 kgf·cm; rated 2.2 / 3.0 / 3.7 kgf·cm; stall 1.2 / 1.6 / 2.0 A; không tải 0.137 / 0.109 / 0.088 s/60°.<br>**Thông số chung:** dải áp 4–8.4V; 34×20×23 mm; 21 g; encoder từ 12-bit; hộp số 1:320; backlash ≤0.5°; spline 25T; TTL half-duplex 1 Mbit/s.<br>Một trang nhà bán ghi "10 kg·cm" trên tiêu đề, **khác** datasheet. Ưu tiên datasheet |
| Giao thức servo bus Feetech | [Feetech Smart Servo Communication Protocol (bản lưu ở Mantech)](https://mantech.co.za/datasheets/products/Feetech%20Smart%20Servo%20Communication%20Protocol.pdf) | Link xác nhận tồn tại. Tài liệu chung cho dòng servo bus Feetech, chưa đối chiếu riêng với HD1910 |
| Feetech STS3215 (servo của SO-100/101) | [Core Electronics](https://core-electronics.com.au/feetech-sts3215-smart-servo.html) (đã đọc) · [RobotShop](https://robotshop.com/products/feetech-12v-30kgcm-magnetic-encoding-servo-sts3215) · [rcdrone C001](https://rcdrone.top/bn/products/feetech-sts3215-c001-servo-7-4v-19-5kg-1-345-servo-for-so-arm100-101) · [OpenELAB C044](https://openelab.io/products/feetech-sts3215-c044-servo-7) · [OpenELAB C046](https://openelab.io/da/products/feetech-sts3215-c046-servo) · [Evelta C046](https://evelta.com/sts3215-c046-7-4v-1-147-magnetic-encoding-metal-gear-dual-axis-ttl-serial-bus-servo-motor/) · [SO-101 specs](https://roboticscenter.ai/hardware/so-101/specs) | Ứng viên đã xem, chưa đưa vào bảng §1.1 |
| TowerPro MG958 | [servodatabase](https://servodatabase.com/servo/towerpro/mg958) · [Probots](https://probots.co.in/tower-pro-mg958-18kg-metal-gear-digital-servo.html) · [Makerlab](https://www.makerlab-electronics.com/products/towerpro-mg958-digital-servo-high-torque-15kg-standard-7075-alloy-gear) · [Cool Components](https://coolcomponents.co.uk/products/mg958-digital-metal-gear-servo) · [Soldered](https://soldered.com/product/servo-motor-towerpro-mg958) | Ứng viên đã xem, chưa đưa vào bảng §1.1. Các shop ghi torque khác nhau |

### 6.4. IC & bo mạch servo
| Nguồn | Dùng cho | Trạng thái |
|---|---|---|
| [PIC12F629/675 datasheet (Microchip, DS41190)](https://ww1.microchip.com/downloads/en/DeviceDoc/41190G.pdf) | Sơ đồ chân PIC ở §4.3.4, bước B1 | Link xác nhận tồn tại |
| [Will — "127 TowerPro Servos, one I2C interface"](https://hackaday.io/project/6748-127-towerpro-servos-one-i2c-interface) | Bảng linh kiện §4.3.1: PIC12F675, resonator 8 MHz, cầu H 2× SOIC-8 (đoán giống IRF7309), 2 transistor dịch mức, LDO 3.3V | Đã đọc. ⚠️ Đây là **MG995**, không phải MG92B |
| [pat92fr — "Smarter Micro Servo (SMS) MOD"](https://hackaday.io/project/176678) · [hướng dẫn](https://hackaday.io/project/176678/instructions) | Mod **MG92B**. Bỏ bo zin, giữ motor và chiết áp, thay bằng bo riêng trong từng servo: STM32G431KB + driver DRV8872 (chế độ giới hạn dòng, đặt 1 A), shunt 0.33 Ω qua op-amp nội (PGA ×8), cấp thẳng LiPo 2S 6.5–10V (biến thể A′, §4.2) | Đã đọc. Trang không ghi linh kiện của bo zin |
| [IRF7309 datasheet (Infineon)](https://www.infineon.com/assets/row/public/documents/non-assigned/49/irf7309pbf-1.pdf) | MOSFET mà tác giả bài MG995 **đoán** là linh kiện cầu H: cặp N + P SO-8, 30V, 4A (N) / −3A (P) | Link xác nhận tồn tại. **Chỉ là phỏng đoán của tác giả**, mã thật đã bị cạo |
| [DRV8872 datasheet (TI)](https://www.ti.com/lit/ds/symlink/drv8872.pdf) | Driver cầu H dùng trong SMS MOD (biến thể A′) | Link xác nhận tồn tại |
| [STM32G431KB (ST)](https://www.st.com/en/microcontrollers-microprocessors/stm32g431kb.html) | MCU của SMS MOD | Chưa mở được (trang ST không phản hồi lúc kiểm tra) |
| 2 transistor, LDO 3.3V, IC MOSFET thật trên bo **MG92B** | §4.3.3 | **Không tìm được nguồn công khai nào ghi mã linh kiện bo MG92B** (đã tìm 05/11/2026). Bài MG995 cũng không có mã vì bị cạo. Cách duy nhất là tháo 1 con và đọc mã (bước B1) |

### 6.5. Bài viết về giá / BOM Microduck
* [Robotopian — Microduck hardware BOM & cost analysis](https://robotopian.com/blogs/news/microduck-hardware-bom-suppliers-cost-analysis) (đã đọc)
* [NYU Shanghai RITS — Hugging Face opens preorders for Microduck](https://rits.shanghai.nyu.edu/ai/hugging-face-opens-preorders-for-microduck-a-399-open-source-biped/)
* [The Gadgeteer — Microduck $399 preorder](https://the-gadgeteer.com/2026/10/24/microduck-robot-399-programmable-preorder/)
* [New Atlas — Microduck](https://newatlas.com/robotics/adorable-waddling-robot-pick-up-hugging-face-microduck-pollen-robotics/)
* [rcdrone — Microduck hardware explained](https://rcdrone.top/blogs/articles/microduck-hardware-explained-how-to-build-an-original-diy-rl-biped-robot)

## 7. Cấu trúc repo
```
README.md                      Bối cảnh, đề bài, cách tiếp cận, nguồn tham khảo (file này)
Phase1_CAD_HocServo.md         Phase 1: model lại CAD (SolidWorks), MJCF cho từng ứng viên
Phase2_MoPhong_TaiServo.md     Phase 2: tải tĩnh / động trên MuJoCo
Phase3_PhanTich_IO.md          Phase 3: I/O ứng viên so với HD1910, ma trận phương án
Phase4_PhuongAn_DoChe.md       Phase 4: phương án độ chế A / A′ / B / C, kiểm thử, System ID
Phase5_Train_Policy.md         Phase 5: train policy (microduck_rl / xgoduck_rl, BAM)
Phase6_PhanCung_ChayThat.md    Phase 6: BOM, gia công, chạy thật
CHECKLIST.md                   Lỗi cần tránh, chia theo phase
scripts/                       static_torque.py, dynamic_load.py (xem scripts/README.md)
LICENSE                        CC BY-NC-SA 4.0
```

## 8. Giấy phép
Toàn bộ nội dung repo, gồm tài liệu, script và các file CAD thêm vào sau này, phát hành theo **[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)**. Toàn văn ở [LICENSE](LICENSE).

* Chọn NC-SA để khớp với điều kiện mô hình 3D upstream (microduck_rl / XGO-Duck, xem [UPSTREAM.md của XGO](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/UPSTREAM.md)). Chi tiết CAD vẽ lại từ STL upstream phải giữ điều kiện này.
* Repo **không chứa** file nào của các dự án upstream, chỉ dẫn link. Số liệu trích từ upstream và nhà sản xuất đều ghi nguồn ở §6.
* Tên sản phẩm (Microduck, XGO-Duck, Feetech, TowerPro…) thuộc về chủ sở hữu tương ứng. Dự án này độc lập, không liên kết với Pollen Robotics hay Luwu Dynamics.
