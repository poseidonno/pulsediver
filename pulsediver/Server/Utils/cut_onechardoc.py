# 定义函数
def process_dictionary(input_dict):
    #字符数小于2的字典
    dict_A = {}
    #字符数大于等于2的字典
    dict_B = {}

    for keyword, doc_ids in input_dict.items():
        if len(keyword) < 2:
            dict_A[keyword] = doc_ids
        else:
            dict_B[keyword] = doc_ids

    # 获取字典B的所有文档id的并集
    set_B = set()
    for doc_list in dict_B.values():
        set_B.update(doc_list)

    # 获取字典A的所有文档id的并集
    set_A = set()
    for doc_list in dict_A.values():
        set_A.update(doc_list)

    # 获取字典B和字典A文档id的交集
    intersection = set_B.intersection(set_A)

    # 从字典A中减去交集部分，得到只含字符小于两个的相关文档列表C
    list_C = []
    for doc_list in dict_A.values():
        list_C.extend([doc_id for doc_id in doc_list if doc_id not in intersection])

    return dict_B, list_C

if __name__ == '__main__':
    # 测试实例
    input_dictionary = {
        "这个人": [1, 2, 3, 4],
        "不是": [1, 2, 5],
        "我们": [1, 2, 3],
        "能": [1, 6, 7],
        "惹": [1, 3, 4, 5, 9]
    }

    list_B, list_C = process_dictionary(input_dictionary)

    # 输出结果
    print("相关文档列表 B:", list_B)
    print("只含字符小于两个的相关文档列表 C:", list_C)

