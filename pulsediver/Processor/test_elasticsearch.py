import ast
import time
import pandas as pd
import jieba.analyse
import re
import os

def extract_keywords(text, min_length=20):
    if len(text) < min_length:
        filtered_words = [word for word in jieba.lcut(text) if re.match(r'[\u4e00-\u9fff]+', word)]
        return filtered_words
    else:
        return jieba.analyse.extract_tags(text, topK=10)

def append_to_index(file_path, file_title, file_content):
    documents = pd.read_csv(file_path)[["Title", "Text"]].fillna('')
    index_title, index_content = build_inverted_index(documents.to_dict('records'))

    df_title = pd.read_csv(file_title)
    df_content = pd.read_csv(file_content)

    title_index = dict(zip(df_title['Word'], df_title['DocIDs'].apply(lambda x: set(map(int, x.split(', '))))))
    content_index = dict(zip(df_content['Word'], df_content['DocIDs'].apply(lambda x: set(map(int, x.split(', '))))))

    for word, doc_id_set in index_title.items():
        if word in title_index:
            title_index[word].update(doc_id_set)
        else:
            title_index[word] = doc_id_set

    for word, doc_id_set in index_content.items():
        if word in content_index:
            content_index[word].update(doc_id_set)
        else:
            content_index[word] = doc_id_set

    df_title = pd.DataFrame({'Word': list(title_index.keys()), 'DocIDs': [', '.join(map(str, doc_ids)) for doc_ids in title_index.values()]})
    df_content = pd.DataFrame({'Word': list(content_index.keys()), 'DocIDs': [', '.join(map(str, doc_ids)) for doc_ids in content_index.values()]})

    df_title.to_csv(file_title, index=False)
    df_content.to_csv(file_content, index=False)
    print("追加完成")
    print(1)

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

        print(f"处理进度：{idx}/{total_docs}")

    print("\n处理完成！")
    print(0)

    return index_title, index_content

def import_and_build_index(file_path):
    file_title = 'index_title.csv'
    file_content = 'index_content.csv'

    if os.path.exists(file_title) and os.path.exists(file_content):
        append_to_index(file_path, file_title, file_content)
    else:
        documents = pd.read_csv(file_path)[["Title", "Text"]].fillna('')
        index_title, index_content = build_inverted_index(documents.to_dict('records'))

        df_title = pd.DataFrame(index_title.items(), columns=['Word', 'DocIDs'])
        df_content = pd.DataFrame(index_content.items(), columns=['Word', 'DocIDs'])

        df_title['DocIDs'] = df_title['DocIDs'].apply(lambda x: ', '.join(map(str, x)))
        df_content['DocIDs'] = df_content['DocIDs'].apply(lambda x: ', '.join(map(str, x)))

        df_title.to_csv(file_title, index=False)
        df_content.to_csv(file_content, index=False)

        print("标题倒排索引已保存到 index_title.csv")
        print("正文倒排索引已保存到 index_content.csv")

file_path = r'E:\Python\搜索引擎实验\MyProject\Spider\web_pages\scraped_data.csv'
start_time = time.time()
import_and_build_index(file_path)
end_time = time.time()
execution_time = end_time - start_time
print(f"程序执行时间为：{execution_time} 秒")

# 测试方法
# file_title = 'index_title.csv'
# file_content = 'index_content.csv'
# file_data = r'E:\Python\搜索引擎实验\MyProject\Spider\web_pages\scraped_data.csv'
#
# word_to_search = input("请输入要查找的词：")
# search_word_in_indices(word_to_search, file_title, file_content, file_data)