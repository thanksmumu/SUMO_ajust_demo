# Vehicle Brightness Control in SUMO

## 项目概述
本项目基于 [SUMO](https://www.eclipse.org/sumo/) 仿真平台，通过 **TraCI 接口** 实时控制车辆自定义参数 `brightness`（亮度），并根据车辆之间的头距自动调整亮度。项目同时提供 CSV 记录与可视化曲线，用于分析车辆亮度随时间变化情况。

### 功能特点
- 基于车辆对向距离调整亮度：
  - 默认亮度：400 lm  
  - 若两辆对向车辆头距 < 50 m，则降低亮度至 250 lm  
  - 距离 >= 50 m，则恢复至 400 lm  
- 保证亮度边界：[200 lm, 600 lm]  
- 实时更新车辆颜色以可视化亮度变化（浅蓝/深蓝）  
- 记录 CSV 文件，包括时间、车辆、距离和亮度信息  
- 支持离线绘图：
  - 分组绘制 AC、BD 两组车辆亮度随时间变化
  - 中文显示，自动保存高分辨率 PNG 图片

## 文件说明
brightness_control.py # SUMO 仿真实时亮度控制脚本
brightness_log.csv # 仿真记录文件（生成）
plot_brightness.py # Python 可视化脚本
cross.sumocfg # SUMO 仿真配置文件


## 环境依赖
- Python 3.10+  
- SUMO 1.15+  
- Python 库：
  - `traci` （SUMO Python 接口）  
  - `pandas`  
  - `matplotlib`  

安装示例：
```bash
pip install pandas matplotlib
确保系统已安装 SUMO 并将 sumo-gui 或 sumo 命令添加到 PATH。

使用说明
1. 运行仿真并生成亮度记录
python brightness_control.py


脚本会启动 SUMO GUI（或非 GUI），实时控制车辆亮度

仿真完成后，会生成 brightness_log.csv 文件

2. 可视化亮度变化
python plot_brightness.py


脚本会读取 CSV 文件

自动生成两张图片：

车辆亮度_AC.png

车辆亮度_BD.png

图片中显示车辆亮度随仿真时间变化，中文标注