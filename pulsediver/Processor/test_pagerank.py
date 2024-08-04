import time

import pandas as pd
import numpy as np
import psutil


class PageRank():
      # G: 传入图的邻接矩阵
      # T: 迭代计算次数上限
      # eps: 误差上限
      # beta: 阻尼因子
      # 注：误差小于eps或者迭代次数大于T结束迭代计算
    def __init__(self, G, T=50, eps=1e-6, beta=0.85) -> None:
        self.G = G
        self.N = len(G)
        self.T = T
        self.eps = eps
        self.beta = beta

    # 创建概率转换矩阵
    def GtoM(self, G):
        M = np.zeros((self.N, self.N))
        for i in range(self.N):
            D_i = sum(G[i])
            if D_i == 0:
                continue
            for j in range(self.N):
                M[j][i] = G[i][j] / D_i  # 归一化并转置
        return M

    def computePR(self):
        # 转换邻接矩阵为概率转移矩阵
        M = self.GtoM(self.G)

        R = np.ones(self.N)  # 将每个页面的初始 PageRank 值设为 1
        teleport = np.ones(self.N) / self.N
        for time in range(self.T):
            A = self.beta * M + (1 - self.beta) * teleport
            R_new = np.dot(A, R)
            if np.linalg.norm(R_new - R) < self.eps:
                break
            R = R_new.copy()
        normalized_PR = np.around(R_new / np.sum(R_new), 5)  # 归一化处理，使得总和为 1
        return normalized_PR

def build_graph_from_csv(csv_file):
    # 从CSV文件中读取数据
    data = pd.read_csv(csv_file)

    # 创建字典存储页面链接关系
    pages = {}

    # 遍历数据，构建页面链接关系
    for index, row in data.iterrows():
        url = row['URL']
        links = row['Links']
        if isinstance(links, str):  # 检查是否是字符串类型
            links = links.split(',')
        else:
            # 处理非字符串情况，比如浮点数或空值
            links = []  # 或者其他适当的处理方式，根据实际需求
        pages[url] = links
    # 构建邻接矩阵G
    all_urls = list(pages.keys())
    G = np.zeros((len(all_urls), len(all_urls)))

    for i, url in enumerate(all_urls):
        for link in pages[url]:
            if link in all_urls:
                j = all_urls.index(link)
                G[i][j] = 1
        print(f"处理进度：{i}/{len(all_urls)}")

    print("\n\n请稍后PageRank即将计算完成......\n")
    return G


if __name__ == "__main__":
    csv_file_path = 'E:\Python\搜索引擎实验\MyProject\Spider\web_pages\scraped_data.csv'  # 替换成你的CSV文件路径
    start_time = time.time()
    G = build_graph_from_csv(csv_file_path)
    PR = PageRank(G)
    pagerank_values = PR.computePR()
    print(PR.computePR())
    end_time = time.time()

    # 计算执行时间
    execution_time = end_time - start_time
    print(f"程序执行时间为：{execution_time} 秒")

    # # # 读取CSV文件
    # data = pd.read_csv(csv_file_path)
    #
    # # 创建新的DataFrame包含URL和PageRank值
    # url_column = data['URL']
    # pagerank_column = pd.Series(pagerank_values, name='Pagerank')
    # result_df = pd.concat([url_column, pagerank_column], axis=1)
    #
    # # 将DataFrame写入CSV文件
    # output_csv_path = 'pagerank_results.csv'  # 设置输出文件路径
    # result_df.to_csv(output_csv_path, index=False)
    # print(f"PageRank values saved to {output_csv_path}")