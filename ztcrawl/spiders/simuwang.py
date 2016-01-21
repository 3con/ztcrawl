# -*- coding: utf-8 -*-
import scrapy
from random import randint
from scrapy.loader import ItemLoader
from ztcrawl.items import ZtArticleItem

class SimuwangSpider(scrapy.Spider):
    name = "simuwang"
    allowed_domains = ["simuwang.com"]
    start_urls = (
        'http://news.simuwang.com/roll/page/2.html',
    )

    def parse(self, response):
        # 列表页无标题图片用此方法, 若有参考easymoney.py
        for href in response.css('.tuwenbox02 a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_item)

    def parse_item(self, response):
        l = ItemLoader(item=ZtArticleItem(), response=response)
        l.add_value('classId', '11');
        l.add_value('cataName', u'私募要闻')
        l.add_value('url', response.urljoin(response.url))
        l.add_css('title', '.hd h1::text')

        keywords = response.css('meta[name*=eywords]::attr(content)').extract()[0]
        keywordsList = keywords.split(',')
        while '' in keywordsList:
            keywordsList.remove('')

        l.add_value('keywords', keywordsList)
        l.add_value('seo_keywords', keywords)
        
        description = response.css('meta[name*=escription]::attr(content)').extract()[0]
        l.add_value('description', description)
        l.add_value('seo_description', description)
        
        l.add_value('publishTime', response.css('.info::text').extract()[0])
        l.add_css('source', '.info .where::text')

        # 无浏览数随机一个三位数
        l.add_value('views', randint(100, 999))
        
        l.add_css('image_urls', '#qmt_content_div p img::attr(src)')

        content = response.css('#Cnt-Main').extract()[0]
        
        # 去广告
        # content = content.replace(response.css('.visible-lg-block.visible-md-block').extract()[0], '')

        # 锚文本替换
        atags = response.css('#Cnt-Main a').extract()
        atexts = response.css('#Cnt-Main a::text').extract()
        if (len(atags) == len(atexts)):
            for index, atag in enumerate(atags):
                content = content.replace(atag, atexts[index])

        content = content.replace(u'(专栏)', '')

        l.add_value('content', content)
        yield l.load_item()