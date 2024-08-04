import re
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import jieba
from flask import Blueprint, render_template, request, redirect, url_for
import pandas as pd

from MyProject.Processor.auto_summary import generate_summary
from MyProject.Server.Utils.pinyin2hanzi import extract_pinyin, get_pinyin2hanzi
from Utils.Page_Ranks import calculate_relevance_with_pagerank, sort_pagerank
from Utils.Page_Ranks import calculate_relevance
from Utils.Page_Ranks import calculate_relevance_byTFIDF
from Utils.cut_onechardoc import process_dictionary

search_bp = Blueprint('search', __name__)

file_title = 'E:\Python\搜索引擎实验\MyProject\Processor\index_title.csv'
file_content = 'E:\Python\搜索引擎实验\MyProject\Processor\index_content.csv'
file_data = 'E:\Python\搜索引擎实验\MyProject\Spider\web_pages\scraped_data.csv'
MAX_SUMMARY_LENGTH = 125  # 设置摘要的最大长度



@lru_cache(maxsize=None)
def load_csv(file_path):
    return pd.read_csv(file_path)

# 预加载数据
df_title = load_csv(file_title)
df_content = load_csv(file_content)
df_data = load_csv(file_data)

def search_word_in_indices(word):
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

def search_words_parallel(query_tokens):
    with ThreadPoolExecutor() as executor:
        results = executor.map(search_word_in_indices, query_tokens)
    return list(results)

def highlight_keywords(summary, keywords):
    text = str(summary)  # 确保text是字符串类型
    for keyword in keywords:
        text = text.replace(keyword, f'<em style="font-weight: bold; color: red;">{keyword}</em>')
    return text

def tokenize_text_with_jieba(text):
    # 保留中文、英文和数字单词
    filtered_words = [word for word in jieba.lcut(text) if re.match(r'[\u4e00-\u9fffA-Za-z0-9]+', word)]
    # 限制分词数量不超过18个
    filtered_words = filtered_words[:18]

    return filtered_words

@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    page = int(request.args.get('page', 1))  # 从查询参数中获取页码，默认为第一页
    results_per_page = 10  # 设置每页显示的结果数

    #使用jieba对用户输入的内容进行分词处理，保留中文、英文和数字单词
    query_tokens = tokenize_text_with_jieba(query)
    print(query_tokens)
    pinyin_list = extract_pinyin(query_tokens)
    print(pinyin_list)

    if pinyin_list:
        pinyin2hanzi_list = get_pinyin2hanzi(pinyin_list)
        if pinyin2hanzi_list:
            query_tokens += pinyin2hanzi_list

    start_time = time.time()
    # 根据词得到索引词对应文档id的字典
    index_dict = {}
    for word in query_tokens:
        merged_ids = search_word_in_indices(word)
        # merged_ids = search_word_in_indices(word, file_title, file_content, file_data)
        index_dict[word] = merged_ids

    # 获取网页排序后的文档结果

    # # 根据pr值进行排序
    # # sorted_documents = sort_pagerank(all_related_documents,file_data)
    # # 默认输出（最快1s-3s）
    # sorted_documents = list

    # 根据相关度以及pr值进行排序
    # sorted_documents = calculate_relevance_with_pagerank(query_tokens, index_dict, file_data)

    #使用tf-idf计算相关度排序
    # 构建文档字典
    all_related_documents = set().union(*index_dict.values())
    make_doc = df_data['ID'].isin(all_related_documents)
    selected_data = df_data[make_doc][['ID', 'Title', 'Text']]
    # 将选定的数据转换为字典列表
    documents = {}
    for _, row in selected_data.iterrows():
        doc_id = row['ID']
        documents[doc_id] = {
            'title': row['Title'],
            'content': row['Text']
        }
    #停用词文档切分
    index_dict_cutted, stop_words = process_dictionary(index_dict)
    print(stop_words)
    sorted_documents = calculate_relevance_byTFIDF(query_tokens, index_dict_cutted, documents) + stop_words
    print(sorted_documents)
    # 根据相关度进行排序，速度最快（0.05-0.15s），相关度效果不咋样
    # sorted_documents = calculate_relevance(query_tokens,index_dict)
    # print(sorted_documents)


    #分页处理
    start_idx = (page - 1) * results_per_page
    end_idx = page * results_per_page

    paginated_results = sorted_documents[start_idx:end_idx]

    if paginated_results:
        # 从 DataFrame 中筛选所需的行
        mask = df_data['ID'].isin(paginated_results)

        selected_data = df_data[mask][['ID', 'Title', 'URL']]
        # 重新索引以匹配sorted_documents中的顺序
        selected_data = selected_data.set_index('ID').reindex(paginated_results).reset_index()

        paginated_results = selected_data.to_dict(orient='records')



    # 获取当前页的文档ID列表
    current_page_ids = [res['ID'] for res in paginated_results]

    # 为当前页的文档生成摘要并添加到模板中
    page_summaries = {}
    for docid in current_page_ids:
        matching_rows = df_data[df_data['ID'] == docid]
        if not matching_rows.empty:
            text = matching_rows['Text'].values[0]
            if isinstance(text, str):
                summary = generate_summary(text, query)
                if len(summary) > MAX_SUMMARY_LENGTH:
                    summary = summary[:MAX_SUMMARY_LENGTH] + '...'
                page_summaries[docid] = summary
            else:
                page_summaries[docid] = ''
        else:
            page_summaries[docid] = ''  # 处理未找到匹配ID的情况

    # 更新当前页结果的摘要和标题关键词高亮处理
    paginated_results_with_summaries = []
    for result in paginated_results:
        result['Summary'] = highlight_keywords(page_summaries[result['ID']], query_tokens)
        highlighted_title = highlight_keywords(result['Title'], query_tokens)
        result['Highlighted_Title'] = highlighted_title
        paginated_results_with_summaries.append(result)



    end_time = time.time()
    execution_time = end_time - start_time

    return render_template('search.html', doc_list=paginated_results_with_summaries, length=len(sorted_documents),execution_times=execution_time, query_word=query, page=page)