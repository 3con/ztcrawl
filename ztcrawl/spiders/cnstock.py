# -*- coding: utf-8 -*-
import scrapy
from random import randint
from scrapy.loader import ItemLoader
from ztcrawl.items import ZtArticleItem

class CnstockSpider(scrapy.Spider):
    name = "cnstock"
    allowed_domains = ["cnstock.com"]
    start_urls = (
        'http://caifu.cnstock.com/list/jj_yenei_dongtai',
    )

    def parse(self, response):
        # 列表页无标题图片用此方法, 若有参考easymoney.py
        for href in response.css('.new-list a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_item)

    def parse_item(self, response):
        l = ItemLoader(item=ZtArticleItem(), response=response)
        l.add_value('classId', '51');
        l.add_value('cataName', u'公募要闻')
        l.add_value('url', response.urljoin(response.url))
        l.add_css('title', 'h1.title::text')

        # 中证seo的keyword就是tags, description为简介, 然而description开头有中文空格, 一看就是程序员不细心
        l.add_css('keywords', 'meta[name*=keywords]::attr(content)')
        l.add_css('seo_keywords', 'meta[name*=keywords]::attr(content)')
        
        description = response.css('meta[name*=description]::attr(content)').extract()[0].replace(u'\u3000', '') # 去掉开头的中文空格
        l.add_value('description', description)
        l.add_value('seo_description', description)
        
        l.add_css('publishTime', '.timer::text')
        source = response.css('.source a::text').extract()
        
        # 有来源还是采上来源
        if len(source) == 0:
            tmp = response.css('.source::text').extract()[0]
            tmp = tmp.replace(u'来源：', '')
            l.add_value('source', tmp)
            # l.add_value('author', tmp)
        else:
            l.add_value('source', source[0])
        # 无浏览数随机一个三位数
        l.add_value('views', randint(100, 999))

        l.add_css('image_urls', '#qmt_content_div p img::attr(src)')

        content = response.css('#qmt_content_div').extract()[0]
        # 去广告
        content = content.replace(response.css('.visible-lg-block.visible-md-block').extract()[0], '')
        l.add_value('content', content)
        yield l.load_item()
