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

def get_movie_review_by_url(url):
    comments_dict = []

    tree = etree.HTML(get_html(url))

    comment_list = tree.xpath('//div[@class="comment-item"]')
    if len(comment_list) == 0:
        return comments_dict
    
    for comment_div in comment_list:
        try:
            name = comment_div.xpath('.//span[@class="comment-info"]/a/text()')[0].strip()
        except:
            name = ''
        try:
            content = comment_div.xpath('.//p[@class="comment-content"]/span/text()')[0].strip()
        except:
            continue
        upvote = comment_div.xpath('.//span[@class="votes vote-count"]/text()')[0].strip()
        time = comment_div.xpath('.//span[@class="comment-time"]/@title')[0]
        try:
            location = comment_div.xpath('.//span[@class="comment-location"]/text()')[0].strip()
        except:
            location = ''
        
        try:
            star_attribute = comment_div.xpath('.//span[contains(@class,"rating")]/@class')[0]
            stars = re.search(r'\d+', star_attribute).group()[0]
        except:
            stars = 0

        comments_dict.append({
            'name': name,
            'content': content,
            'upvote': upvote,
            'time': time,
            # 'location': location,
            'stars': stars
        })

    return comments_dict

def get_movie_review(movie_id):
    comments = []
    limit = 20
    types = ["h", "m", "l"]  # 好评 中评 差评

    for percent_type in types:
        page = 0
        while True:
            url = (
                f'https://movie.douban.com/subject/{movie_id}/comments?'
                f'percent_type={percent_type}&start={page}&limit={limit}&sort=new_score&status=P'
            )
            print(url)

            tmp = get_movie_review_by_url(url)
            if not tmp:
                break

            comments.extend(tmp)
            page += limit
            t.sleep(random.uniform(1, 2))

    print("==================影评获取完毕===================")
    print(f'共获取 {len(comments)} 条影评')
    return comments

def save_movie_review(movie_name, comments_dict):
    dir_path = f'./data/{movie_name}'
    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, 'short_reviews.json'), 'w', encoding='utf-8') as f:
        json.dump(comments_dict, f, ensure_ascii=False, indent=4)

def main():
    movie_name = input("请输入电影名称：")
    movie_id_dict = get_movie_id(movie_name)

    for index, movie_id in enumerate(movie_id_dict):
        print(f"{index+1}. {movie_id_dict[movie_id]}")

    movie_index = int(input("请输入电影ID："))
    movie_id = list(movie_id_dict.keys())[movie_index-1]

    # 只抓短评，不做任何统计
    comments_dict = get_movie_review(movie_id)
    save_movie_review(movie_name, comments_dict)

    print(f"短评已保存，共 {len(comments_dict)} 条")
    print("请运行 wordcloud_gen.py 来生成母女关系词云图。")


if __name__ == '__main__':
    main()