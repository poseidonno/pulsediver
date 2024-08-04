import math

import pandas as pd

#使用TF-IDF计算相关度
def calculate_tf(word, document):
    if isinstance(document, str):
        word_count = document.lower().count(word.lower())
        total_words = len(document.split())
        return word_count / total_words if total_words > 0 else 0
    else:
        return 0

def calculate_idf(word, index_dict, total_documents):
    if word in index_dict:
        documents_with_word = len(index_dict[word])
        return math.log((total_documents + 1) / (documents_with_word + 1))
    else:
        return 0

def calculate_relevance_byTFIDF(query_tokens, index_dict, documents):
    index_dict = sort_dict_bylen(index_dict)
    print(index_dict)
    relevance_scores = {}
    total_documents = len(documents)

    for word in query_tokens:
        for doc_id, content in documents.items():
            tf = calculate_tf(word, content['content'])
            idf = calculate_idf(word, index_dict, total_documents)
            relevance_scores[doc_id] = relevance_scores.get(doc_id, 0) + (tf * idf)

    sorted_documents = sorted(relevance_scores.keys(), key=lambda x: relevance_scores[x], reverse=True)
    return sorted_documents


#仅用文档相关度计算
def calculate_relevance(query_tokens, index_dict):
    index_dict = sort_dict_bylen(index_dict)
    relevance_scores = {doc_id: 0 for doc_ids in index_dict.values() for doc_id in doc_ids}

    for word in query_tokens:
        if word in index_dict:
            matched_documents = index_dict[word]
            for doc_id in matched_documents:
                relevance_scores[doc_id] += 1

    sorted_documents = sorted(relevance_scores.keys(), key=lambda x: relevance_scores[x], reverse=True)
    return sorted_documents


#pagerank的排序
def sort_pagerank(relevant_documents, file_path):
    df = pd.read_csv(file_path)
    pagerank_dict = {row['ID']: row['PR'] for index, row in df.iterrows() if row['ID'] in relevant_documents}
    sorted_documents = sorted(relevant_documents, key=lambda x: pagerank_dict.get(x, 0), reverse=True)
    return sorted_documents


#先pagerank排序后再文档相关度排序
def calculate_relevance_with_pagerank(query_tokens, index_dict, file_path):
    index_dict = sort_dict_bylen(index_dict)
    relevance_scores = {doc_id: 0 for doc_ids in index_dict.values() for doc_id in doc_ids}

    for word in query_tokens:
        if word in index_dict:
            matched_documents = index_dict[word]
            for doc_id in matched_documents:
                relevance_scores[doc_id] += 1

    # 获取相关文档的 ID
    relevant_documents = [doc_id for doc_id in relevance_scores.keys() if relevance_scores[doc_id] > 0]

    # 调用排序函数，基于 PageRank 对相关文档进行排序
    sorted_documents_by_pagerank = sort_pagerank(relevant_documents, file_path)

    # 根据相关度再次排序
    sorted_documents_by_relevance = sorted(sorted_documents_by_pagerank, key=lambda x: relevance_scores[x],
                                           reverse=True)


    return sorted_documents_by_relevance

#现根据字符串长度排序
def sort_dict_bylen(index_dict):
    # 根据key的字符串长度排序字典
    sorted_keys = sorted(index_dict.keys(), key=lambda x: len(x), reverse=True)
    sorted_dict = {key: index_dict[key] for key in sorted_keys}

    return sorted_dict

