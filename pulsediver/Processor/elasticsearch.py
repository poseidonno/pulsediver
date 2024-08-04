import ast
import time

import pandas as pd
import jieba.analyse
import re

def extract_keywords(text, min_length=20):
    if len(text) < min_length:
        filtered_words = [word for word in jieba.lcut(text) if re.match(r'[\u4e00-\u9fffA-Za-z0-9]+', word)]
        return filtered_words
    else:
        return jieba.analyse.extract_tags(text, topK=10)

def build_inverted_index(documents):
    index_title = {}
    index_content = {}

    total_docs = len(documents)
    for idx, doc in enumerate(documents, start=1):
        title = doc["Title"]
        keywords_title = extract_keywords(title)
        for word in keywords_title:
            if word not in index_title:
                index_title[word] = set()
            index_title[word].add(idx)

        content = doc["Text"]
        keywords_content = extract_keywords(content)
        for word in keywords_content:
            if word not in index_content:
                index_content[word] = set()
            index_content[word].add(idx)

        # 打印进度信息
        print(f"处理进度：{idx}/{total_docs}")

    print("\n处理完成！")

    return index_title, index_content

def import_and_build_index(file_path):
    # 读取 CSV 文件
    data = pd.read_csv(file_path)

    # 提取标题和正文列
    documents = data[["Title", "Text"]].fillna('')  # 选择标题和正文列，并处理缺失值

    # 去掉字典值部分的花括号


    # 建立倒排索引
    index_title, index_content = build_inverted_index(documents.to_dict('records'))

    # 转换为 DataFrame
    df_title = pd.DataFrame(index_title.items(), columns=['Word', 'DocIDs'])
    df_content = pd.DataFrame(index_content.items(), columns=['Word', 'DocIDs'])

    # 将倒排索引保存到CSV文件前去除value的花括号
    df_title['DocIDs'] = df_title['DocIDs'].apply(lambda x: ', '.join(map(str, x)))
    df_content['DocIDs'] = df_content['DocIDs'].apply(lambda x: ', '.join(map(str, x)))
    # 将倒排索引保存到CSV文件
    df_title.to_csv('index_title.csv', index=False)
    df_content.to_csv('index_content.csv', index=False)

    print("标题倒排索引已保存到 index_title.csv")
    print("正文倒排索引已保存到 index_content.csv")

# 使用新的方法导入CSV文件并建立倒排索引
file_path = r'E:\Python\搜索引擎实验\MyProject\Spider\web_pages\scraped_data.csv'
start_time = time.time()
import_and_build_index(file_path)
#计算执行时间
end_time = time.time()
execution_time = end_time - start_time
print(f"程序执行时间为：{execution_time} 秒")


def search_word_in_indices(word, file_title, file_content, file_data):
    # 读取标题和正文倒排索引 CSV 文件
    df_title = pd.read_csv(file_title)
    df_content = pd.read_csv(file_content)

    # 查找词在标题倒排索引中的 'Document IDs'
    title_ids = df_title[df_title['Word'] == word]['DocIDs']
    content_ids = df_content[df_content['Word'] == word]['DocIDs']
    if title_ids.empty and content_ids.empty:
        return print(f"未找到 '{word}'的相关结果")
    elif title_ids.empty:
        print("标题中未找到相关信息，但在正文里寻找到了")
        content_ids = content_ids.values[0]
        # 读取原始数据文件
        df_data = pd.read_csv(file_data)
        content_id_set = set(map(int, content_ids.split(', ')))

        merged_ids = list(content_id_set)

    elif content_ids.empty:
        print("正文中未找到相关信息，但在标题里寻找到了")
        title_ids = title_ids.values[0]
        # 读取原始数据文件
        df_data = pd.read_csv(file_data)
        title_id_set = set(map(int, title_ids.split(', ')))
        merged_ids = list(title_id_set)
    else:
        title_ids = title_ids.values[0]
        content_ids = content_ids.values[0]
        # 查找词在正文倒排索引中的 'Document IDs'

        # 读取原始数据文件
        df_data = pd.read_csv(file_data)

        # 获取标题和正文结果集的 'ID'
        title_id_set = set(map(int, title_ids.split(', ')))
        content_id_set = set(map(int, content_ids.split(', ')))

        # 计算并集
        merged_ids = list(title_id_set.union(content_id_set))
    print(f"为您查找到相关【{len(merged_ids)}】条记录")
        # 在原始数据文件中查找对应 'ID' 的 'Title' 和 'URL'
    merged_results = df_data[df_data['ID'].isin(merged_ids)][['ID', 'Title', 'URL']]

    print("\n汇总处理后的结果：")
    print(merged_results.to_string(index=False))

# 测试方法
# file_title = 'index_title.csv'
# file_content = 'index_content.csv'
# file_data = r'E:\Python\搜索引擎实验\MyProject\Spider\web_pages\scraped_data.csv'
#
# word_to_search = input("请输入要查找的词：")
# search_word_in_indices(word_to_search, file_title, file_content, file_data)
