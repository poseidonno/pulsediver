import csv
from urllib.parse import urlparse

# 定义顶级域名列表
top_level_domains = ['.com', '.net', '.org', '.gov', '.edu']  # 这里列举了几个常见的顶级域名


def calculate_domain_importance(url):
    # 去掉"http://"或"https://"
    parsed_url = urlparse(url)
    path_without_protocol = parsed_url.path[parsed_url.path.find('/') + 1:]

    # 计算链接深度
    depth = path_without_protocol.count('/')

    # 解析域名部分
    domain_parts = parsed_url.netloc.split('.')
    domain_level = len(domain_parts)  # 计算域名级别

    # 判断顶级域名是否在列表中，并给予相应加分
    top_level_bonus = 0
    for top_level in top_level_domains:
        if top_level in domain_parts:
            top_level_bonus = 1  # 假设顶级域名在列表中则加分

    # 根据深度和域名级别计算重要度分数，加上顶级域名的加分
    importance_score = max(1 - depth * 0.1, 0) + (4 - domain_level) * 0.25 + top_level_bonus

    return importance_score


if __name__ == "__main__":
    csv_file_path = r'E:\Python\搜索引擎实验\MyProject\Spider\web_pages\scraped_data.csv'

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            url = row['URL']  # 获取CSV中的URL列
            importance_score = calculate_domain_importance(url)  # 计算URL的重要性分数
            print(f"URL: {url}, Importance Score: {importance_score}")
