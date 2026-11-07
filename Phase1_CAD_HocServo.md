# PHASE 1 — MODEL LẠI CAD: HỐC SERVO CHO TỪNG ỨNG VIÊN

[README](README.md) · [Phase 1 – CAD](Phase1_CAD_HocServo.md) · [Phase 2 – Mô phỏng tải](Phase2_MoPhong_TaiServo.md) · [Phase 3 – Phân tích I/O](Phase3_PhanTich_IO.md) · [Phase 4 – Độ chế](Phase4_PhuongAn_DoChe.md) · [Phase 5 – Train](Phase5_Train_Policy.md) · [Phase 6 – Phần cứng & chạy thật](Phase6_PhanCung_ChayThat.md) · [Checklist](CHECKLIST.md)

---

> **Trạng thái:** chưa bắt đầu (cập nhật 05/11/2026).
> **Đầu vào:** cơ khí của XGO-Duck và servo ứng viên mua về (1–2 con mỗi loại).
> **Đầu ra:** mỗi ứng viên có 1 biến thể CAD và 1 file MJCF với khối lượng thật, để chạy Phase 2.

## 1.0. Hiện trạng file CAD/MJCF của XGO-Duck (kiểm tra 05/11/2026)

| Có gì | Ở đâu | Hệ quả |
|---|---|---|
| **Chỉ có file STL** của các chi tiết in (`structure/*.stl`, 30 file, ví dụ `2x_shank.stl`, `2x_hip_rol_shell.stl`) | [xgoduck_hardware/structure](https://github.com/LuwuDynamics/xgoduck_hardware/tree/master/structure) | Không sửa hốc theo tham số được. Phải **vẽ lại** các chi tiết chứa servo trong CAD, dùng STL làm khuôn tham chiếu (import mesh, đo, dựng lại) |
| Bản lắp SolidWorks gốc (`XGODUCK_roller.SLDASM`) | Chỉ được nhắc tên trong `mass_properties_sw.json`, **không công bố** | Không có CAD tham số gốc |
| **MJCF + URDF của XGO-Duck**, khối lượng và quán tính từng link xuất từ SolidWorks (tổng 0.874 kg cho bản roller) | [xgoduck_rl/src/mjlab_microduck/robot/xgoduck](https://github.com/LuwuDynamics/xgoduck_rl/tree/main/src/mjlab_microduck/robot/xgoduck) (`robot_walk.xml`, `robot_allcollisions.xml`, `urdf/XGODUCK.urdf`) | **Dùng làm MJCF baseline HD1910 cho Phase 2 ngay**, không cần chờ vẽ lại CAD. Biến thể cho ứng viên khác: sửa khối lượng, CoM, quán tính của các link chứa servo (§1.4) |
| Giấy phép mô hình 3D | [UPSTREAM.md](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/UPSTREAM.md): microduck_rl ghi giấy phép **phi thương mại, share-alike** cho mô hình 3D | Chi tiết vẽ lại dựa trên STL của XGO/Microduck vẫn phải tuân theo giấy phép đó |

## 1.1. Ứng viên servo

| Ứng viên | Vai trò | Ghi chú |
|---|---|---|
| Feetech HD1910 | **Baseline**, servo gốc của XGO-Duck | Khung XGO thiết kế cho servo này: 34×20×23 mm, 21 g, spline 25T. Mô-men theo datasheet nhà sản xuất do XGO chép lại (xem [README §1](README.md)) |
| TowerPro MG92B | Ứng viên giá rẻ cho 10 khớp chân (hoặc cả 15) | 22.8×12×31 mm, 13.8 g theo trang TowerPro (đo lại). Nhỏ hơn hốc HD1910, phải làm hốc mới. Nếu chọn sẽ cần độ (Phase 4) |
| TowerPro MG90S | Ứng viên cho 5 khớp đầu/cổ | Tải ở đầu nhỏ hơn chân, xác nhận lại ở Phase 2. Riêng **servo mỏ** không thuộc policy RL, nên có thể dùng servo zin không độ (§3.4) |

Có thêm ứng viên khác thì bổ sung vào bảng này. Kích thước của mỗi ứng viên phải **đo bằng thước kẹp trên con thật**, không lấy từ ảnh trên trang bán hàng.

## 1.2. Chi tiết tiêu chuẩn: thiết kế bắt đầu từ linh kiện mua được ở VN

> ⚠️ **Vòng bi của XGO-Duck tương đối khó tìm ở VN.** Phải kiểm tra nguồn mua trước khi vẽ lại CAD.

**Nguyên tắc thiết kế hệ cơ điện tử:** thiết kế phải xuất phát từ **chi tiết tiêu chuẩn**, tức các chi tiết mà nhóm không tự gia công được (vòng bi, bu lông, đai ốc, vít tự ren, chốt, trục, lò xo, đầu nối...). Kích thước của chúng là cố định, nên chi tiết tự làm (in 3D, CNC) phải vẽ quanh chúng. Làm ngược lại sẽ dẫn đến một bản CAD đẹp nhưng không lắp được vì không mua được linh kiện.

Hệ quả cho dự án: XGO-Duck chọn linh kiện theo thị trường Trung Quốc. Khi vẽ lại CAD, **phải chốt danh sách chi tiết tiêu chuẩn mua được ở VN trước**, sau đó mới vẽ ổ đỡ, lỗ bắt vít và hốc servo theo danh sách đó.

### 1.2.1. Chi tiết tiêu chuẩn của XGO-Duck

Theo [BOM của xgoduck_hardware](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/docs/BOM.md) (đọc 07/11/2026):

| Chi tiết | SL | Ghi chú |
|---|---|---|
| Vòng bi 10 × 15 × 3 mm | 10 (2 + 8 cho bản roller) | BOM **không ghi mã series**, chưa rõ nắp che/phớt/vành chặn |
| Vòng bi 16 × 22 × 4 mm | 11 | Như trên |
| Vít tự ren M2 × 6, đầu bằng (côn chìm), đuôi bằng | 204 (200 + 4 cho roller) | Vít bắt vào nhựa in |
| Vít tự ren M2.3 × 8, đầu tròn mặt phẳng, đuôi bằng | 6 | BOM ghi rõ không thay bằng vít M2.5 × 6 của trục servo |
| Ốc máy M3 × 16, đầu tròn | 4 | Ren máy |
| Dây servo AMP2.0-3P, bước 2.0 mm, 150 mm | 15 | Đầu cắm theo servo HD1910; đổi servo thì đầu cắm cũng đổi |

Vì BOM không ghi mã series, phải tìm vòng bi theo kích thước $d \times D \times B$ và mua mẫu về đo lại. Không giả định một mã vòng bi nào khớp chỉ vì trùng kích thước.

Phương án độ MG92B (§4.1.2) thêm các chi tiết tiêu chuẩn riêng: vòng bi MR63ZZ, chốt thép $\Phi 3$ h6 hoặc ốc vai. Các chi tiết này cũng phải qua bước kiểm tra nguồn mua bên dưới.

### 1.2.2. Quy trình
1. **Khảo sát nguồn VN cho từng chi tiết** trong bảng §1.2.1 và các chi tiết của phương án độ. Ghi vào BOM ([Phase 6 §6.1](Phase6_PhanCung_ChayThat.md)): nơi bán, mã, kích thước, đơn giá, ngày tra, link.
2. **Mua mẫu và đo bằng thước kẹp** trước khi vẽ. Với vòng bi, đo $d$, $D$, $B$ và ghi loại nắp che (ZZ, 2RS, hở), có vành chặn hay không.
3. **Không mua được thì đổi sang kích thước có sẵn ở VN**, rồi sửa ổ đỡ trong CAD:
   * Tham số hóa ổ đỡ bằng biến, ví dụ `brg_d`, `brg_D`, `brg_B`, giống cách tham số hóa hốc servo ở §1.3.
   * Đổi vòng bi chỉ được làm thay đổi ổ đỡ, **không được dời trục khớp** (§1.3, bước 3).
   * Kiểm tra lại không gian quanh ổ (thành ổ in 3D đủ dày) và tải của khớp đó.
4. **Ốc vít:** ưu tiên cỡ phổ biến ở VN. Không thay vít tự ren bằng ốc máy hoặc ngược lại mà không sửa lỗ trong CAD. Nếu đổi sang ốc máy thì phải vẽ thêm chỗ cho đai ốc hoặc insert ren cấy nóng.
5. **Chốt danh sách chi tiết tiêu chuẩn** (kích thước đo thật) trước khi vẽ hốc servo ở §1.3.

## 1.3. Sửa hốc servo
1. **Đo servo thật:**
   * Kích thước thân, vị trí và đường kính lỗ tai bắt vít.
   * **Vị trí trục ra so với thân.** Đây là kích thước quan trọng nhất.
   * Chiều cao horn, số răng spline (xem §4.1.2).
   * Vị trí lỗ ra dây.
2. **Vẽ lại các chi tiết chứa servo từ STL** (xem §1.0): import STL của XGO, dựng lại chi tiết dạng solid có tham số. **Tham số hóa hốc** bằng biến, ví dụ `servo_L`, `servo_W`, `servo_H`, `shaft_offset`. Đổi ứng viên chỉ cần đổi bộ biến.
3. **Giữ nguyên vị trí và hướng trục khớp của XGO-Duck.** Phần thay đổi là thân servo dịch quanh trục khớp, còn trục khớp đứng yên. Nhờ vậy động học chân và gait giữ nguyên, kết quả Phase 2 giữa các ứng viên so sánh được với nhau.
4. **Kiểm tra va chạm trên toàn dải góc khớp:** dải khớp phải nằm gọn trong hành trình cơ của servo và chốt chặn (xem Bước A2 ở §4.2).
5. **Nếu ứng viên cần độ (MG92B), chừa chỗ ngay từ bây giờ:**
   * U-bracket hai gối đỡ, vòng bi MR63ZZ, chốt trục giả $\Phi 3$ h6 (§4.1.2).
   * Nắp đáy in 3D. Với phương án B, nắp này phải chứa được bo zin (§4.3).
   * Đường luồn bó dây qua U-bracket và khớp háng (§4.3.5).

## 1.4. Khối lượng & quán tính → MJCF

**Cách nhanh (làm trước):** lấy MJCF của XGO-Duck trong `xgoduck_rl` làm gốc.
* `robot_walk.xml` có free joint `trunk_base_freejoint` ở gốc cây, nên 6 DOF đầu là base, đúng như script §2.2 giả định.
* Đã có site `left_foot` / `right_foot`.
* Khớp chân: `left_hip_yaw`, `left_hip_roll`, `left_hip_pitch`, `left_knee`, `left_ankle`, và tương tự cho `right_*`. Khớp đầu: `neck_pitch`, `head_pitch`, `head_yaw`, `head_roll`.
* `robot_walk.xml` chỉ có 14 khớp vì **mỏ không do policy RL điều khiển**: XGO điều khiển mỏ riêng qua console. Vậy MJCF đi bộ có 14 khớp, còn robot thật có 15 servo. Khi tạo biến thể, vẫn phải cộng khối lượng servo mỏ vào link đầu.

Với mỗi ứng viên, tạo `duck_<servo>.xml` bằng cách sửa khối lượng, CoM và quán tính của các link chứa servo:
* Bớt phần khối lượng HD1910 (21 g mỗi con).
* Cộng khối lượng ứng viên **cân thật**.
* Cộng thay đổi của chi tiết in vẽ lại.

**Cách đầy đủ (sau khi vẽ lại CAD ở §1.3):**
* Mỗi link cần đủ khối lượng $m$, trọng tâm CoM và tensor quán tính $I$.
* **Chi tiết in 3D:** CAD tính khối lượng như vật đặc, trong khi bản in thật có infill khoảng 15–30%. Cần in thử, cân từng chi tiết rồi ghi đè khối lượng trong CAD. Nếu chưa in được thì gán khối lượng riêng hiệu dụng theo infill và ghi chú là số ước lượng.
* **Linh kiện nặng:** servo, pin, bo mạch, ốc và dây phải có trong CAD, ít nhất dưới dạng khối đặc trưng (dummy). Khối lượng gán vào là **khối lượng cân thật**.
* **Xuất mô hình (SolidWorks):**
  * Dùng `sw_urdf_exporter` để xuất URDF. MuJoCo đọc trực tiếp được URDF.
  * Khối lượng và quán tính lấy theo cách XGO đã làm trong `mass_properties_sw.json`: dùng Mass Properties của SolidWorks cho từng link, có override khối lượng, quán tính tính quanh CoM theo trục link.
* Giữ site `left_foot` / `right_foot` như MJCF của XGO, đặt tại **tâm đế bàn chân, sát mặt đất**. Script §2.2 tính phản lực đất tại hai điểm này. Kiểm tra lại vị trí site trên mesh đế chân.

## 1.5. Kiểm tra bền chi tiết in 3D sau khi vẽ lại

Chi tiết sửa ít (chỉ đổi kích thước hốc, thành hốc vẫn dày như cũ) thì thường không cần làm mục này. Chi tiết **sửa nhiều** thì phải kiểm tra lại độ bền và độ cứng. "Sửa nhiều" gồm: đổi hình dạng, mỏng thành, khoét thêm, dời lỗ vít hoặc ổ vòng bi, đổi đường truyền lực.

```
Tải 6 thành phần tại khớp (Phase 2 §2.4)
      ↓
FEA trong SolidWorks Simulation (bước 2)  ──→  so với chi tiết gốc XGO cùng tải (bước 3)
      ↓                                              ↓ vượt bản gốc
Thử tải bản in thật (bước 4)  ←─────────────────────┘
      ↓
Sửa CAD → cân lại → cập nhật MJCF (§1.4) → chạy lại Phase 2
```

1. **Lấy tải.** Chạy [`joint_wrench.py`](scripts/joint_wrench.py) theo [Phase 2 §2.4](Phase2_MoPhong_TaiServo.md) cho mọi ca: tư thế tĩnh, đi, **té ngã và va đập**. Với mỗi chi tiết, lấy bộ 6 thành phần tại các khớp mà chi tiết đó nối, ở các thời điểm đỉnh.

2. **FEA trong SolidWorks Simulation**, phân tích tĩnh tuyến tính (Static study):
   * **Gá cố định** (Fixture): mặt ổ vòng bi hoặc mặt bắt servo ở một đầu chi tiết.
   * **Đặt tải** (Remote Load) tại tâm khớp ở đầu còn lại, theo hệ tọa độ trùng frame link của MJCF (§2.4, lưu ý 2).
   * **Vật liệu:** lấy từ datasheet của **đúng loại nhựa và đúng hãng** sẽ in. Ưu tiên hãng công bố độ bền theo cả phương XY (trong lớp) và phương Z (giữa các lớp). Chi tiết in yếu nhất ở phương Z, nên vùng chịu kéo vuông góc với lớp in phải so với độ bền Z. Ghi rõ nguồn số liệu vật liệu.
   * **Hai tiêu chí:**
     * **Độ bền:** ứng suất lớn nhất so với độ bền vật liệu, có hệ số an toàn. Với chi tiết in, hệ số khoảng 2–4 là kinh nghiệm thực hành; **dự án tự chốt**.
     * **Độ cứng:** độ võng hoặc góc xoay quy về khớp phải nhỏ so với backlash của servo (HD1910 $\le 0.5^\circ$). Khung mềm hơn servo thì policy, vốn train trên mô hình khung cứng, sẽ chạy sai.
   * **Giới hạn:** FEA coi chi tiết là khối đặc, trong khi bản in có infill. Vì vậy FEA chỉ cho biết **vị trí** ứng suất tập trung và **so sánh** giữa các thiết kế. Không coi ứng suất tính ra là độ bền tuyệt đối của bản in.

3. **So với chi tiết gốc của XGO.** Chi tiết gốc đã chạy được trên robot thật, nên đây là mốc tin cậy hơn số tuyệt đối:
   * Import STL gốc vào SolidWorks và chuyển thành solid body.
   * Chạy FEA với **cùng ca tải, cùng gá, cùng vật liệu** cho bản gốc và bản vẽ lại.
   * Ứng suất lớn nhất và độ võng của bản mới **không vượt bản gốc** → đạt.
   * Vượt bản gốc → sửa thiết kế, hoặc chứng minh bằng thử thật ở bước 4.
   * Ca té ngã và va đập chỉ dùng được ở bước này (so tương đối), vì lực va chạm trong sim không đáng tin về giá trị tuyệt đối (§2.4, lưu ý 1).

4. **Thử tải bản in thật:**
   * In chi tiết với **đúng thông số in sẽ dùng thật**: cùng nhựa, infill, số vách (perimeter), nhiệt độ và hướng đặt khi in.
   * Gá giống như trong FEA. Treo tạ hoặc kéo bằng cân móc theo hướng tải chính, tăng dần tới khi gãy.
   * **Đạt** khi tải gãy $\ge$ tải lớn nhất từ bước 1 × hệ số an toàn. Ghi lại tải gãy, vị trí gãy, so với vị trí ứng suất tập trung trong FEA.
   * Kiểm tra thêm những chỗ FEA không bắt được:
     * Lỗ vít tự ren M2 (§1.2.1) bị tuột ren sau nhiều lần tháo lắp.
     * Ổ vòng bi bị lỏng dần do nhựa biến dạng chậm (creep) dưới tải lâu dài.

5. **Sửa thiết kế nếu không đạt**, theo thứ tự rẻ trước:
   * Đổi hướng đặt khi in sao cho ứng suất chính chạy dọc lớp in.
   * Tăng số vách ở vùng chịu lực. Vùng quanh ổ vòng bi và lỗ vít in đặc 100%.
   * Thêm gân, bo góc tại vị trí ứng suất tập trung mà FEA chỉ ra.
   * Đổi vật liệu in.

   Sau mỗi lần sửa: cân lại bản in, cập nhật khối lượng trong MJCF (§1.4) rồi chạy lại Phase 2, vì khối lượng đổi thì tải đổi.

## 1.6. Điều kiện xong Phase 1
- [ ] Đã có danh sách chi tiết tiêu chuẩn (vòng bi, ốc vít, chốt) **mua được ở VN**, kèm kích thước đo trên mẫu thật (§1.2).
- [ ] Đã có MJCF baseline HD1910 (từ `xgoduck_rl`) và mở được trong MuJoCo viewer.
- [ ] Mỗi ứng viên có 1 biến thể `duck_<servo>.xml`, khối lượng servo đã thay bằng số cân thật.
- [ ] Nếu đi tiếp sang chế tạo: các chi tiết chứa servo đã vẽ lại thành CAD tham số. Trục khớp trùng XGO-Duck và không va chạm trong dải khớp.
- [ ] Chi tiết sửa nhiều đã qua kiểm tra bền (§1.5): ứng suất và độ võng không vượt bản gốc XGO, hoặc đã thử tải bản in thật đạt hệ số an toàn.

---

← [README](README.md) · [Phase 2](Phase2_MoPhong_TaiServo.md) →
