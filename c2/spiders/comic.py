# -*- coding: utf-8 -*-
import scrapy
from c2.items import C2Item
import re
import os
from c2 import settings


class ComicSpider(scrapy.Spider):
    name = 'comic'
    allowed_domains = ['www.cartoonmad.com']
    start_urls = ['http://www.cartoonmad.com/comic/2655.html']

    def parse(self, response):
        urls = response.xpath(".//table[@width='688']//tr//td/a/@href").extract()
        dir_names = response.xpath(".//table[@width='688']//tr//td/a/text()").extract()
        pages = response.xpath(".//table[@width='688']//tr//td/font/text()").extract()

        for index in range(len(urls)):
            item = C2Item()
            url = urls[index]
            item['link_url'] = 'http://www.cartoonmad.com' + url
            item['dir_name'] = dir_names[index]
            item['page_num'] = pages[index]
            yield scrapy.Request(url=item['link_url'], meta={'item': item}, callback=self.parsecartoon)

    def parsecartoon(self, response):
        # 接收传递的item
        o_item = response.meta['item']
        # 获取章节的第一页的链接
        o_item['link_url'] = response.url

        page_num = re.findall(r'(\d+)', o_item['page_num'])[0]

        img_urls = response.xpath(".//td/a/img/@src").extract()
        if len(img_urls) == 0:
            yield scrapy.Request(url=o_item['link_url'], meta={'item': o_item}, callback=self.parsecartoon)
        else:
            for img in img_urls:
                if img.find('web.cartoonmad.com') != -1:
                    b_img = img[:-7]
                    type = img.split('.')[-1]
                    for page in range(1, int(page_num) + 1):
                        item = C2Item()
                        item['link_url'] = response.url
                        item['dir_name'] = o_item['dir_name']
                        item['page_num'] = o_item['page_num']
                        p = "%03d" % page
                        img_url = b_img + p + "." + type
                        # 保存图片链接
                        item['img_url'] = [img_url]

                        if self.isImgExist(item):
                            yield item

    def isImgExist(self, item):
        dir_path = os.path.join(settings.IMAGE_STORES, item['dir_name'])
        img_url = item['img_url'][0]
        page = img_url.split('/')[-1].split('.')[0]
        type = img_url.split('/')[-1].split('.')[-1]
        img_file_name = '第' + page + '页.' + type
        file_path = os.path.join(dir_path, img_file_name)

        if not os.path.exists(file_path):
            return True
        else:
            return False

        # 获取章节的页数
        # page_num = response.xpath('.//td[@valign="top"]/text()').re(u'共(\d+)页')[0]
        # page_num = re.findall(r'(\d+)', item['page_num'])[0]
        # 根据页数，整理出本章节其他页码的链接
        # p_link = item['link_url'][:-7]

        # 从第二页开始
        # for page in range(2, int(page_num) + 1):
        #     p = "%02d" % page
        #     page_link = p_link + str(p) + '.html'
        #     # 根据本章节其他页码的链接发送Request请求，用于解析其他页码的图片链接，并传递item
        #     yield scrapy.Request(url=page_link, meta={'item': item}, callback=self.parseother)

    def parseother(self, response):
        item = response.meta['item']
        # 获取该页面的链接
        item['link_url'] = response.url
        img_urls = response.xpath(".//td/a/img[@border='0']/@src").extract()
        img_url = []
        for img in img_urls:
            if img.find('web.cartoonmad.com') != -1:
                img_url.append(img)
        # 保存图片链接
        item['img_url'] = img_url
        # 返回item，交给item pipeline下载图片
        yield item
