import os
import json
import jieba
import jieba.analyse
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter


# ----------------- 数据读取 -----------------
def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


# ----------------- 主逻辑 -----------------
def main():
    print("开始汇总所有电影的 overall 评论数据...\n")

    base_dir = "./data"
    if not os.path.exists(base_dir):
        print("未找到 data 目录，程序退出。")
        return

    # 加载停用词
    if os.path.exists("stopwords.txt"):
        with open("stopwords.txt", "r", encoding="utf-8") as f:
            stopwords = set(f.read().splitlines())
    else:
        stopwords = set()

    all_comments = []

    # ----------------- 遍历所有电影文件夹 -----------------
    for movie in os.listdir(base_dir):
        movie_dir = os.path.join(base_dir, movie)
        if not os.path.isdir(movie_dir):
            continue

        json_path = os.path.join(movie_dir, "原始评论数据", "all_comments.json")

        if not os.path.exists(json_path):
            print(f"[跳过] 未找到：{json_path}")
            continue

        print(f"[读取] {json_path}")
        comments = load_json(json_path)

        for c in comments:
            content = c.get("content", "").strip()
            if content:
                all_comments.append(content)

    print(f"\n共载入评论：{len(all_comments)} 条")

    if len(all_comments) == 0:
        print("没有任何评论可用于统计，程序结束。")
        return

    # ----------------- 提取关键词并合并成语料 -----------------
    processed_strings = []
    for text in all_comments:
        kws = " ".join(jieba.analyse.extract_tags(text, topK=20, withWeight=False))
        processed_strings.append(kws)

    full_text = " ".join([w for w in processed_strings if w not in stopwords])

    # ----------------- 生成词云 -----------------
    wc = WordCloud(
        background_color="white",
        width=1000,
        height=800,
        font_path=r"C:\Windows\Fonts\SIMSUN.TTC",
        stopwords=stopwords,
        max_words=200
    )

    try:
        wc.generate(full_text)
    except ValueError:
        print("词云生成失败：文本为空。")
        return

    # 保存词云
    plt.figure(figsize=(12, 9))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("overall_keywords.png", dpi=300)
    plt.close()
    print("已保存 overall_keywords.png")

    # ----------------- 词频统计 -----------------
    word_freq = wc.words_     # 归一化权重
    total_words = sum(len(c.split()) for c in all_comments)

    data = []
    for word, weight in word_freq.items():
        count = int(weight * total_words)
        data.append({
            "word": word,
            "count": count,
            "weight": weight,
            "proportion": count / total_words if total_words else 0
        })

    df = pd.DataFrame(data).sort_values("count", ascending=False)
    df.to_csv("overall_word_frequencies.csv", index=False, encoding="utf-8-sig")
    print("已保存 overall_word_frequencies.csv")

    # ----------------- 绘制柱状图 -----------------
    top_n = 50
    top_df = df.head(top_n)

    plt.figure(figsize=(16, 8))
    plt.bar(top_df["word"], top_df["count"], width=0.5, color=plt.cm.viridis(range(top_n)))
    plt.xticks(rotation=45, ha="right", fontproperties="SimSun")
    plt.ylabel("出现次数", fontproperties="SimSun")
    plt.title(f"总体词频统计（前 {top_n}）", fontproperties="SimSun")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig("overall_word_frequencies.png", dpi=400)
    plt.close()

    print("已保存 overall_word_frequencies.png")
    print("\n整体分析完成。")


if __name__ == "__main__":
    main()
