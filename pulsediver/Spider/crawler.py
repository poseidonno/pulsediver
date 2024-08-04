import csv
import datetime
import os
import random
import re
from collections import deque

import gevent

import gevent.monkey
import unicodedata

# 打开gevent的猴子补丁，使得网络库的请求变为非阻塞
gevent.monkey.patch_all()

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# start_urls = ['https://www.51cto.com/',
#               'https://www.iteye.com/', 'https://www.cnblogs.com/',
#               'http://www.blogjava.net/', 'https://blog.csdn.net/']
base_domains = ['https://blog.csdn.net','https://www.51cto.com','https://www.cnblogs.com']
# 创建一个目录来存储下载的网页
if not os.path.exists("web_pages"):
    os.makedirs("web_pages")

# 定义正则表达式来匹配标题、正文和链接
title_pattern = re.compile(r'<title>(.*?)</title>', re.IGNORECASE)
text_pattern = re.compile(r'<p>(.*?)</p>', re.IGNORECASE)
link_pattern = re.compile(r'href=["\'](https?://.*?)(?=["\'])', re.IGNORECASE)
url_pattern = re.compile(r'^(https?://)?(www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(/\S*)?$')
# time_pattern = re.compile(r'<time.*?>(.*?)</time>', re.IGNORECASE)
# 不同的 User-Agent 头
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/88.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/14.0.3',
    # 添加其他 User-Agent 头
]
# 随机选择一个 User-Agent 头
user_agent = random.choice(user_agents)
headers = {'User-Agent': user_agent}

# 禁止爬取的文件后缀词汇列表
FILE_WORDS = ['.gif', '.png', '.bmp', '.jpeg', '.jpg', '.svg',
              '.mp3', '.wma', '.flv', '.mp4', '.wmv', '.ogg', '.avi',
              '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.pdf',
              '.zip', '.exe', '.tat', '.ico', '.css', '.js', '.swf', '.apk', '.m3u8', '.do', '.ts', '.xml']



# 获取现有数据的最后一个ID
def get_last_id(csv_file_path):
    last_id = 0
    data_found = False  # 添加一个标志来检查是否找到数据
    if os.path.isfile(csv_file_path):
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # 跳过表头
            next(reader, None)
            # 遍历CSV文件找到最后一行的ID
            for row in reader:
                last_id = int(row[0])  # 假设ID是第一列
                data_found = True  # 标记为找到数据
        if not data_found:
            return 0  # 如果文件为空，则ID从0开始
        else:
            return last_id   # 返回最后一个ID
    else:
        return 0  # 文件不存在时，ID从0开始
# 提取信息并保存到CSV文件（协程版本）
def extract_and_save_info_coroutine(url, writer, current_id):
    try:
        response = requests.get(url, headers=headers, timeout=3)  # 设置超时时间为3秒
        if response.status_code == 200:
            html_text = response.text

            # 提取标题
            title_match = title_pattern.search(html_text)
            title = title_match.group(1) if title_match else "No Title"

            # 提取正文并进行清洗
            soup = BeautifulSoup(html_text, 'html.parser')
            paragraphs = soup.find_all('p')
            text = "\n".join(p.get_text() for p in paragraphs)
            cleaned_text = clean_text(text)

            # 提取链接并以逗号分隔
            links = link_pattern.findall(html_text)
            links = filter_links(links)
            links_str = ", ".join(links)

            # 提取发布时间
            #---------------------------------

            # 写入到CSV文件中
            writer.writerow([current_id, url, title, cleaned_text, links_str])
        else:
            print(f"Failed to fetch {url}")
    except requests.Timeout:  # 处理超时异常
        print(f"Timeout occurred for {url}. Skipping...")
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")


# 广度优先搜索来爬取网页（协程版本）
def BFS_gevent(start_url, max_pages):
    csv_file_path = 'web_pages/scraped_data.csv'
    urls_file_path = 'web_pages/visited_urls.txt'

    # 读取已经访问的 URL 列表
    visited_urls = load_visited_urls(urls_file_path)

    mode = 'a' if os.path.isfile(csv_file_path) else 'w'

    # 获取最后一个ID
    last_id = get_last_id(csv_file_path)
    current_id = last_id + 1

    with open(csv_file_path, mode, newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if mode == 'w':
            writer.writerow(["ID", "URL", "Title", "Text", "Links"])

        queue = deque([(start_url, 0)])
        page_counter = 0

        while queue:
            current_url, depth = queue.popleft()

            if current_url not in visited_urls and is_valid_domain(current_url):
                gevent.spawn(extract_and_save_info_coroutine, current_url, writer, current_id)
                current_id += 1
                visited_urls.add(current_url)  # 将当前 URL 加入已访问集合
                page_counter += 1
                print(f"Page {page_counter} downloaded: {current_url}")

                if page_counter >= max_pages:
                    break

                try:
                    response = requests.get(current_url, headers=headers, timeout=3)
                    if response.status_code == 200:
                        html_text = response.text
                        links = link_pattern.findall(html_text)
                        links = filter_links(links)
                        for link in links:
                            absolute_link = urljoin(current_url, link)
                            if absolute_link not in visited_urls:
                                queue.append((absolute_link, depth + 1))
                    else:
                        print(f"Failed to fetch {current_url}")
                except requests.Timeout:
                    print(f"Timeout occurred for {current_url}. Skipping...")
                except Exception as e:
                    print(f"Error processing {current_url}: {str(e)}")

        # 写入已访问的 URL 到文件中
        with open(urls_file_path, 'w', encoding='utf-8') as visited_urls_file:
            visited_urls_file.write('\n'.join(visited_urls))

    print(f"Finished crawling {len(visited_urls)} pages.")

#文本清洗
def clean_text(text):
    # 过滤掉表情符号
    try:
        co = re.compile(u'['u'\U0001F300-\U0001F64F' u'\U0001F680-\U0001F6FF'u'\u2600-\u2B55]+')
    except re.error:
        co = re.compile(u'('u'\ud83c[\udf00-\udfff]|'u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'u'[\u2600-\u2B55])+')

    cleaned_text = co.sub('', text)
    cleaned_text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # 将多个连续空白字符替换为单个空格
    cleaned_text = re.sub(r'\n+', ' ', cleaned_text)  # 将换行符替换为空格
    return cleaned_text.strip()  # 去除文本两端的空格

# URL 过滤函数，排除特定后缀的链接
def filter_links(links):
    filtered_links = []
    for link in links:
        if not any(ext in link for ext in FILE_WORDS):
            filtered_links.append(link)
    return filtered_links

# 检验url是否有效
def is_valid_url(url):
    if bool(url_pattern.match(url)):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return 0
        except (requests.exceptions.RequestException, ValueError):
            return -2
    else:
        return -1
def is_valid_domain(url):
    global base_domains
    parsed_url = urlparse(url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return any(domain in base_domain for base_domain in base_domains)
def load_visited_urls(visited_urls_path):
    visited_urls = set()
    if os.path.isfile(visited_urls_path):
        with open(visited_urls_path, 'r', encoding='utf-8') as visited_urls_file:
            visited_urls = set(visited_urls_file.read().splitlines())
    return visited_urls

# 主程序入口
if __name__ == "__main__":
    # start_url = random.choice(start_urls)

    start_url = input("初始网址：")
    if is_valid_url(start_url) == 0:
        max_pages = int(input("请输入需要爬取的网页数量:"))
        print("开始爬取.....")

        BFS_gevent(start_url, max_pages)
    elif is_valid_url(start_url) == -1:
        print("URL格式错误，请重试")
    else:
        print("URL地址无效")