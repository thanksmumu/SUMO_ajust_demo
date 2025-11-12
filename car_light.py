#!/usr/bin/env python3
"""
brightness_control.py
- 使用 TraCI 在仿真运行时按规则改变车辆自定义参数 'brightness'
- 规则:
    基准 brightness = 400 lm
    若两对向车辆头距 < 50 m -> 将双方 brightness 设为 250 lm
    若间距 >= 50 m -> 恢复为 400 lm
- 记录 CSV: time, veh1, veh2, distance_m, veh1_brightness, veh2_brightness
"""

import traci
import traci.constants as tc
import csv
import math
import os
import sys
from datetime import datetime

# ---------- 配置（按需调整） ----------
SUMO_BINARY = "sumo-gui"   # 或 "sumo"（无 GUI）
SUMO_CFG = "cross.sumocfg"

# 车辆对（你想监控的对向车辆对）
# A 与 B 是东西向对向车辆； C 与 D 是南北向对向车辆
VEH_PAIR_LIST = [("A", "B"), ("C", "D")]

# 参数值
BRIGHTNESS_BASE = 400      # 基准 400 lm
BRIGHTNESS_LOW = 250       # 当距离 < 50m 时设置为 250 lm
BRIGHTNESS_MIN = 200       # 最低 200 lm（边界）
BRIGHTNESS_MAX = 600       # 最高 600 lm（边界）
DISTANCE_THRESHOLD = 50.0  # 米

# 日志文件
LOG_CSV = "brightness_log.csv"

# ---------- 帮助函数 ----------
def clamp_brightness(val):
    """确保亮度在 [BRIGHTNESS_MIN, BRIGHTNESS_MAX] 范围内, 返回 int"""
    if val is None:
        return BRIGHTNESS_BASE
    v = int(round(val))
    if v < BRIGHTNESS_MIN:
        return BRIGHTNESS_MIN
    if v > BRIGHTNESS_MAX:
        return BRIGHTNESS_MAX
    return v

def euclidean_distance(pos1, pos2):
    """pos = (x, y)"""
    return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])

# ---------- 主逻辑 ----------
def main():
    # 删除旧日志
    if os.path.exists(LOG_CSV):
        os.remove(LOG_CSV)

    # 启动 SUMO（GUI 或 非 GUI）
    sumo_cmd = [SUMO_BINARY, "-c", SUMO_CFG]
    print(f"[{datetime.now()}] Starting SUMO with: {' '.join(sumo_cmd)}")
    traci.start(sumo_cmd)

    # 打开 CSV 写入
    with open(LOG_CSV, mode="w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["time", "veh1", "veh2", "distance_m", "veh1_brightness", "veh2_brightness"])

        try:
            step = 0
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
                sim_time = traci.simulation.getTime()
                step += 1

                for (v1, v2) in VEH_PAIR_LIST:
                    # 检查车辆是否存在于仿真中
                    try:
                        # 若车辆尚未进入仿真, getPosition 会抛出异常
                        pos1 = traci.vehicle.getPosition(v1)  # (x, y)
                        pos2 = traci.vehicle.getPosition(v2)
                    except traci.TraCIException:
                        # 车辆不在仿真中（还未出发或已离开） -> 记录空行并跳过
                        continue

                    # 计算距离（欧氏距离）
                    dist = euclidean_distance(pos1, pos2)

                    # 判定并设置目标亮度
                    if dist < DISTANCE_THRESHOLD:
                        target_brightness = BRIGHTNESS_LOW
                    else:
                        target_brightness = BRIGHTNESS_BASE

                    # 保证边界
                    target_brightness = clamp_brightness(target_brightness)

                    # 将亮度写入车辆自定义参数：使用 traci.vehicle.setParameter
                    # param 名称我们使用 "brightness"（字符串）
                    try:
                        traci.vehicle.setParameter(v1, "brightness", str(target_brightness))
                        traci.vehicle.setParameter(v2, "brightness", str(target_brightness))
                    except traci.TraCIException:
                        # 有可能该车辆处于不允许更改参数的状态，捕获并继续
                        pass

                    # 把亮度映射到车辆颜色以便 GUI 可视化：
                    # 这里简单地把亮度映射到黄色/白色的亮度感知（非物理）
                    # 映射方法：brightness 200->暗，600->亮。生成 RGB 三元组（0-255）
                    try:
                        # 将亮度映射为蓝色深浅
                        def brightness_to_rgb(br):
                            """
                            根据亮度返回蓝色调颜色：
                            - 亮度高（>=400）：亮蓝（浅蓝色）
                            - 亮度低（<400）：深蓝
                            """
                            if br < BRIGHTNESS_BASE:
                                # 深蓝：亮度越低，颜色越暗
                                # 250流明 → 深蓝 (0, 0, 100)
                                # 200流明 → 更暗 (0, 0, 80)
                                factor = (br - BRIGHTNESS_MIN) / (BRIGHTNESS_BASE - BRIGHTNESS_MIN)
                                blue_val = int(80 + 20 * factor)  # 在80~100之间
                                return (255, 255, blue_val, 255)
                            else:
                                # 浅蓝：亮度越高，颜色越亮
                                # 400流明 → 亮蓝 (0, 150, 255)
                                # 600流明 → 更亮蓝 (100, 200, 255)
                                factor = (br - BRIGHTNESS_BASE) / (BRIGHTNESS_MAX - BRIGHTNESS_BASE)
                                r = int(0 + 100 * factor)
                                g = int(150 + 50 * factor)
                                b = 0
                                return (r, 255, b, 255)

                        color = brightness_to_rgb(target_brightness)
                        traci.vehicle.setColor(v1, color)
                        traci.vehicle.setColor(v2, color)
                    except traci.TraCIException:
                        pass

                    # 记录日志
                    writer.writerow([f"{sim_time:.2f}", v1, v2, f"{dist:.3f}", target_brightness, target_brightness])

        except Exception as e:
            print(f"[{datetime.now()}] Exception during simulation: {e}")
        finally:
            traci.close()
            print(f"[{datetime.now()}] SUMO closed. Log saved to {LOG_CSV}")

if __name__ == "__main__":
    main()
