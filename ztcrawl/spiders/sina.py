# -*- coding: utf-8 -*-
import scrapy
from random import randint
from scrapy.loader import ItemLoader
from ztcrawl.items import ZtArticleItem

class SinaSpider(scrapy.Spider):
    name = "sina"
    allowed_domains = ["sina.com.cn"]
    start_urls = (
        'http://roll.finance.sina.com.cn/finance/sm4/index.shtml',
    )

    def parse(self, response):
        for href in response.css('.list_009 li a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_item)

    def parse_item(self, response):
        l = ItemLoader(item=ZtArticleItem(), response=response)
        l.add_value('classId', '10');
        l.add_value('cataName', u'私募资讯')
        l.add_value('url', response.urljoin(response.url))
        l.add_css('title', '#artibodyTitle::text')
        l.add_css('seo_keywords', 'meta[name*=keywords]::attr(content)')
        l.add_css('seo_description', 'meta[name*=description]::attr(content)')
        
        # 新浪发布时间和来源在一个dom节点内，而且来源会变化简单处理
        source = response.css('.time-source span a::text').extract()
        if len(source) == 0:
            tmp = response.css('.time-source::text').extract()[0]
            tmp = tmp.replace(' ', '').replace('\n', '').replace('\t', '')
            l.add_value('author', tmp[16:])
            l.add_value('source', tmp[16:])
            l.add_value('publishTime', tmp[:16])
        else:
            l.add_value('author', source[0])
            l.add_value('source', source[0])
            l.add_value('publishTime', response.css('.time-source::text').extract()[0].replace(' ', '').replace('\n', '').replace('\t', ''))
        
        l.add_css('keywords', '.article-keywords a::text')
        # 新浪无浏览数随机一个三位数
        l.add_value('views', randint(100, 999))

        l.add_css('image_urls', '#artibody img::attr(src)')

        # content = ''.join(response.xpath('//div[@id="artibody"]/*').extract())
        content = response.css('#artibody').extract()[0]
        l.add_value('content', content)
        yield l.load_item()
