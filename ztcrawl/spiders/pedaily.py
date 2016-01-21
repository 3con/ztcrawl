# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from ztcrawl.items import ZtArticleItem

class PedailySpider(scrapy.Spider):
    name = "pedaily"
    allowed_domains = ["pedaily.cn"]
    start_urls = (
        'http://pe.pedaily.cn/',
    )

    def parse(self, response):
        # 列表页有标题图片用此方法, cnstock.py
        for li in response.css('#newslist-all li'):
            full_url = response.urljoin(li.css('h3 a::attr(href)').extract()[0])

            title_image = li.css('img::attr(src)').extract()
            subresponse = scrapy.Request(full_url, callback=self.parse_item)
            
            item = ZtArticleItem()
            if len(title_image) != 0:
                item['title_image'] = title_image[0]
                item['image_urls'] = title_image
            
            subresponse.meta['item'] = item
            yield subresponse

    def parse_item(self, response):
        l = ItemLoader(item=response.meta['item'], response=response)
        l.add_value('classId', '18');
        l.add_value('cataName', u'私募股权资讯')
        l.add_value('url', response.urljoin(response.url))
        l.add_css('title', 'h1::text')

        keywords = response.css('meta[name*=eywords]::attr(content)').extract()[0]
        keywordsList = keywords.split(',')
        while '' in keywordsList:
            keywordsList.remove('')
            
        l.add_value('keywords', keywordsList)
        l.add_value('seo_keywords', keywords)
        
        description = response.css('.news-show .subject::text').extract()
        l.add_value('description', description)
        l.add_value('seo_description', description)
        
        l.add_value('publishTime', response.css('.date::text').extract()[0])
        
        tmp = response.css('.news-show .box-l::text').extract()[0].split(u'\u3000')
        while '' in tmp:
            tmp.remove('')

        l.add_value('source', tmp[0].replace(' ', ''))
        l.add_value('author', tmp[1].replace(' ', '') if tmp[1] != u'\u3000' else '')

        # pedaily 阅读数为ajax加载, 没有爬取的必要
        # views = response.css('#HitsText::text').extract()[0].replace(u'阅读：', '')
        # l.add_value('views', views)
        
        image_urls = response.css('#news-content img::attr(src)').extract().append(response.meta['item']['image_urls'])
        l.add_value('image_urls', image_urls)


        content = response.css('#news-content').extract()[0]
        
        # 去广告
        # content = content.replace(response.css('.visible-lg-block.visible-md-block').extract()[0], '')

        # 锚文本替换
        atags = response.css('#news-content a').extract()
        atexts = response.css('#news-content a::text').extract()
        if (len(atags) == len(atexts)):
            for index, atag in enumerate(atags):
                content = content.replace(atag, atexts[index])

        l.add_value('content', content)
        yield l.load_item()
