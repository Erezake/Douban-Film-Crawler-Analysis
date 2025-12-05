import json
from filter import filter_mother_daughter
from statistic import MovieReviewStatistic
import os
import pandas as pd
import sys


# ----------------- 日志记录器 -----------------
class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


# ----------------- 数据读取函数 -----------------
def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def load_csv(path, content_col):
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df.fillna("")
        return [{"content": str(x)} for x in df[content_col].tolist()]
    return []


# ----------------- 主逻辑 -----------------
def main():
    movie_name = input("请输入电影名称：").strip()

    # 日志文件名称
    log_filename = f"./data/{movie_name}/{movie_name}_母女关系分析日志.txt"
    sys.stdout = Logger(log_filename)

    print(f"当前电影：{movie_name}")
    print("开始处理数据...\n")

    # 读取短评、长评、小红书
    short_path = f'./data/{movie_name}/short_reviews.json'
    long_path = f'./data/{movie_name}/long_reviews.json'
    xhs_comment_path = f'./data/{movie_name}/xhs_comments.csv'
    xhs_search_path = f'./data/{movie_name}/xhs_contents.csv'

    short_comments = load_json(short_path)
    long_comments = load_json(long_path)
    xhs_comments = load_csv(xhs_comment_path, "content")
    xhs_search_contents = load_csv(xhs_search_path, "desc")

    print(f"豆瓣短评：{len(short_comments)} 条")
    print(f"豆瓣长评：{len(long_comments)} 条")
    print(f"小红书评论：{len(xhs_comments)} 条")
    print(f"小红书搜索内容：{len(xhs_search_contents)} 条\n")

    # 母女关系过滤
    filtered_short = filter_mother_daughter(short_comments)
    filtered_long = filter_mother_daughter(long_comments)
    filtered_xhs_comments = filter_mother_daughter(xhs_comments)
    filtered_xhs_search = filter_mother_daughter(xhs_search_contents)

    print("-------- 母女关系相关评论统计 --------")
    print(f"豆瓣短评相关：{len(filtered_short)}")
    print(f"豆瓣长评相关：{len(filtered_long)}")
    print(f"小红书评论相关：{len(filtered_xhs_comments)}")
    print(f"小红书搜索结果相关：{len(filtered_xhs_search)}")

    # 合并全部来源的评论
    all_filtered_comments = (
        filtered_short +
        filtered_long +
        filtered_xhs_comments +
        filtered_xhs_search
    )

    print(f"\n总的母女关系相关评论：{len(all_filtered_comments)}")
    print("--------------------------------------\n")

    # 调用统计模块
    stat = MovieReviewStatistic(movie_name, all_filtered_comments)
    stat.stastic_star()
    stat.statistic_comment()

    print("\n分析完成。日志已保存。")


if __name__ == '__main__':
    main()
