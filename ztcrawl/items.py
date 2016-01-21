# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZtArticleItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    keywords = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    source = scrapy.Field()
    publishTime = scrapy.Field()
    content = scrapy.Field()
    views = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_paths = scrapy.Field()
    classId = scrapy.Field()
    cataName = scrapy.Field()
    seo_title = scrapy.Field()
    seo_keywords = scrapy.Field()
    seo_description = scrapy.Field()
    title_image = scrapy.Field()