import os
import shutil
from pathlib import Path

# -------------------------- 核心配置 --------------------------
# 脚本所在目录（自动获取，无需修改）
SCRIPT_DIR = Path(__file__).parent
# 电影数据根目录（data文件夹路径，适配你的结构）
DATA_ROOT = SCRIPT_DIR / "data"

# 分类规则（中文文件夹名 + 对应文件，保持不变）
CATEGORY_MAP = {
    "原始评论数据": [
        "all_comments.json",   # 合并后的所有评论
        "long_reviews.json",   # 电影长评
        "short_reviews.json"   # 电影短评
    ],
    "情感分析结果": [
        "comment_sentiment.csv"  # 每条评论的情感（正面/负面）结果表
    ],
    "主题词与词频分析结果": [
        "comment_keywords.csv",  # 评论高频主题词统计
        "comment_keywords.png",  # 主题词柱状图
        "word_frequencies.csv",  # 词语出现频率统计
        "word_frequencies.png",  # 词频可视化图表
        "wordcloud.png"          # 评论关键词词云图
    ],
    "分析过程日志": [
        "analysis_log.txt",  # 之前脚本生成的分析日志
        "_日志.txt"          # 匹配其他带“_日志”的记录文件
    ]
}



def organize_single_movie(movie_folder):
    """整理单个电影文件夹的文件"""
    movie_name = os.path.basename(movie_folder)
    print(f"\n=====================================")
    print(f"开始整理《{movie_name}》的文件...")
    print(f"文件夹路径：{movie_folder}")
    print("=====================================")

    # 遍历电影文件夹下的所有文件（跳过已有的分类文件夹）
    for filename in os.listdir(movie_folder):
        file_path = os.path.join(movie_folder, filename)
        # 跳过子文件夹（避免重复处理）
        if os.path.isdir(file_path):
            # 如果是之前生成的分类文件夹，先清空（避免重复文件）
            if filename in CATEGORY_MAP.keys():
                shutil.rmtree(file_path)
            continue

        # 匹配文件对应的分类文件夹
        target_category = None
        for category, file_patterns in CATEGORY_MAP.items():
            for pattern in file_patterns:
                if pattern in filename:
                    target_category = category
                    break
            if target_category:
                break

        # 移动文件到对应分类文件夹
        if target_category:
            # 创建分类文件夹（不存在则新建）
            category_folder = os.path.join(movie_folder, target_category)
            os.makedirs(category_folder, exist_ok=True)
            # 移动文件（覆盖同名文件）
            target_path = os.path.join(category_folder, filename)
            shutil.move(file_path, target_path)
            print(f"→ 已移动：{filename} → {target_category}")
        else:
            print(f"⚠️ 未匹配到分类：{filename}（暂不移动）")

    # 生成README文档
    print(f"✅ 《{movie_name}》整理完成！")


def main():
    # 检查data目录是否存在
    if not os.path.exists(DATA_ROOT):
        print(f"❌ 未找到data目录！路径：{DATA_ROOT}")
        print("请确认脚本放在 Douban-MovieReview-Crawler 文件夹下，且data目录存在")
        return

    # 获取data目录下的所有电影文件夹（子文件夹）
    movie_folders = [
        os.path.join(DATA_ROOT, folder)
        for folder in os.listdir(DATA_ROOT)
        if os.path.isdir(os.path.join(DATA_ROOT, folder))
    ]

    if not movie_folders:
        print(f"❌ data目录下未找到任何电影文件夹！路径：{DATA_ROOT}")
        print("请将电影文件夹（如“你好，李焕英”）放在data目录下")
        return

    # 显示找到的电影文件夹
    print(f"📁 已找到 {len(movie_folders)} 个电影文件夹：")
    for i, folder in enumerate(movie_folders, 1):
        print(f"  {i}. {os.path.basename(folder)}")

    # 询问用户是否批量整理所有
    choice = input("\n是否整理所有电影文件夹？（y=是，n=只整理第一个）：").strip().lower()
    if choice != "y":
        movie_folders = [movie_folders[0]]  # 只整理第一个
        print(f"\n🔧 仅整理：{os.path.basename(movie_folders[0])}")

    # 批量整理每个电影文件夹
    for folder in movie_folders:
        organize_single_movie(folder)

    print("\n🎉 所有选中的电影文件夹整理完成！")
    print(f"👉 结果路径：{DATA_ROOT}")
    print("文科同学直接打开电影文件夹，按README说明查看即可~")


if __name__ == "__main__":
    main()