import json
import os
import jieba
import jieba.analyse
import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline
from collections import Counter
from pathlib import Path  # 用于跨平台路径处理


# ----------------- 辅助功能：日志记录 -----------------
def log_info(message, log_file):
    """打印信息并写入日志文件"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + '\n')


# ----------------- 评论合并功能 -----------------
def merge_movie_comments():
    # 输入验证（过滤空值和非法字符）
    while True:
        movie_name = input("请输入电影名称：").strip()
        invalid_chars = r'\/:*?"<>|'
        if not movie_name:
            print("错误：电影名称不能为空！")
        elif any(char in invalid_chars for char in movie_name):
            print(f"错误：电影名称不能包含这些字符：{invalid_chars}")
        else:
            break

    # 路径设置
    data_dir = Path("./data") / movie_name / "原始评论数据"
    output_file = data_dir / "all_comments.json"
    log_file = data_dir / f"{movie_name}_情感分析日志.txt"

    try:
        # 确保数据目录存在
        data_dir.mkdir(parents=True, exist_ok=True)

        # 初始化日志文件（清空已有内容）
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"电影《{movie_name}》评论分析日志\n")
            f.write("=" * 50 + "\n")

        # 初始化所有评论列表
        all_comments = []

        # 1. 读取短评JSON
        short_file = data_dir / "short_reviews.json"
        if short_file.exists():
            with open(short_file, "r", encoding="utf-8") as f:
                short_comments = json.load(f)
                # 标准化为列表格式
                if isinstance(short_comments, list):
                    all_comments.extend(short_comments)
                else:
                    all_comments.append(short_comments)
            log_info(f"已读取短评文件：{short_file}，共 {len(short_comments)} 条", log_file)
        else:
            log_info(f"警告：未找到短评文件 {short_file}，将跳过", log_file)

        # 2. 读取长评JSON
        long_file = data_dir / "long_reviews.json"
        if long_file.exists():
            with open(long_file, "r", encoding="utf-8") as f:
                long_comments = json.load(f)
                # 标准化为列表格式
                if isinstance(long_comments, list):
                    all_comments.extend(long_comments)
                else:
                    all_comments.append(long_comments)
            log_info(f"已读取长评文件：{long_file}，共 {len(long_comments)} 条", log_file)
        else:
            log_info(f"警告：未找到长评文件 {long_file}，将跳过", log_file)

        # 3. 读取小红书评论CSV（content列）
        xhs_comments_file = data_dir / "xhs_comments.csv"
        if xhs_comments_file.exists():
            try:
                df_xhs_comments = pd.read_csv(xhs_comments_file, encoding="utf-8")
                # 检查是否存在content列
                if "content" in df_xhs_comments.columns:
                    # 提取非空内容并转换为字典列表
                    xhs_comments = [
                        {"content": str(content).strip()}
                        for content in df_xhs_comments["content"]
                        if pd.notna(content) and str(content).strip()
                    ]
                    all_comments.extend(xhs_comments)
                    log_info(f"已读取小红书评论CSV：{xhs_comments_file}，共 {len(xhs_comments)} 条", log_file)
                else:
                    log_info(f"警告：{xhs_comments_file} 中未找到 'content' 列，将跳过", log_file)
            except Exception as e:
                log_info(f"读取 {xhs_comments_file} 出错：{str(e)}，将跳过", log_file)
        else:
            log_info(f"警告：未找到小红书评论文件 {xhs_comments_file}，将跳过", log_file)

        # 4. 读取小红书内容CSV（desc列）
        xhs_contents_file = data_dir / "xhs_contents.csv"
        if xhs_contents_file.exists():
            try:
                df_xhs_contents = pd.read_csv(xhs_contents_file, encoding="utf-8")
                # 检查是否存在desc列
                if "desc" in df_xhs_contents.columns:
                    # 提取非空内容并转换为字典列表
                    xhs_contents = [
                        {"content": str(desc).strip()}
                        for desc in df_xhs_contents["desc"]
                        if pd.notna(desc) and str(desc).strip()
                    ]
                    all_comments.extend(xhs_contents)
                    log_info(f"已读取小红书内容CSV：{xhs_contents_file}，共 {len(xhs_contents)} 条", log_file)
                else:
                    log_info(f"警告：{xhs_contents_file} 中未找到 'desc' 列，将跳过", log_file)
            except Exception as e:
                log_info(f"读取 {xhs_contents_file} 出错：{str(e)}，将跳过", log_file)
        else:
            log_info(f"警告：未找到小红书内容文件 {xhs_contents_file}，将跳过", log_file)

        # 去重处理（按content字段）
        unique_comments = list(
            {comment['content']: comment for comment in all_comments if 'content' in comment}.values())

        # 保存合并结果
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_comments, f, ensure_ascii=False, indent=2)

        log_info(f"\n合并完成！共 {len(unique_comments)} 条有效评论（已去重），已保存到 {output_file}", log_file)
        return movie_name, output_file, log_file  # 返回日志文件路径

    except json.JSONDecodeError as e:
        error_msg = f"错误：JSON 文件格式非法（{e}），请检查文件内容"
        print(error_msg)
        return None, None, None
    except PermissionError:
        error_msg = "错误：没有文件读写权限，请检查目录权限"
        print(error_msg)
        return None, None, None
    except Exception as e:
        error_msg = f"意外错误：{str(e)}"
        print(error_msg)
        return None, None, None


# ----------------- 情感与主题词分析功能 -----------------
def analyze_comments(movie_name, comments_file, log_file):
    if not movie_name or not comments_file or not os.path.exists(comments_file) or not log_file:
        print("评论文件或日志文件不存在，无法进行分析")
        return

    log_info(f"\n开始情感与主题词分析：电影《{movie_name}》", log_file)

    DATA_DIR = os.path.dirname(comments_file)
    STOPWORDS_FILE = "stopwords.txt"

    # 读取评论
    with open(comments_file, 'r', encoding='utf-8') as f:
        comments = json.load(f)

    # 读取停用词
    try:
        with open(STOPWORDS_FILE, 'r', encoding='utf-8') as f:
            stopwords = set(f.read().splitlines())
        log_info(f"已加载停用词文件：{STOPWORDS_FILE}", log_file)
    except FileNotFoundError:
        log_info(f"警告：未找到停用词文件 {STOPWORDS_FILE}，将不使用停用词过滤", log_file)
        stopwords = set()

    # 加载模型
    import time
    start_time = time.time()
    classifier = pipeline(
        "sentiment-analysis",
        model="IDEA-CCNL/Erlangshen-Roberta-330M-Sentiment"
    )
    load_time = time.time() - start_time
    log_info(f"Loading model cost {load_time:.6f} seconds.", log_file)

    jieba.initialize()
    log_info("Prefix dict has been built succesfully.", log_file)

    # -------- 情感分析 ---------
    sentiment_list = []
    sentiment_count = Counter()

    for comment in comments:
        text = comment.get("content", "").strip()
        if not text:
            continue

        result = classifier(text[:128])[0]
        label = result["label"].lower()
        score = result["score"]
        sentiment = "positive" if label == "positive" else "negative"

        sentiment_list.append({
            "content": text,
            "sentiment": sentiment,
            "score": score
        })
        sentiment_count[sentiment] += 1

    # 保存情感结果
    df_sentiment = pd.DataFrame(sentiment_list)
    csv_path = os.path.join(DATA_DIR, "comment_sentiment.csv")
    df_sentiment.to_csv(csv_path, index=False, encoding="utf-8-sig")
    log_info(f"\n情感分析结果 CSV 已保存：{csv_path}", log_file)

    total_comments = len(sentiment_list)
    for k, v in sentiment_count.items():
        log_info(f"{k} 评论: {v} 条，占比 {v / total_comments:.2%}", log_file)

    # -------- 主题词分析 ---------
    log_info("\n开始提取主题关键词...", log_file)

    all_keywords = []
    for comment in comments:
        text = comment.get("content", "").strip()
        if text:
            kws = jieba.analyse.extract_tags(text, topK=20, withWeight=False)
            kws = [k for k in kws if k not in stopwords]
            all_keywords.extend(kws)

    if all_keywords:
        keyword_counts = pd.Series(all_keywords).value_counts()
        top_n = 30
        top_keywords = keyword_counts.head(top_n)

        csv_kw_path = os.path.join(DATA_DIR, "comment_keywords.csv")
        top_keywords.to_csv(csv_kw_path, header=["count"], encoding="utf-8-sig")
        log_info(f"主题词频 CSV 已保存：{csv_kw_path}", log_file)

        # 柱状图
        plt.figure(figsize=(12, 6))
        plt.bar(top_keywords.index, top_keywords.values, width=0.5, color=plt.cm.viridis(range(top_n)))
        plt.xticks(rotation=45, ha='right', fontproperties='SimSun')
        plt.ylabel("出现次数", fontproperties='SimSun')
        plt.title(f"{movie_name} 评论主题词前{top_n}", fontproperties='SimSun')
        plt.tight_layout()
        chart_path = os.path.join(DATA_DIR, "comment_keywords.png")
        plt.savefig(chart_path)
        plt.close()
        log_info(f"主题词柱状图已保存：{chart_path}", log_file)
    else:
        log_info("未提取到有效关键词，无法生成主题词分析结果", log_file)

    log_info("\n评论分析全部完成！", log_file)

# ----------------- 主程序 -----------------
if __name__ == "__main__":
    # 1. 合并评论
    movie_name, comments_file, log_file = merge_movie_comments()
    # 2. 分析评论
    if movie_name and comments_file and log_file:
        analyze_comments(movie_name, comments_file, log_file)