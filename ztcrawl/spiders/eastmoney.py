# -*- coding: utf-8 -*-
import scrapy
import time
import re
from random import randint
from scrapy.loader import ItemLoader
from ztcrawl.items import ZtArticleItem

class EastmoneySpider(scrapy.Spider):
    name = "easymoney"
    allowed_domains = ["eastmoney.com"]
    start_urls = (
        'http://finance.eastmoney.com/yaowen_cgnjj.html',
        # 'http://finance.eastmoney.com/yaowen_cgnjj_3.html',
    )

    def parse(self, response):
        # 列表页有标题图片用此方法, cnstock.py
        for li in response.css('#artitileList1 li'):
            full_url = response.urljoin(li.css('.title a::attr(href)').extract()[0])

            title_image = li.css('.newsImg::attr(src)').extract()
            subresponse = scrapy.Request(full_url, callback=self.parse_item)
            
            item = ZtArticleItem()
            if len(title_image) != 0:
                item['title_image'] = title_image[0]
                item['image_urls'] = title_image
            
            subresponse.meta['item'] = item
            yield subresponse

    def parse_item(self, response):
        l = ItemLoader(item=response.meta['item'], response=response)
        l.add_value('classId', '49');
        l.add_value('cataName', u'国内经济')
        l.add_value('url', response.urljoin(response.url))
        l.add_css('title', '.newsContent h1::text')
        l.add_css('seo_title', '.newsContent h1::text')
        l.add_css('seo_keywords', 'meta[name*=keywords]::attr(content)')
        l.add_css('seo_description', 'meta[name*=description]::attr(content)')
        # 东财来源是图片
        l.add_value('source', u'东方财富网')
        # l.add_value('author', u'东方财富网')
        # 无浏览数随机一个三位数
        l.add_value('views', randint(100, 999))

        l.add_css('keywords', 'meta[name*=keywords]::attr(content)')
        l.add_css('description', '.c_review::text')

        # 2015年12月9日 11:09 -> 2015-12-09 11:09
        publishTime = response.css('.Info span:first-child::text').extract()[0]
        publishTime = time.strftime('%Y-%m-%d %H:%M', time.strptime(re.sub('[^0-9]', '', publishTime), '%Y%m%d%H%M'))
        l.add_value('publishTime', publishTime)

        content = response.css('#ContentBody').extract()[0]
        # 替换摘要
        substract = response.css('.c_review').extract();
        if len(substract):
            content = content.replace(substract[0], '')

        # 删除广告
        ad = response.css('.reading').extract()
        if len(ad) > 0:
            content = content.replace(ad[0], '')

        # 锚文本替换
        atags = response.css('#ContentBody a')
        ataghtml = response.css('#ContentBody a').extract()
        for index, atag in enumerate(atags):
            atext = atag.css('::text').extract()
            if len(atext):
                content = content.replace(ataghtml[index], atext[0])
            else:
                content = content.replace(ataghtml[index], atag.css(':first-child').extract()[0])
                
        l.add_value('content', content)

        yield l.load_item()