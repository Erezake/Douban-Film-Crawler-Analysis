# 母女题材电影文本分析项目

本仓库包含对 12 部当代中国母女题材电影的跨影片文本分析流程，涵盖数据采集、预处理、筛选、情感分析、关键词挖掘、词频统计和总体汇总等工作。本项目最终服务于大学生创新训练项目的论文撰写与研究论证。

## 1. 项目结构说明

```text
data/
    每部电影一个独立文件夹（如《你好，李焕英》《春潮》《血观音》）
    ├── short_reviews.json       豆瓣短评原始数据
    ├── long_reviews.json        豆瓣长评原始数据
    ├── wordcloud.png            生成的单片词云图
    ├── word_frequencies.csv     单片词频统计表
    ├── sentiment_log.txt        情感分析详细日志
    └── ...
    
filter.py                        数据清洗与母女关系筛选规则
movie_short_review.py            豆瓣短评采集脚本
movie_long_review.py             豆瓣长评采集脚本
wordcloud_gen.py                 词云生成主程序（调用 statistic.py）
statistic.py                     基础统计模块（被调用）
sentiment_topic_analysis.py      核心情感计算（基于 RoBERTa 模型）
sentiment_spectrum_optimized_chinese.py  情感光谱可视化脚本
overall.py                       跨影片汇总分析
organize.py                      文件归档与整理工具
stopwords.txt                    停用词表
requirements.txt                 Python 依赖列表
readme.md                        项目说明文件
```

## 2. 重要配置说明 (Configuration)

在使用爬虫脚本（`movie_short_review.py` 和 `movie_long_review.py`）前，**必须**手动配置请求头，以通过豆瓣的反爬验证。

请打开脚本文件，找到 `headers` 部分并填入你自己的浏览器信息：

```python
# 示例配置（请务必替换为实际值）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/...", 
    "Cookie": "dbcl2=xxxxxx; bid=xxxxxx; ...",
}
```
*注：`User-Agent` 和 `Cookie` 需登录豆瓣网页版后通过浏览器开发者工具（F12 -> Network）获取。*

## 3. 使用方式与工作流程 (Workflow)

本项目严格按照以下顺序执行。请确保上一阶段产出文件后，再执行下一阶段脚本。

### 第一步：数据采集
运行爬虫脚本获取原始评论数据（需先完成 Header 配置）。
```bash
python movie_short_review.py
python movie_long_review.py
```

### 第二步：清洗与筛选
基于关键词规则（如“母女”、“母亲”等）剔除无关噪音，保留核心语料。
```bash
python filter.py
```

### 第三步：分析与计算
执行核心分析任务。
*注：运行 `wordcloud_gen.py` 时会自动调用 `statistic.py` 进行 TF-IDF 计算与分词。*
```bash
python wordcloud_gen.py
python sentiment_topic_analysis.py
```

### 第四步：汇总与绘图
生成跨影片的对比图谱与总体数据表。
```bash
python overall.py
python sentiment_spectrum_optimized_chinese.py
```

### 第五步：整理与归档 (可选)
将散落在根目录的分析结果（图片、CSV、日志）自动移动到 `data/` 下对应的电影子文件夹中，保持目录整洁。
```bash
python organize.py
```

## 4. 主要脚本说明

*   **`filter.py`**
    数据清洗的核心。负责读取原始 JSON，执行正则清洗、MD5 去重及关键词相关性过滤。

*   **`wordcloud_gen.py` & `statistic.py`**
    `statistic.py` 负责底层的 Jieba 分词与 TF-IDF 权重计算；`wordcloud_gen.py` 调用统计结果生成可视化的词云图片。

*   **`sentiment_topic_analysis.py`**
    情感计算核心。基于 `Erlangshen-Roberta-330M-Sentiment` 模型，对筛选后的文本进行情感极性打分，输出日志供人工复核。

*   **`sentiment_spectrum_optimized_chinese.py`**
    可视化专用脚本。绘制 12 部电影的情感分布光谱，直观呈现从“温情”到“压抑”的情绪流动。

*   **`organize.py`**
    项目维护工具。用于在分析结束后，自动化整理输出文件，实现“分门别类”的归档管理。

## 5. 环境配置

建议使用 **Python 3.10+** 版本。

安装项目依赖：
```bash
pip install -r requirements.txt
```

## 6. 输出成果示例

运行结束后，`data/` 目录下将包含以下关键文件：

*   `wordcloud.png`：单部电影的词云图
*   `word_frequencies.csv`：单部电影的高频词统计表
*   `sentiment_log.txt`：情感预测详细记录
*   `movie_sentiment_spectrum.png`：12 部电影情绪光谱汇总图
*   `overall_word_frequencies.csv`：跨影片总体高频词表

## 7. 版权与使用说明

本项目代码与数据仅用于大学生创新训练项目结题及学术研究。
爬取的公开评论数据仅供非商业科研分析使用。