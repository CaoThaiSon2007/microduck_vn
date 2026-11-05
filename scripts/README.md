# scripts/

Script tính tải servo cho [Phase 2](../Phase2_MoPhong_TaiServo.md).

| File | Việc | Mục |
|---|---|---|
| `static_torque.py` | Mô-men tĩnh từng khớp ở một tư thế, kiểm tra CoP và cân bằng lực | §2.2 |
| `dynamic_load.py` | Chạy quỹ đạo trong MuJoCo, log $\tau(t)$, $\omega(t)$, in $\tau_{peak}$, $\tau_{RMS}$, $\omega_{max}$ | §2.3 |

## Cài đặt
```
python -m venv .venv
.venv\Scripts\activate          # Windows; Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```
Đã thử với Python 3.11 và MuJoCo 3.17.0 (05/11/2026).

## Lấy MJCF baseline HD1910
MJCF của XGO-Duck nằm trong [xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl). File MJCF tham chiếu mesh theo đường dẫn tương đối, nên phải chạy script **từ trong thư mục model**:
```
git clone https://github.com/LuwuDynamics/xgoduck_rl
cd xgoduck_rl/src/mjlab_microduck/robot/xgoduck
python <repo này>/scripts/static_torque.py robot_walk.xml --foot-half <HX> <HY>
python <repo này>/scripts/dynamic_load.py scene_walk.xml --gait my_gait:q_ref --kp 20
```
* `robot_walk.xml`: robot không có sàn, dùng cho tính tĩnh.
* `scene_walk.xml`: có sàn, dùng cho mô phỏng động.

## Lưu ý
* Tên khớp/site trong ví dụ theo MJCF XGO-Duck. **Dấu góc trong ví dụ là giả định.** Kiểm tra trong viewer trước khi dùng kết quả.
* Số in ra khi chạy không có `--gait` hoặc không có `--foot-half` chỉ để kiểm tra script, **không phải kết quả tải**.
* Mô hình 3D và MJCF của upstream có giấy phép riêng. Xem [UPSTREAM.md của XGO](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/UPSTREAM.md).
