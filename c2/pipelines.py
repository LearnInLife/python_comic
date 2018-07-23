# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.htmlxs
import os
from c2 import settings
import scrapy
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

import shutil


class C2Pipeline(ImagesPipeline):
    img_store = get_project_settings().get('IMAGES_STORE')

    # 重写ImagesPipeline类的此方法
    # 发送图片下载请求
    def get_media_requests(self, item, info):
        img_url = item['img_url'][0]
        print(img_url)
        yield scrapy.Request(img_url)

    # 重写item_completed方法
    # 将下载的文件保存到不同的目录中
    def item_completed(self, results, item, info):
        print(results)
        image_path = [x['path'] for ok, x in results if ok]
        print(image_path)

        dir_path = os.path.join(settings.IMAGE_STORES, item['dir_name'])

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        img_url = item['img_url'][0]
        page = img_url.split('/')[-1].split('.')[0]
        type = img_url.split('/')[-1].split('.')[-1]
        img_file_name = '第' + page + '页.' + type
        file_path = os.path.join(dir_path, img_file_name)
        # 将文件从默认下路路径移动到指定路径下
        orign_path = os.path.join(self.img_store, image_path[0])
        shutil.move(orign_path, file_path)

        item["image_paths"] = file_path
        return item

# class C2Pipeline(object):
#     def process_item(self, item, spider):
#         if 'img_url' in item:
#             images = []
#             # 按章节保存文件夹
#             dir_path = os.path.join(settings.IMAGE_STORE, item['dir_name'])
#             # 文件夹不存在则创建文件夹
#             if not os.path.exists(dir_path):
#                 os.makedirs(dir_path)
#             # 获取每一个图片链接
#             for img_url in item['img_url']:
#                 # 解析链接，获取第几页
#                 # page = item['link_url'].split('/')[-1].split('.')[0][-2:]
#                 page = img_url.split('/')[-1].split('.')[0]
#                 # 扩展名
#                 type = img_url.split('/')[-1].split('.')[-1]
#                 # 图片名称
#                 img_file_name = '第' + page + '页.' + type
#                 # 图片保存路径
#                 file_path = os.path.join(dir_path, img_file_name)
#                 images.append(file_path)
#                 if os.path.exists(file_path):
#                     continue
#
#                 # 保存图片
#                 with open(file_path, 'wb') as f:
#                     head = {
#                         'User-Agent': random.choice(settings.USER_AGENTS)
#                     }
#                     response = requests.get(url=img_url, headers=head)
#                     for blok in response.iter_content(1024):
#                         if not blok:
#                             break
#
#                         f.write(blok)
#
#             item['image_paths'] = images
#         return item
