import re

import jieba
from Pinyin2Hanzi import DefaultDagParams
from Pinyin2Hanzi import dag
def extract_pinyin(jieba_result):
    # 将分词结果中的连续拼音部分提取出来
    pinyin_matches = []
    temp_pinyin = ''
    for word in jieba_result:
        # 检查每个词中的拼音部分
        pinyin_list = re.findall(r'[a-zA-Z]+', word.lower())
        if pinyin_list:
            # 将拼音部分加入列表中
            pinyin_matches.extend(pinyin_list)
    return pinyin_matches

def re_tokenize_words(words):
    new_words = []
    for word in words:
        # 检查是否含有撇号
        if "'" in word:
            # 对含有撇号的词进行二次分词
            sub_words = jieba.lcut(word.replace("'", ""))
            new_words.extend(sub_words)
        else:
            new_words.append(word)

    # 去除重复内容并保持顺序
    unique_words = list(dict.fromkeys(new_words))
    return unique_words

def pinyin_2_hanzi(pinyinList):
    get_results = []
    dagParams = DefaultDagParams()
    result = dag(dagParams, pinyinList, path_num=10, log=True)#10代表侯选值个数
    for item in result:
        socre = item.score
        res = item.path # 转换结果
        get_results.append(res)
    return get_results[:5]

def get_pinyin2hanzi(pinyin_list):
    results = pinyin_2_hanzi(pinyin_list)
    cleaned_list = [str(item).replace("['", "").replace("']", "").replace(", '", "") for item in results]
    final_list = re_tokenize_words(cleaned_list)
    return final_list


if __name__ == '__main__':
    # 示例文本
    input_text = "wo xiang shi shi"
    jieba_result = jieba.lcut(input_text)
    print(jieba_result)
    pinyin_list = extract_pinyin(['qu', 'kuai', 'lian'])
    print(pinyin_list)
    results = pinyin_2_hanzi(pinyin_list)
    cleaned_list = [str(item).replace("['", "").replace("']", "").replace(", '", "") for item in results]
    final_list = re_tokenize_words(cleaned_list)
    print(cleaned_list)
    print(final_list)

