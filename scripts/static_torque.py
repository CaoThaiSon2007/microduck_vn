# static_torque.py — mô-men tĩnh từng khớp ở một tư thế cho trước (Phase 2, §2.2)
#
# Chạy (trong thư mục chứa MJCF, vì MJCF tham chiếu mesh theo đường dẫn tương đối):
#   python static_torque.py robot_walk.xml --foot-half 0.030 0.015
#
# --foot-half: nửa chiều dài, nửa chiều rộng đế chân [m] theo trục x, y của site bàn chân.
#              ĐO TRÊN CAD rồi điền. Bỏ trống thì không kiểm tra CoP (in cảnh báo).
import argparse
import sys

import mujoco
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định không in được tiếng Việt

KGFCM = 0.0980665  # 1 kgf·cm = 0.0980665 N·m


def load(path):
    m = mujoco.MjModel.from_xml_path(path)
    d = mujoco.MjData(m)
    # chỉ lấy các khớp có actuator (bỏ free joint của base)
    act_dof = [m.jnt_dofadr[m.actuator_trnid[a, 0]] for a in range(m.nu)]
    act_name = [m.joint(m.actuator_trnid[a, 0]).name for a in range(m.nu)]
    return m, d, act_dof, act_name


def static_torque(m, d, act_dof, pose, stance=("left_foot",), foot_half=None):
    """pose: {tên_khớp: góc_rad}; stance: các site bàn chân đang chạm đất.
    Trả về (tau theo actuator [N·m], wrench f, danh sách CoP_ok hoặc None)."""
    mujoco.mj_resetData(m, d)
    for name, val in pose.items():
        d.qpos[m.joint(name).qposadr[0]] = val
    d.qvel[:] = 0
    mujoco.mj_forward(m, d)
    g = d.qfrc_bias.copy()  # = trọng lực khi qvel = 0

    Jc = []
    for s in stance:
        jp, jr = np.zeros((3, m.nv)), np.zeros((3, m.nv))
        mujoco.mj_jacSite(m, d, jp, jr, m.site(s).id)
        Jc.append(np.vstack([jp, jr]))  # [lực; mô-men] tại site, hệ world
    Jc = np.vstack(Jc)

    # 6 hàng base: g_b = Jc_b^T f
    # 1 chân → 6 ẩn, nghiệm duy nhất; 2 chân → 12 ẩn, lstsq trả nghiệm min-norm (xem Phase 2, lưu ý 2)
    f = np.linalg.lstsq(Jc[:, :6].T, g[:6], rcond=None)[0]
    tau = (g - Jc.T @ f)[act_dof]

    if foot_half is None:
        return tau, f, None
    # Kiểm tra tâm áp lực (CoP) nằm trong đế chân — chỉ có nghĩa khi đứng 1 chân
    cop_ok = []
    for k, s in enumerate(stance):
        F, M = f[6 * k:6 * k + 3], f[6 * k + 3:6 * k + 6]
        if F[2] <= 0:  # đất phải "kéo" chân xuống → tư thế không hợp lệ
            cop_ok.append(False)
            continue
        r_world = np.array([-M[1] / F[2], M[0] / F[2], 0.0])
        r_local = d.site(s).xmat.reshape(3, 3).T @ r_world
        cop_ok.append(abs(r_local[0]) <= foot_half[0] and abs(r_local[1]) <= foot_half[1])
    return tau, f, cop_ok


def main():
    ap = argparse.ArgumentParser(description="Mô-men tĩnh từng khớp (Phase 2, §2.2)")
    ap.add_argument("model", nargs="?", default="robot_walk.xml", help="file MJCF")
    ap.add_argument("--foot-half", nargs=2, type=float, metavar=("HX", "HY"),
                    help="nửa dài, nửa rộng đế chân [m]; bỏ trống = không kiểm tra CoP")
    args = ap.parse_args()

    m, d, act_dof, act_name = load(args.model)
    total_mass = float(m.body_subtreemass[0])
    if args.foot_half is None:
        print("⚠️  Chưa có --foot-half: KHÔNG kiểm tra CoP, mọi tư thế đều được tính.")

    # VÍ DỤ: quét độ ngồi xổm, đứng 1 chân trái.
    # Tên khớp và site theo MJCF XGO-Duck (xgoduck_rl). DẤU GÓC là GIẢ ĐỊNH:
    # mở viewer kiểm tra chiều gập gối/hông và đế chân trụ có nằm phẳng không trước khi tin kết quả.
    worst = np.zeros(m.nu)
    for knee in np.linspace(0.0, 1.2, 25):
        pose = {"left_knee": knee, "left_hip_pitch": -knee / 2, "left_ankle": -knee / 2,
                "right_knee": 0.6, "right_hip_pitch": -0.3}
        tau, f, ok = static_torque(m, d, act_dof, pose, ("left_foot",), args.foot_half)
        # Kiểm tra cân bằng lực: đứng 1 chân thì F_z phải bằng tổng trọng lượng
        if abs(f[2] - total_mass * abs(m.opt.gravity[2])) > 1e-6 * max(1.0, f[2]):
            print(f"knee={knee:.2f}: F_z = {f[2]:.4f} N ≠ m·g — kiểm tra lại model")
        if ok is not None and not all(ok):
            print(f"knee={knee:.2f}: CoP ngoài đế chân → robot đổ, bỏ tư thế này")
            continue
        worst = np.maximum(worst, np.abs(tau))

    print(f"\nTổng khối lượng model: {total_mass:.3f} kg")
    for i in np.argsort(-worst):
        print(f"{act_name[i]:16s} {worst[i]:7.4f} N·m = {worst[i] / KGFCM:6.2f} kgf·cm")


if __name__ == "__main__":
    main()
