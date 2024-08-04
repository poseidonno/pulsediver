import re

import jieba
from flask import Blueprint, render_template, request, redirect, url_for
import pandas as pd

from MyProject.Processor.auto_summary import generate_summary
from Page_Ranks import calculate_relevance_byTFIDF

search_bp = Blueprint('search', __name__)

file_title = 'E:\Python\搜索引擎实验\MyProject\Processor\index_title.csv'
file_content = 'E:\Python\搜索引擎实验\MyProject\Processor\index_content.csv'
file_data = 'E:\Python\搜索引擎实验\MyProject\Spider\web_pages\scraped_data.csv'





def search_word_in_indices(word, file_title, file_content, file_data):
    # 读取标题和正文倒排索引 CSV 文件
    df_title = pd.read_csv(file_title)
    df_content = pd.read_csv(file_content)
    df_data = pd.read_csv(file_data)

    # 查找词在标题和正文倒排索引中的 'Document IDs'
    title_ids = df_title[df_title['Word'] == word]['DocIDs']
    content_ids = df_content[df_content['Word'] == word]['DocIDs']

    if title_ids.empty and content_ids.empty:
        return []
    elif title_ids.empty:
        content_ids = content_ids.values[0]
        content_id_set = set(map(int, content_ids.split(', ')))
        return list(content_id_set)
    elif content_ids.empty:
        title_ids = title_ids.values[0]
        title_id_set = set(map(int, title_ids.split(', ')))
        return list(title_id_set)
    else:
        title_ids = title_ids.values[0]
        content_ids = content_ids.values[0]
        title_id_set = set(map(int, title_ids.split(', ')))
        content_id_set = set(map(int, content_ids.split(', ')))
        merged_ids = list(title_id_set.union(content_id_set))
        return merged_ids

def highlight_keywords(summary, keywords):
    text = summary
    for keyword in keywords:
        text = text.replace(keyword,f'<em style="font-weight: bold; color: red;">{keyword}</em>')
    return text

def tokenize_text_with_jieba(text):
    # 保留中文、英文和数字单词
    filtered_words = [word for word in jieba.lcut(text) if re.match(r'[\u4e00-\u9fffA-Za-z0-9]+', word)]
    return filtered_words

def search(query):
    # 使用jieba对用户输入的内容进行分词处理，保留中文、英文和数字单词
    query_tokens = tokenize_text_with_jieba(query)

    # 根据词得到索引词对应文档id的字典
    index_dict = {}
    for word in query_tokens:
        merged_ids = search_word_in_indices(word, file_title, file_content, file_data)
        index_dict[word] = merged_ids

    # 计算相关度并获取相关度排序后的文档结果
    sorted_documents = calculate_relevance_byTFIDF(query_tokens, index_dict)

    # 获取相关度排序后的文档结果
    results = []
    if sorted_documents:
        df_data = pd.read_csv(file_data)
        merged_results = df_data[df_data['ID'].isin(sorted_documents)][['ID', 'Title', 'URL']]
        results = merged_results.to_dict(orient='records')
        print(sorted_documents)


        # 生成摘要
        summaries = {}
        for result in results:
            text = df_data[df_data['ID'] == result['ID']]['Text'].values[0]
            summary = generate_summary(text, query)
            summaries[result['ID']] = summary

        # 应用摘要和进行标题关键词高亮处理
        for result in results:
            result['Summary'] = highlight_keywords(summaries[result['ID']], query_tokens)
            # 对标题进行关键词高亮处理
            highlighted_title = highlight_keywords(result['Title'], query_tokens)
            result['Highlighted_Title'] = highlighted_title


search("微信小程序")