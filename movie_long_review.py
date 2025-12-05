import requests
from lxml import etree
import re
import time as t
import random
import os
import json


def get_html(url):
    headers = {
        "User-Agent": "",
        "Cookie": "",
    }
    return requests.get(url=url, headers=headers).text


def get_movie_id(movie_name):
    url = f'https://search.douban.com/movie/subject_search?search_text={movie_name}'

    response_text = get_html(url)
    # 使用正则表达式提取 "id" 和 "title"
    pattern = r'"id":\s*(\d+).*?"title":\s*"([^"]+)"'

    matches = re.findall(pattern, response_text)

    # 将结果转换为字典
    result = {int(match[0]): match[1].encode().decode('unicode_escape') for match in matches}

    return result


def get_movie_longreviews(movie_id, max_pages=5):
    """
    抓取长评列表（不抓全文，先抓ID与标题）
    max_pages: 抓多少页，每页 20 条
    """
    reviews = []
    for page in range(max_pages):
        start = page * 20
        url = f'https://movie.douban.com/subject/{movie_id}/reviews?start={start}'
        print("长评列表页：", url)

        html = get_html(url)
        tree = etree.HTML(html)

        items = tree.xpath('//div[@class="main review-item"]')
        if not items:
            break

        for it in items:
            review_id = it.xpath('./@id')[0].split('_')[-1]  # review_item id="review_12345"
            title = it.xpath('.//h2/a/text()')[0].strip()
            link = it.xpath('.//h2/a/@href')[0]
            reviews.append({
                'id': review_id,
                'title': title,
                'url': link
            })

        t.sleep(random.uniform(1, 2))

    return reviews

def get_longreview_content(url):
    """
    抓取单篇长评全文
    """
    html = get_html(url)
    tree = etree.HTML(html)

    paragraphs = tree.xpath('//div[@class="review-content clearfix"]//p/text()')
    text = "\n".join(p.strip() for p in paragraphs if p.strip())
    return text

def get_all_longreviews(movie_id):
    review_list = get_movie_longreviews(movie_id)

    long_reviews = []
    for r in review_list:
        print("抓取长评全文：", r['url'])
        content = get_longreview_content(r['url'])
        long_reviews.append({
            "title": r["title"],
            "url": r["url"],
            "content": content
        })
        t.sleep(random.uniform(1, 2))

    print(f"共抓到 {len(long_reviews)} 篇长评")
    return long_reviews


def save_long_reviews(movie_name, reviews):
    dir_path = f'./data/{movie_name}'
    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, 'long_reviews.json'), 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=4)


def main():
    movie_name = input("请输入电影名称：")
    movie_id_dict = get_movie_id(movie_name)

    for index, movie_id in enumerate(movie_id_dict):
        print(f"{index+1}. {movie_id_dict[movie_id]}")

    movie_index = int(input("请输入电影ID："))
    movie_id = list(movie_id_dict.keys())[movie_index-1]

    # 只抓长评，不做任何统计
    comments_dict = get_all_longreviews(movie_id)
    save_long_reviews(movie_name, comments_dict)

    print(f"长评已保存，共 {len(comments_dict)} 条")
    print("请运行 wordcloud_gen.py 来生成母女关系词云图。")


if __name__ == '__main__':
    main()