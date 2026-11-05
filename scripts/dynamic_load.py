# dynamic_load.py — log mô-men / tốc độ khớp khi chạy quỹ đạo (Phase 2, §2.3)
#
# Chạy (trong thư mục chứa MJCF; dùng scene có sàn, ví dụ scene_walk.xml của xgoduck_rl):
#   python dynamic_load.py scene_walk.xml                        # giữ tư thế mặc định (smoke test)
#   python dynamic_load.py scene_walk.xml --gait my_gait:q_ref   # quỹ đạo từ module của dự án
#
# my_gait.py phải có hàm q_ref(t: float, m: mujoco.MjModel) -> np.ndarray (m.nu,) góc mục tiêu [rad].
#
# Mặc định script NỚI forcerange của mọi actuator (--force-limit), vì MJCF của XGO đặt sẵn
# ±1.04 N·m: nếu giữ nguyên, mô-men bị cắt và kết quả nhìn như servo "đủ" (Checklist Phase 2).
import argparse
import importlib
import sys

import mujoco
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Tải động từng khớp (Phase 2, §2.3)")
    ap.add_argument("model", help="file MJCF có sàn")
    ap.add_argument("--gait", help="module:hàm sinh góc mục tiêu, ví dụ my_gait:q_ref")
    ap.add_argument("--settle", type=float, default=1.0, help="thời gian ổn định trước khi log [s]")
    ap.add_argument("--run", type=float, default=10.0, help="thời gian log [s]")
    ap.add_argument("--force-limit", type=float, default=100.0,
                    help="forcerange mới cho mọi actuator [N·m]; 0 = giữ nguyên MJCF")
    ap.add_argument("--kp", type=float, default=0.0,
                    help="kp mới cho actuator <position> [N·m/rad] để bám quỹ đạo cứng; 0 = giữ nguyên MJCF")
    ap.add_argument("--out", default="load_log.npz", help="file lưu log để vẽ đồ thị τ–ω")
    args = ap.parse_args()

    m = mujoco.MjModel.from_xml_path(args.model)
    d = mujoco.MjData(m)
    if args.force_limit > 0:
        m.actuator_forcerange[:] = [-args.force_limit, args.force_limit]
        m.actuator_forcelimited[:] = 1
    if args.kp > 0:  # actuator <position>: force = kp·ctrl − kp·q − kv·q̇
        m.actuator_gainprm[:, 0] = args.kp
        m.actuator_biasprm[:, 1] = -args.kp

    act_dof = [m.jnt_dofadr[m.actuator_trnid[a, 0]] for a in range(m.nu)]
    act_name = [m.joint(m.actuator_trnid[a, 0]).name for a in range(m.nu)]

    if args.gait:
        mod, fn = args.gait.split(":")
        q_ref = getattr(importlib.import_module(mod), fn)
    else:
        print("⚠️  Không có --gait: giữ tư thế mặc định (chỉ để kiểm tra script chạy được).")
        q0 = np.zeros(m.nu)
        q_ref = lambda t, m: q0  # noqa: E731

    tau_log, w_log = [], []
    n = int((args.settle + args.run) / m.opt.timestep)
    for k in range(n):
        t = k * m.opt.timestep
        d.ctrl[:] = q_ref(t, m)
        mujoco.mj_step(m, d)
        if t >= args.settle:
            tau_log.append(d.actuator_force.copy())
            w_log.append(d.qvel[act_dof].copy())
    tau, w = np.array(tau_log), np.array(w_log)

    sat = np.abs(tau) >= 0.999 * np.abs(m.actuator_forcerange[:, 1])
    if sat.any():
        print("⚠️  Có actuator chạm forcerange — tăng --force-limit rồi chạy lại.")

    print(f"{'khớp':16s} {'τ_peak':>8s} {'τ_RMS':>8s} {'ω_max':>8s}   (N·m, N·m, rad/s)")
    for i, name in enumerate(act_name):
        print(f"{name:16s} {np.abs(tau[:, i]).max():8.4f} {np.sqrt((tau[:, i] ** 2).mean()):8.4f} "
              f"{np.abs(w[:, i]).max():8.3f}")
    np.savez(args.out, tau=tau, w=w, names=act_name, dt=m.opt.timestep)


if __name__ == "__main__":
    main()
