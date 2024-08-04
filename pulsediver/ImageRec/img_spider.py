import csv
import os

import aiohttp
import asyncio
from urllib.parse import urljoin

from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import imagehash

start_urls =['https://unsplash.com/', 'https://www.foodiesfeed.com/', 'https://visualhunt.com']
max_images = 1200
download_folder = "images"
visited_urls = set()  # 存储已访问过的链接
downloaded_image_hashes = set()  # 存储已下载图片的哈希
max_depth = 8  # 最大爬取深度
# desc_pattern = re.compile(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', re.IGNORECASE)

csv_filename = "image_data.csv"
csv_header = ["ID", "URL"]
last_saved_img_url = None
# image_data_list = []  # 存储图片信息的列表
image_count = 0

# csv_file_path = 'image_data.csv'  # 替换为你的 CSV 文件路径
folder_path = 'datasets/images'
def get_last_id_from_folder(folder_path):
    try:
        file_list = os.listdir(folder_path)  # 获取文件夹中的所有文件
        if not file_list:  # 如果文件夹为空
            return 0

        file_list.sort()  # 按文件名排序
        last_file = file_list[-1]  # 获取最后一个文件名
        file_id, _ = os.path.splitext(last_file)  # 获取文件名中的ID部分
        return int(file_id)  # 返回文件ID
    except Exception as e:
        print(f"Error reading folder: {e}")
        return 0
image_count = get_last_id_from_folder(folder_path)
print(image_count)

max_images = image_count + max_images


async def fetch(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.read()
        else:
            return None


async def calculate_image_hash(image):
    # 计算图像的平均哈希
    hash_value = imagehash.average_hash(image)
    return str(hash_value)


async def download_image(session, url):
    global image_count, max_images

    try:
        if image_count >= max_images:
            return False

        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                image = Image.open(BytesIO(content))
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")

                width, height = image.size
                if width < 500 or height < 500:
                    return

                hash_value = await calculate_image_hash(image)
                if hash_value in downloaded_image_hashes:
                    print(f"Skipping similar image: {url}")
                    return

                filename = f"{download_folder}/{image_count+1}.jpg"
                os.makedirs(download_folder, exist_ok=True)
                with open(filename, 'wb') as f:
                    f.write(content)
                    image_count += 1
                    print(f"image:{image_count} and saved to---{filename}  with:{url}")

                    downloaded_image_hashes.add(hash_value)

                    # description = extract_description(content)
                    # print(description)
                    # 将图片信息存入列表
                    # image_data_list.append([image_count, url])


            else:
                print("")
    except Exception as e:
        print("")




#提取图片的文字描述（未实现）
# def extract_description(content):
#     try:
#         detected_encoding = chardet.detect(content)
#         content_decoded = content.decode(detected_encoding['encoding'], 'replace')
#
#         soup = BeautifulSoup(content_decoded, 'html.parser')
#         img_tags = soup.find_all('img')  # 查找页面中所有的图片标签
#         if img_tags:
#             for img_tag in img_tags:
#                 img_description = img_tag.get('alt')  # 尝试获取每个图片标签的 alt 属性
#                 if img_description:
#                     print(f"Extracted Description from Image: {img_description}")
#                     return img_description
#
#             # 如果没有找到带有 alt 属性的图片，则返回提示信息
#             print("No description found in any image.")
#             return ""
#         else:
#             print("No image tag found.")
#             return ""
#     except Exception as e:
#         print(f"Error extracting description: {e}")
#         return ""


async def parse_and_crawl(session, url, depth):
    global last_saved_img_url  # 使用全局变量来记录最后一个被保存的图片URL

    try:
        if depth <= 0 or url in visited_urls:
            return

        if "istockphoto.com" in url:
            return

        visited_urls.add(url)
        content = await fetch(session, url)
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            img_tags = soup.find_all('img')
            for img in img_tags:
                img_url = urljoin(url, img.get('src', ''))
                if img_url not in downloaded_image_hashes:
                    download_status = await download_image(session, img_url)
                    if download_status is False:
                        return

                    img_id = image_count

                    # 更新最后一个被保存的图片URL
                    last_saved_img_url = img_url

            links = soup.find_all('a', href=True)
            for link in links:
                next_url = urljoin(url, link['href'])
                await parse_and_crawl(session, next_url, depth - 1)

    except Exception as e:
        print(f"Error parsing {url}: {e}")

# 在函数结束时将最后一个被保存的图片URL写入CSV文件
# async def finalize_csv():
#     if image_data_list:
#         with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
#             csv_writer = csv.writer(csvfile)
#             csv_writer.writerows(image_data_list)

async def main():
    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        for url in start_urls:
            await parse_and_crawl(session, url, max_depth)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        else:
            raise e

    # 在爬取结束后调用 finalize_csv() 函数
    # loop.run_until_complete(finalize_csv())
