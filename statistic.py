import jieba
import jieba.analyse
from wordcloud import WordCloud
import pandas as pd
import matplotlib.pyplot as plt
import os

class MovieReviewStatistic:
    def __init__(self, movie_name, comments_dict):
        self.movie_name = movie_name
        self.comments_dict = comments_dict
        self.length = len(comments_dict)
        self.stars_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0} # 初始化一个字典来存储每个星级的评论数量
        # 读取文件中的停用词列表
        with open('stopwords.txt', 'r', encoding='utf-8') as file:
            self.stopwords = set(file.read().splitlines())

    def stastic_star(self):
        all_star = 0
        all_val = 0

        for comment in self.comments_dict:
            # ------------- 新增：跳过没有星级的评论 -------------
            if 'stars' not in comment or comment['stars'] in ["", None]:
                continue
            # ----------------------------------------------------

            try:
                stars = int(comment['stars'])
            except:
                continue

            upvote = int(comment.get('upvote', 1))  # 长评可能没有点赞，默认给 1

            if stars == 0:
                continue

            self.stars_count[stars] += 1
            all_star += stars * upvote
            all_val += 5 * upvote

        # for star in sorted(self.stars_count.keys()):
        #     print(f"星级 {star} 的评论数量: {self.stars_count[star]}")
        #
        # if all_val == 0:
        #     print("无可计算的星级评论（所有长评都没有星级）")
        #     return
        #
        # star_avg = (all_star / all_val) * 5
        # print(f"点赞加权的平均星级: {star_avg:.2f}")

    def statistic_comment(self):
        # 初始化一个空列表来存储处理后的文本
        processed_strings = []

        # 预处理每个评论内容，并将其添加到processed_strings列表中
        for comment in self.comments_dict:
            # 提取关键词并用空格连接
            keywords = ' '.join(jieba.analyse.extract_tags(comment['content'], topK=20, withWeight=False))
            # 将处理后的文本添加到列表中
            processed_strings.append(keywords)

        # 将所有处理后的文本连接成一个单独的字符串
        string = ' '.join(font for font in processed_strings if font not in self.stopwords)

        # 创建词云对象，并生成词云
        wc = WordCloud(
            background_color='white',
            width=1000,
            height=800,
            font_path = r'C:\Windows\Fonts\SIMSUN.TTC',  # 指定字体路径
            stopwords=self.stopwords,
            max_words=250  # 显示的最大词数
        )

        # 生成词云
        wc.generate(string)
        wc.to_file(f'./data/{self.movie_name}/wordcloud.png')  # 保存词云图片

        # 使用matplotlib显示词云图
        plt.figure(figsize=(10, 8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')  # 不显示坐标轴
        plt.show()

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_dir = os.path.join(base_dir, "data", self.movie_name)
        os.makedirs(save_dir, exist_ok=True)

        # 创建保存目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_dir = os.path.join(os.getcwd(), "data", self.movie_name)
        os.makedirs(save_dir, exist_ok=True)

        # 统计词频
        word_frequencies = wc.words_  # 归一化频率
        total_words = sum([len(comment.get("content", "").split()) for comment in self.comments_dict])
        if total_words == 0:
            print("没有可计算的词频内容")
            return

        data = []
        for word, weight in word_frequencies.items():
            count = int(weight * total_words)
            data.append({
                "word": word,
                "count": count,
                "weight": weight,
                "proportion": count / total_words
            })

        df = pd.DataFrame(data).sort_values("count", ascending=False)
        csv_path = os.path.join(save_dir, "word_frequencies.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"词频 CSV 已保存：{csv_path}")

        # 绘制柱状图
        top_n = 50
        top_df = df.head(top_n)
        plt.figure(figsize=(15, 8))
        plt.bar(top_df['word'], top_df['count'], width=0.5, color=plt.cm.viridis(range(top_n)))
        plt.xticks(rotation=45, ha='right', fontproperties='SimSun')
        plt.yticks(fontsize=12)
        plt.ylabel("出现次数", fontproperties='SimSun', fontsize=12)
        plt.title(f"{self.movie_name} 母女关系词云词频统计（前{top_n}）", fontproperties='SimSun', fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        chart_path = os.path.join(save_dir, "word_frequencies.png")
        plt.savefig(chart_path)
        plt.show()
        print(f"柱状图已保存：{chart_path}")
        