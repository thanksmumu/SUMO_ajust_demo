import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ---------------- 中文字体设置 ----------------
rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 中文字体
rcParams['axes.unicode_minus'] = False             # 负号正常显示

# ---------------- 读取 CSV ----------------
df = pd.read_csv("brightness_log.csv")

# 提取车辆
vehicles = pd.unique(df[['veh1', 'veh2']].values.ravel())
colors = {'A': 'red', 'B': 'blue', 'C': 'green', 'D': 'orange'}

# 分组：AC 一组，BD 一组
groups = {
    'AC': ['A', 'C'],
    'BD': ['B', 'D']
}

# 绘图并保存
for group_name, group_vehicles in groups.items():
    plt.figure(figsize=(10, 6))
    
    for veh in group_vehicles:
        mask1 = df['veh1'] == veh
        mask2 = df['veh2'] == veh

        # 合并时间和亮度，并重置索引
        time = pd.concat([df.loc[mask1, 'time'], df.loc[mask2, 'time']]).reset_index(drop=True)
        brightness = pd.concat([df.loc[mask1, 'veh1_brightness'], df.loc[mask2, 'veh2_brightness']]).reset_index(drop=True)

        # 按时间排序
        data = pd.DataFrame({'时间': time, '亮度': brightness}).sort_values('时间')

        plt.plot(data['时间'], data['亮度'], label=f'车辆 {veh}', color=colors.get(veh, 'black'))

    # 设置中文标题和坐标轴
    plt.xlabel("仿真时间 (秒)")
    plt.ylabel("车辆亮度 (流明)")
    plt.title(f"{group_name} 组车辆亮度随时间变化")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # 保存图片
    plt.savefig(f"车辆亮度_{group_name}.png", dpi=300)
    plt.close()  # 关闭图，避免显示

print("绘图完成，图片已保存到当前目录。")
