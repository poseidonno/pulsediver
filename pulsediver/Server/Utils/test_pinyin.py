import re

import jieba
from Pinyin2Hanzi import DefaultDagParams
from Pinyin2Hanzi import dag
def extract_continuous_pinyin_from_jieba_result(jieba_result):
    # 将分词结果中的连续拼音部分提取出来
    pinyin_matches = re.findall(r'[a-zA-Z]+', ''.join(jieba_result).lower())
    return pinyin_matches

def pinyin_2_hanzi(pinyinList):
    get_results = []
    dagParams = DefaultDagParams()
    result = dag(dagParams, pinyinList, path_num=10, log=True)#10代表侯选值个数
    for item in result:
        socre = item.score
        res = item.path # 转换结果
        get_results.append(res)
    return get_results[:5]

def get_pint2hanzi(pinyin_list):
    results = pinyin_2_hanzi(pinyin_list)
    cleaned_list = [str(item).replace("['", "").replace("']", "").replace(", '", "") for item in results]
    return cleaned_list


if __name__ == '__main__':
    # 示例文本
    input_text = "你好，ni hao, 我的名字是。"
    jieba_result = jieba.lcut(input_text)
    print(jieba_result)
    pinyin_list = extract_continuous_pinyin_from_jieba_result(input_text)
    print(pinyin_list)
    results = pinyin_2_hanzi(pinyin_list)
    cleaned_list = [str(item).replace("['", "").replace("']", "").replace(", '", "") for item in results]
    print(cleaned_list)
