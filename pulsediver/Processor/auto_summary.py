import math
import jieba
from collections import Counter, defaultdict

# 提取停用词列表
STOP_WORDS = ['，', '？', '。', '\n', '\n\n', '、']

def tokenize(text):
    return (word for word in jieba.cut(text) if word not in STOP_WORDS)

def compute_tf(documents):
    tf_word = []
    for doc in documents:
        doc_count = len(doc)
        word_counter = Counter(doc)
        tf = {word: word_counter[word] / doc_count for word in doc}
        tf_word.append(tf)
    return tf_word

def compute_idf(documents):
    idf_word = defaultdict(int)
    docs_count = len(documents)
    for doc in documents:
        unique_words = set(doc)
        for word in unique_words:
            idf_word[word] += 1
    idf_word = {word: math.log(docs_count / (count + 1)) for word, count in idf_word.items()}
    return idf_word

def compute_doc_vector(documents):
    docv = []
    for doc in documents:
        doc_counter = Counter(doc)
        docv.append(dict(doc_counter))
    return docv

def compute_word_df(documents):
    word2df = Counter()
    for doc in documents:
        word2df.update(set(doc))
    return dict(word2df)

def compute_tf_idf(tf, idf):
    word_tfidf = []
    for tf_doc in tf:
        article = {word: value * idf.get(word, 0) for word, value in tf_doc.items()}
        word_tfidf.append(article)
    return word_tfidf

def find_keyword_indexes(text, keywords):
    indexes = []
    for keyword in keywords:
        indexes.extend([i for i in range(len(text)) if text[i:i + len(keyword)] == keyword])
    indexes.sort()
    return indexes

def extract_windows(text, indexes, k):
    results = []
    for i in indexes:
        if len(text[i:i + k]) >= k:
            results.append(text[i:i + k])
        else:
            results.append(text[i:])
    return results

def compute_window_weights(windows, word_tfidf, keywords):
    window_weights = {}
    for i, window in enumerate(windows):
        window_weight = sum(word_tfidf.get(word, 0) for word in window if word in keywords)
        window_weights[i] = window_weight
    sorted_window_weights = {k: v for k, v in sorted(window_weights.items(), key=lambda item: item[1], reverse=True)}
    return sorted_window_weights

def adjust_best_window(text, indexes, windows, best_key):
    i = 1
    j = 1
    best_i = indexes[best_key]
    best_j = indexes[best_key] + len(windows[best_key]) - 1
    while best_i - i >= 0 and text[best_i - i] not in STOP_WORDS:
        i += 1
    while best_j + j < len(text) and text[best_j + j] not in STOP_WORDS:
        j += 1
    final_summary = text[best_i - i + 1:best_j + j]
    return final_summary


def generate_summary(text, keywords, window_size=125, fallback_length=125):

    # 分词和处理文本
    tokenized_text = list(tokenize(text))
    documents = [tokenized_text]

    # 寻找关键词在文本中的位置
    keyword_indexes = find_keyword_indexes(text, keywords)

    # 如果没有找到关键词，则返回文本的前部分
    if not keyword_indexes:
        orgin_summary = text[:fallback_length] + "..."
        return orgin_summary

    # 计算 TF、IDF 等
    tf = compute_tf(documents)
    idf = compute_idf(documents)
    doc_vector = compute_doc_vector(documents)
    word_tfidf = compute_tf_idf(tf, idf)

    # 提取窗口并计算权重
    extracted_windows = extract_windows(text, keyword_indexes, window_size)
    window_weights = compute_window_weights(extracted_windows, word_tfidf[0], keywords)

    # 获取最重要窗口的索引并调整摘要
    best_window_key = list(window_weights.keys())[0]
    adjusted_summary = adjust_best_window(text, keyword_indexes, extracted_windows, best_window_key)+"..."
    return adjusted_summary
# 使用示例
if __name__ == "__main__":
    sample_text = "在文件中写入一个小Pan桃❀: 请问是把cesium的包下载下来放到static里吗？Steven Hank: 可以监听下window.earth的柚子学编程: 其他组件不能第一时间获取到window.earth的值怎么办，有延迟的。比如在主页面window.earth = viewer，其他页面打印出的window.earth是undefined,如果设置一个延时函数是可以获取到的Steven Hank 回复 lingerhaiyang: 最简单的方式是通过window.earth = viewer；在其他组件调用的时候直接通过window.earth 调用Steven Hank 回复 @codeDo: cesium引入的方式不推荐通过node_moudules的方式，通过将cesium放入static，然后在index.html通过srcipt标签引入请填写红包祝福语或标题红包个数最小为10个红包金额最低5元打赏作者Steven Hank你的鼓励将是我创作的最大动力您的余额不足，请更换扫码支付或充值打赏作者抵扣说明： 1.余额是钱包充值的虚拟货币，按照1:1的比例进行支付金额的抵扣。 2.余额无法直接购买下载，可以购买VIP、付费专栏及课程。"
    sample_keywords = ['人工智能', '文章']
    highlighted_summary = generate_summary(sample_text, sample_keywords)
    print("Generated Highlighted Summary:")
    print(highlighted_summary)
