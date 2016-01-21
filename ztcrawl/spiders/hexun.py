# -*- coding: utf-8 -*-
import scrapy
from random import randint
import re
from scrapy.loader import ItemLoader
from ztcrawl.items import ZtArticleItem

class HexunSpider(scrapy.Spider):
    name = "hexun"
    allowed_domains = ["hexun.com"]
    start_urls = (
        'http://trust.hexun.com/trust_industry/index.html',
    )

    def parse(self, response):
        # 列表页无标题图片用此方法, 若有参考easymoney.py
        for href in response.css('#news_list a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_item)

    def parse_item(self, response):
        l = ItemLoader(item=ZtArticleItem(), response=response)
        l.add_value('classId', '57');
        l.add_value('cataName', u'市场动态')
        l.add_value('url', response.urljoin(response.url))
        l.add_css('title', '#artibodyTitle h1::text')

        keywords = response.css('meta[name*=eywords]::attr(content)').extract()[0]
        keywordsList = keywords.split(' ')
        while '' in keywordsList:
            keywordsList.remove('')
            
        l.add_value('keywords', keywordsList)
        l.add_value('seo_keywords', keywords)
        
        description = ''.join(response.css('#artibody p::text').extract())
        if len(description) > 200:
            description = description[:200]
            
        l.add_value('description', description)
        l.add_value('seo_description', description)
        
        l.add_value('publishTime', response.css('#pubtime_baidu::text').extract()[0])
        l.add_css('source', '#source_baidu a::text')

        # 无浏览数随机一个三位数
        l.add_value('views', randint(100, 999))
        
        l.add_css('image_urls', '#artibody img::attr(src)')

        content = response.css('#artibody').extract()[0]
        
        # 去广告
        # content = content.replace(response.css('.visible-lg-block.visible-md-block').extract()[0], '')

        # 锚文本替换
        atags = response.css('#artibody a').extract()
        atexts = response.css('#artibody a::text').extract()
        if (len(atags) == len(atexts)):
            for index, atag in enumerate(atags):
                content = content.replace(atag, atexts[index])

        l.add_value('content', content)
        yield l.load_item()
