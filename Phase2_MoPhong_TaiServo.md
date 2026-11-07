# PHASE 2 — MÔ PHỎNG TẢI SERVO TRÊN MUJOCO (TĨNH & DI CHUYỂN)

[README](README.md) · [Phase 1 – CAD](Phase1_CAD_HocServo.md) · [Phase 2 – Mô phỏng tải](Phase2_MoPhong_TaiServo.md) · [Phase 3 – Phân tích I/O](Phase3_PhanTich_IO.md) · [Phase 4 – Độ chế](Phase4_PhuongAn_DoChe.md) · [Phase 5 – Train](Phase5_Train_Policy.md) · [Phase 6 – Phần cứng & chạy thật](Phase6_PhanCung_ChayThat.md) · [Checklist](CHECKLIST.md)

---

> **Trạng thái:** quy trình và script đề xuất 05/11/2026, **chưa có kết quả tính nào**. Mọi số liệu phải sinh từ MJCF của dự án (Phase 1) và từ servo đo thật (§2.5).
> **Đầu vào:** `duck_<servo>.xml` từ Phase 1. Baseline HD1910 dùng thẳng `robot_walk.xml` của [xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl/tree/main/src/mjlab_microduck/robot/xgoduck). Phải clone cả repo, vì MJCF tham chiếu mesh STL theo đường dẫn tương đối.
> **Đầu ra:** bảng $\tau_{peak}$, $\tau_{RMS}$, $\omega_{max}$ cho từng khớp, từng ứng viên, kèm kết luận ứng viên nào đi tiếp sang [Phase 3](Phase3_PhanTich_IO.md). Thêm bảng tải 6 thành phần tại từng khớp (§2.4) để kiểm tra bền chi tiết in ở Phase 1 §1.5.

**Mục tiêu:** tính mô-men và tốc độ mà mỗi khớp **cần** khi robot đứng và đi, rồi so với khả năng **đo được** của servo.

```
Chọn ứng viên → sửa gá CAD → cân/gán khối lượng → xuất MJCF        (Phase 1)
      ↑                                                  ↓
 loại / đổi servo ← so τ_peak, τ_RMS, (ω,τ) với servo ĐO THẬT ← tĩnh (§2.2) + động (§2.3)
```

Mỗi ứng viên có **một biến thể MJCF riêng**, vì đổi servo thì khối lượng ở chân đổi, kéo theo tải của mọi khớp phía trên.

## 2.1. Tư thế cần xét

| Tư thế | Khớp thường chịu tải nặng nhất |
|---|---|
| Đứng 1 chân (pha single support khi đi) | Hip roll, ankle roll của chân trụ, vì phải đỡ cả thân lệch sang bên |
| Ngồi xổm sâu nhất mà gait dùng tới | Knee, hip pitch, vì cánh tay đòn trọng tâm lớn nhất |
| Đứng dậy từ ngồi xổm | Knee, cộng thêm thành phần gia tốc (xem §2.3) |
| Các frame của quỹ đạo gait | Tất cả các khớp; cho tải tĩnh tương đương theo thời gian |

## 2.2. Mô-men tĩnh (script `static_torque.py`)

**Nguyên lý.** Khi robot đứng yên ($\dot{q} = \ddot{q} = 0$), phương trình chuyển động rút gọn thành:

$$g(q) = S^T\tau + J_c^T f$$

Trong đó:
* $g(q)$ là lực trọng trường. Khi $\dot q = 0$, nó đúng bằng `qfrc_bias` của MuJoCo.
* $J_c$ là Jacobian tại site bàn chân chạm đất.
* $f$ là wrench mặt đất tác dụng lên chân, gồm lực và mô-men, tổng cộng 6 thành phần cho mỗi chân.

6 hàng đầu ứng với base tự do và không có actuator. Từ 6 hàng này giải ra $f$, sau đó tính $\tau = g_j - J_{c,j}^T f$ cho các khớp. Nhờ vậy dùng thẳng model base tự do mà không phải đổi gốc cây động học sang bàn chân.

**Script:** [`scripts/static_torque.py`](scripts/static_torque.py) (cách cài và chạy xem [`scripts/README.md`](scripts/README.md)).

```
cd xgoduck_rl/src/mjlab_microduck/robot/xgoduck
python <đường dẫn repo>/scripts/static_torque.py robot_walk.xml --foot-half <HX> <HY>
```

* `--foot-half`: nửa chiều dài và nửa chiều rộng đế chân [m], **đo trên CAD**. Bỏ trống thì script không kiểm tra CoP và in cảnh báo.
* Ví dụ trong `main()`: quét độ ngồi xổm khi đứng 1 chân trái. **Dấu góc là giả định.** Phải mở viewer kiểm tra chiều gập và đế chân trụ có nằm phẳng không.
* Script tự kiểm tra cân bằng lực: khi đứng 1 chân, $F_z = m g$.
* **Đã kiểm chứng phương pháp (05/11/2026)** trên `robot_walk.xml` của xgoduck_rl. Mô-men từng khớp khớp với momen trọng lực tính độc lập quanh trục khớp, sai lệch $< 10^{-13}$ N·m. Lần chạy đó chỉ để kiểm tra script; tư thế ví dụ chưa kiểm tra dấu và CoP, nên **chưa phải kết quả tải**.

**Lưu ý khi đọc kết quả:**
1. **CoP nằm ngoài đế chân** nghĩa là robot thật sẽ đổ ở tư thế đó, nên mô-men tính ra không có ý nghĩa. Script tự loại các tư thế này. Phải truyền `--foot-half` bằng kích thước đế chân đo trên CAD. Nếu bỏ trống, script không kiểm tra CoP.
2. **Khi đứng 2 chân, cách chia tải giữa hai chân là bất định.** `lstsq` chỉ trả về một nghiệm hợp lý, chưa chắc khớp thực tế. Để kiểm tra chéo: thả robot vào sim có tiếp xúc đất, giữ tư thế bằng actuator, đợi khoảng 1 s cho ổn định rồi đọc `d.actuator_force`. Trường hợp quyết định thiết kế là đứng 1 chân, và ở đó nghiệm là duy nhất.
3. **Đây là cận dưới của tải.** Ở §2.3, nếu tải động của một khớp **nhỏ hơn** tải tĩnh ở cùng tư thế thì model sim đang có lỗi.

## 2.3. Tải động khi đi (script `dynamic_load.py`)

Cách làm:
1. Chạy quỹ đạo gait trong forward sim. Nguồn quỹ đạo có thể là gait của XGO, hoặc policy đã train bằng microduck_rl / xgoduck_rl (ví dụ policy HD1910 của XGO chạy trên MJCF ứng viên).
2. Dùng actuator dạng position với kp cao và `forcerange` rất lớn, để sim cho biết khớp **cần** bao nhiêu mô-men.
   * ⚠️ MJCF của XGO đặt sẵn `forcerange="-1.04 1.04"` (N·m), tức đã giới hạn theo servo 1910. Khi tính tải phải **nới giới hạn này** trong một bản sao. Nếu không, mô-men bị cắt và nhìn như "đủ".
3. Ghi log $\tau(t)$ và $\omega(t)$ cho từng khớp.

**Script:** [`scripts/dynamic_load.py`](scripts/dynamic_load.py).

```
python <đường dẫn repo>/scripts/dynamic_load.py scene_walk.xml --gait my_gait:q_ref --kp 20 --force-limit 100
```

* `--gait module:hàm`: hàm `q_ref(t, m)` trả về góc mục tiêu cho mọi actuator. Bỏ trống thì script chỉ giữ tư thế 0 để kiểm tra chạy được. Robot không có bộ cân bằng nên sẽ chao, **số in ra không phải tải thật**.
* `--force-limit`: mặc định nới `forcerange` lên ±100 N·m. Script cảnh báo nếu actuator vẫn chạm giới hạn.
* `--kp`: đặt kp cứng cho actuator `<position>`. MJCF của XGO để kp = 0.84, quá mềm nên không bám được quỹ đạo.
* Log lưu ra `load_log.npz` (`tau`, `w`, `names`, `dt`) để vẽ đồ thị $\tau$–$\omega$.

**Kịch bản cần chạy:**
* Đứng yên.
* Đi ở tốc độ mục tiêu.
* Đi nhanh hơn mục tiêu khoảng 20%.
* Xoay tại chỗ.
* Đứng dậy từ ngồi xổm.
* Bị đẩy ngang (push recovery).
* Ngã rồi tự đứng dậy, nếu robot cần làm việc này.

> **Khớp mỏ:** MJCF đi bộ của XGO không có khớp mỏ, vì mỏ được điều khiển riêng qua console, không qua policy (§1.4). Vì vậy các kịch bản trên **không cho tải của servo mỏ**. Tính tải mỏ riêng: lấy mô-men tĩnh của hàm (khối lượng × cánh tay đòn CoM tới trục, $\tau = m g d$ ở góc xấu nhất), cộng với tải của thao tác cần làm, ví dụ ngậm hoặc kẹp vật.

**Chỉ số và cách so:**

| Chỉ số | So với | Bắt lỗi gì |
|---|---|---|
| $\tau_{peak} = \max\lvert\tau\rvert$ | $\tau_{stall}$ đo thật | Servo bị ghì, không theo kịp quỹ đạo |
| $\tau_{RMS}$ cả chu kỳ đi | Khả năng tải liên tục (nhiệt) | Servo nóng hoặc cháy khi chạy lâu, lỗi hay gặp ở servo rẻ |
| $\omega_{max}$ | $\omega_0$ (không tải) đo thật | Không đạt tốc độ bước |
| Đám điểm $(\omega, \tau)$ | Đường đặc tính $\tau = \tau_{stall}(1 - \omega/\omega_0)$ ở **áp pin khi có tải** | Điểm nào nằm trên đường thì servo không đáp ứng được |

**Ngưỡng chấp nhận** (dựa trên kinh nghiệm thực hành, chưa phải số đã kiểm chứng; dự án tự chốt). Đối chiếu với datasheet HD1910: rated torque bằng khoảng 25% stall (3.0 / 12 kgf·cm ở 6V), khớp với ngưỡng $\tau_{RMS}$ dưới đây. Ứng viên có datasheet ghi rated torque thì so $\tau_{RMS}$ trực tiếp với rated torque.
* $\tau_{peak} \lesssim 50\text{–}60\%\ \tau_{stall}$
* $\tau_{RMS} \lesssim 25\text{–}30\%\ \tau_{stall}$
* Mọi điểm $(\omega, \tau)$ nằm dưới đường đặc tính.

Phải chừa biên vì hai lý do. Thứ nhất, thông số stall trên trang bán hàng thường ghi cao hơn thực tế. Thứ hai, áp pin sụt khi 15 servo cùng kéo tải.

## 2.4. Tải lên chi tiết cơ khí (script `joint_wrench.py`)

§2.2 và §2.3 chỉ cho **mô-men quanh trục khớp**, tức tải của servo. Chi tiết in 3D, ổ đỡ và vòng bi còn chịu các thành phần khác truyền qua khớp: lực dọc trục, lực hướng kính và **mô-men uốn**. Mô-men uốn thường là thứ làm gãy chi tiết in. Mục này lấy đủ 6 thành phần lực/mô-men tại từng khớp để làm đầu vào cho kiểm tra bền ở [Phase 1 §1.5](Phase1_CAD_HocServo.md).

**Nguyên lý.** Sau `mj_forward`, gọi thêm `mj_rnePostConstraint`. MuJoCo trả về `cfrc_int[b]`: lực và mô-men mà body cha tác dụng lên body $b$ (gồm cả nhánh phía dưới $b$), lấy quanh trọng tâm cây `subtree_com[root]`. Script chuyển mô-men về tâm khớp $p$ (`xanchor`):

$$M_p = M_c + (c - p) \times F$$

rồi chiếu lên hệ trục của body con (frame link trong MJCF/URDF), và tách theo trục khớp $\hat a$:
* $M_{axis} = M_p \cdot \hat a$: phần servo gánh.
* $M_{bend} = \lVert M_p - M_{axis}\hat a \rVert$: phần ổ đỡ, vòng bi và khung gánh.
* $F_{axial} = F \cdot \hat a$, $F_{radial} = \lVert F - F_{axial}\hat a \rVert$: tải vòng bi.

**Script:** [`scripts/joint_wrench.py`](scripts/joint_wrench.py).

```
python <đường dẫn repo>/scripts/joint_wrench.py scene_walk.xml --gait my_gait:q_ref --kp 20 --check
python <đường dẫn repo>/scripts/joint_wrench.py scene_walk.xml --kp 20 --drop 0.05   # thả rơi 5 cm
python <đường dẫn repo>/scripts/joint_wrench.py scene_walk.xml --kp 20 --push 1.0    # đẩy ngang 1 m/s
```

* `--gait`, `--kp`, `--force-limit`, `--settle`, `--run`: giống `dynamic_load.py` (§2.3).
* `--drop H`: sau thời gian `--settle`, nâng base thêm $H$ [m] rồi thả. Đây là ca va đập.
* `--push V`: sau `--settle`, đặt vận tốc ngang $V$ [m/s] cho base. Đẩy đủ mạnh thì robot ngã, đây là ca té ngã.
* `--check`: so $M_{axis}$ với mô-men khớp tính theo cách độc lập (actuator + passive + frictionloss/limit − armature·$\ddot q$). Sai lệch lớn nghĩa là quy ước tính bị sai.
* In ra cho mỗi khớp: $\lvert F\rvert_{max}$, $F_{axial}$, $F_{radial}$, $M_{axis}$, $M_{bend}$ đỉnh, kèm **đủ 6 thành phần $[F_x\,F_y\,F_z\,M_x\,M_y\,M_z]$ tại thời điểm $M_{bend}$ đỉnh**. FEA phải dùng bộ 6 số xảy ra cùng lúc này, không ghép các đỉnh riêng lẻ của từng thành phần (ghép như vậy thường quá bảo thủ và không ứng với trạng thái nào có thật).
* Log đầy đủ theo thời gian lưu ra `wrench_log.npz` (`wrench`, `decomp`, `actuator_force`, `names`, `dt`), dùng để chọn thêm thời điểm khác cho FEA, ví dụ lúc $F_{radial}$ đỉnh.

**Đã kiểm chứng (07/11/2026):**
* Con lắc 1 khớp, 1 kg, cánh tay đòn 0.2 m, giữ nằm ngang: script cho $F_z = +9.81$ N (cha đỡ con hướng lên) và $M = -1.962$ N·m, bằng đúng mô-men actuator. Quy ước dấu và điểm đặt đúng.
* `scene_walk.xml` của xgoduck_rl, `--kp 20`, cả 3 ca (giữ tư thế, `--drop 0.05`, `--push 1.0`): `--check` cho sai lệch $\le 2.3\times10^{-5}$ N·m. Các lần chạy này không có `--gait` nên robot không giữ được thăng bằng, **số in ra không phải kết quả tải**.

**Ca tải cần chạy:**
* Các tư thế của §2.1 và các kịch bản của §2.3.
* **Ca té ngã và va đập** (`--drop`, `--push`). Với chi tiết in, đây thường là ca tải lớn nhất, lớn hơn nhiều so với lúc đi.

**Lưu ý khi đọc kết quả:**
1. Lực va chạm trong MuJoCo phụ thuộc mạnh vào `solref`/`solimp` của tiếp xúc và vật liệu đế chân. Số ở ca té ngã và va đập **chỉ dùng để so tương đối** giữa các thiết kế (§1.5, bước 3), không coi là tải tuyệt đối.
2. Hệ trục của kết quả là frame link trong MJCF. Trước khi đặt tải trong SolidWorks, phải xác định frame này trên chi tiết CAD. Nếu xuất MJCF bằng `sw_urdf_exporter` (§1.4) thì frame link trùng hệ tọa độ đặt trong SolidWorks.
3. Mỗi khớp cho tải tại **một mặt cắt** (giữa link cha và link con). Một chi tiết in thường nối hai khớp, nên lấy tải ở cả hai khớp và kiểm tra cả hai đầu.

## 2.5. Đo servo thật để chốt
Mua 1–2 con mỗi ứng viên về đo, dùng chung bàn thử với §4.5.3:
* **$\tau_{stall}$:** gắn tay đòn dài $L$, treo tải $m$, có $\tau = mgL$. Tăng tải dần cho tới khi servo không giữ được nữa. Ghi lại cả dòng điện.
* **Đường $\tau$–$\omega$:** đo thời gian servo kéo các mức tải khác nhau qua một góc cố định, suy ra $\omega$. Đo ở **áp pin thật khi có tải**.
* **Mô hình actuator cho sim:** đo backlash, ma sát và độ trễ (xem §4.5.3); microduck_rl và xgoduck_rl làm việc này bằng BAM (Better Actuator Models), ví dụ `1910_m6.json`. Thay các thông số đo được vào MJCF, chạy lại §2.3 rồi mới kết luận chọn ứng viên nào.

**Nếu chỉ vài khớp sát ngưỡng** (thường là knee hoặc hip roll), có hai hướng rẻ hơn nâng cấp cả 15 servo:
* Chỉ đổi servo mạnh hơn cho riêng các khớp đó.
* Sửa hình học chân để giảm cánh tay đòn trọng tâm, rồi chạy lại vòng lặp.

## 2.6. Kết luận Phase 2
- [ ] Đã chạy đủ các kịch bản ở §2.3 cho từng ứng viên.
- [ ] Đã xuất tải 6 thành phần tại các khớp (§2.4), gồm cả ca té ngã và va đập, để kiểm tra bền chi tiết in ở §1.5.
- [ ] Ứng viên đạt cả 3 tiêu chí ở §2.3 với **thông số đo thật** (§2.5) thì đi tiếp sang [Phase 3](Phase3_PhanTich_IO.md).
- [ ] Ứng viên trượt: ghi lại khớp nào trượt, trượt tiêu chí nào. Sau đó đổi servo riêng cho khớp đó hoặc sửa hình học chân rồi quay lại [Phase 1](Phase1_CAD_HocServo.md).
- [ ] Nếu **tải tĩnh** (§2.2) đã vượt khả năng servo thì loại luôn. Phần độ chế ở Phase 4 không tăng được mô-men đủ để bù.

---

← [Phase 1](Phase1_CAD_HocServo.md) · [Phase 3](Phase3_PhanTich_IO.md) →
