# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from c2 import settings
import random


class RandomUserAgent(object):
    def process_request(self, request, spider):
        user_agent = random.choice(settings.USER_AGENTS)
        request.headers.setdefault("User-Agent", user_agent)