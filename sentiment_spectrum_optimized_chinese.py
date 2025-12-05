import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

# --- 关键改进：指定中文字体文件 ---
# 你需要根据自己的操作系统，将下面的路径替换为一个真实存在的中文字体文件路径
# Windows 示例: 'C:/Windows/Fonts/simhei.ttf' (黑体)
# macOS 示例: '/System/Library/Fonts/STHeiti Light.ttc' (华文细黑)
# Linux 示例: '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc' (Noto Sans CJK)

# 为了让代码更具通用性，这里我们先尝试自动查找常见的中文字体
def find_chinese_font():
    font_paths = [
        'C:/Windows/Fonts/simhei.ttf',
        'C:/Windows/Fonts/simsun.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/System/Library/Fonts/STSong.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
    ]
    for path in font_paths:
        try:
            font = FontProperties(fname=path)
            # 尝试一个中文字符来验证字体是否有效
            plt.text(0, 0, '测试', fontproperties=font)
            plt.close() # 关闭临时图表
            print(f"成功找到并设置字体: {path}")
            return path
        except:
            continue
    return None

# 自动查找字体
font_path = find_chinese_font()

if font_path:
    # 使用 FontProperties 对象来指定字体
    chinese_font = FontProperties(fname=font_path)
    # 同时，也设置全局字体，以便某些情况下（如图例）也能生效
    plt.rcParams['font.family'] = chinese_font.get_name()
else:
    print("警告：未找到系统中的中文字体，请手动在代码中指定 'font_path'。")
    #  fallback 方案，可能无法正常显示中文
    chinese_font = FontProperties()

# 解决负号显示问题
plt.rcParams['axes.unicode_minus'] = False

# -------------------------- 数据准备 --------------------------
movies = [
    "《女孩》", "《妈妈和七天的时间》", "《过春天》", "《瀑布》",
    "《妈妈！》", "《你好，李焕英》", "《送我上青云》", "《春潮》",
    "《好东西》", "《血观音》", "《出走的决心》", "《还有明天》"
]
pos_pct = [52.32, 51.09, 51.43, 49.22, 46.95, 45.98, 42.75, 41.45, 40.03, 39.54, 39.18, 38.11]
neg_pct = [47.68, 48.91, 48.57, 50.78, 53.05, 54.02, 57.25, 58.55, 59.97, 60.46, 60.82, 61.89]

# -------------------------- 绘图配置 --------------------------
fig, ax = plt.subplots(figsize=(16, 9))
x = np.arange(len(movies))
width = 0.35

color_pos = '#2E86AB'
color_neg = '#E25822'

bar1 = ax.bar(x - width/2, pos_pct, width, label='正面情绪',
              color=color_pos, alpha=0.8, edgecolor='white', linewidth=1)
bar2 = ax.bar(x + width/2, neg_pct, width, label='负面情绪',
              color=color_neg, alpha=0.8, edgecolor='white', linewidth=1)

# -------------------------- 标签优化 --------------------------
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom',
                fontsize=10, fontweight='bold', color='black')

add_labels(bar1)
add_labels(bar2)

# -------------------------- 坐标轴和标题优化 --------------------------
# 在需要显示中文的地方，通过 fontproperties 参数传入我们定义的字体
ax.set_title('12部电影的情绪分布光谱', fontproperties=chinese_font,
             fontsize=18, fontweight='bold', pad=20)
ax.text(0.5, 1.02, '从左到右：正面情绪占比逐渐降低，负面情绪占比逐渐升高',
        transform=ax.transAxes, ha='center', fontproperties=chinese_font,
        fontsize=12, color='#666666')

ax.set_ylabel('情绪占比 (%)', fontproperties=chinese_font,
              fontsize=14, fontweight='bold', labelpad=15)
ax.set_xlabel('电影名称', fontproperties=chinese_font,
              fontsize=14, fontweight='bold', labelpad=15)

ax.set_xticks(x)
ax.set_xticklabels(movies, rotation=45, ha='right', fontproperties=chinese_font, fontsize=11)

ax.set_ylim(0, 80)
ax.set_yticks(np.arange(0, 81, 10))
ax.grid(axis='y', linestyle='--', alpha=0.3, color='#999999')

# -------------------------- 图例和边框优化 --------------------------
# 图例的字体设置
ax.legend(loc='upper right', fontsize=12, frameon=True,
          facecolor='white', edgecolor='#DDDDDD', framealpha=0.8,
          prop=chinese_font) # 使用 prop 参数

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#DDDDDD')
ax.spines['bottom'].set_color('#DDDDDD')

# -------------------------- 布局调整 --------------------------
plt.tight_layout(rect=[0, 0, 1, 0.96])

# -------------------------- 保存图片 --------------------------
plt.savefig('movie_sentiment_spectrum_optimized_chinese.png', dpi=300, bbox_inches='tight')
plt.show()