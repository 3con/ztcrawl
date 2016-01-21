# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# import scrapy
import codecs
import redis
import settings
import os
from base64 import b64encode
from scrapy import signals
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonItemExporter
from random import randint
# from scrapy import log

class ZtcrawlPipeline(ImagesPipeline):
    if hasattr(settings, 'REDIS_PASS'):
        r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASS)
    else:
        r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    def process_item(self, item, spider):
        self.spider_name = spider.name
        return super(ZtcrawlPipeline, self).process_item(item, spider)

    def item_completed(self, results, item, info):
        item = super(ZtcrawlPipeline, self).item_completed(results, item, info)
        # 神切面, 以后肯定有用
        itemKey = 'Crawl_%s_%s' % (self.spider_name, b64encode(item['url'][0]))
        if self.r.get(itemKey) == None:
            self.r.setex(itemKey, 3600 * 24 * 15, item['url'][0])
        else:
            raise DropItem('%s already scraped.' % (item['url'][0]))

        if len(item['images']) != 0:
            try:
                for image in item['images']:
                    item['content'][0] = item['content'][0].replace(image['url'], '%s%s' % (settings.IMAGE_REPL_PREFIX, image['path']))
                    if 'title_image' in item and image['url'] == item['title_image'].encode('utf-8'):
                        item['title_image'] = '%s%s' % (settings.IMAGE_REPL_PREFIX, image['path'])
            except:
                raise DropItem('Can not replace images')

        # 增加转义, 防止json文件解析错误 (addslashes)
        item['content'][0] = item['content'][0].replace('"', '\"').replace("'", '\'').replace('{', "\{").replace('}', "\}").replace(u'  ', '')
        return item

class JsonExportPipeline(object):

    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file = codecs.open('%s_data.json' % spider.name, 'w+b', encoding='utf-8')
        self.files[spider] = file
        self.exporter = JsonItemExporter(file)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

# 生成文章爬虫主辅表的pipeline
class ZtSqlGeneratePipeline(object):

    def __init__(self):
        if os.path.exists('tz_cms_content_caiji.sql') and os.path.exists('tz_cms_content_article_caiji.sql'):
            self.filem = codecs.open('tz_cms_content_caiji.sql', 'a', encoding='utf-8')
            self.files = codecs.open('tz_cms_content_article_caiji.sql', 'a', encoding='utf-8')
        else:
            self.filem = codecs.open('tz_cms_content_caiji.sql', 'w', encoding='utf-8')
            self.files = codecs.open('tz_cms_content_article_caiji.sql', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        aidpath = 'aid'
        
        if os.path.exists(aidpath):
            with open(aidpath, 'r+') as f:
                aid = int(f.read())
                f.seek(0)
                f.write(str(aid + 1))
        else:
            with open(aidpath, 'w') as f:
                aid = 1
                f.write(str(aid))

        item['content'][0] = item['content'][0].replace('"', '\\\"').replace("'", '\\\'')

        sqlm = u"INSERT INTO tz_cms_content_caiji(classId, cataName, title, urltitle, fontColor, fontBold, fontEm, keywords, description, TIME, image, url, orderNo, states, isAnchor, copyfrom, views, taglink, tplId, tpl, figure, caseType, isNotice, disabled, updateTime, createTime, updateUserId, createUserId, updateUserName, createUserName, seoTitle, seoKeyword, seoDescription, publishTime, shortTitle, aid) VALUES  ( '{classId}', '{cataName}', '{title}', NULL, NULL, NULL, NULL, '{keywords}', '{description}', NULL, '{image}', '', 0, 1, 1, '{source}', '{views}', '0', NULL, '', '', '', 0, 0, {publishTime}, {publishTime}, '999', '999', NULL, 'caiji', '{title}-中投在线', '{seo_keywords}', '{seo_description}', {publishTime}, NULL, '{aid}');\r\n"
        sqls = u"INSERT INTO tz_cms_content_article_caiji( contentId ,content ,disabled ,updateTime,createTime,updateUserId,createUserId,updateUserName,createUserName,aid) values ( null,'{content}',0,{publishTime}, {publishTime},'999','999','caiji','caiji','{aid}' );\r\n"

        sqlm = sqlm.replace('{classId}', item['classId'][0] if 'classId' in item else '') \
        .replace('{cataName}', item['cataName'][0] if 'cataName' in item else '') \
        .replace('{title}', item['title'][0] if 'title' in item else '') \
        .replace('{keywords}', ' '.join(item['keywords']) if 'keywords' in item else '') \
        .replace('{description}', item['description'][0] if 'description' in item else '') \
        .replace('{seo_keywords}', '') \
        .replace('{seo_description}', '') \
        .replace('{source}', item['source'][0] if 'source' in item else '') \
        .replace('{image}', item['title_image'] if 'title_image' in item else '') \
        .replace('{publishTime}', '\'%s\'' % (item['publishTime'][0],) if 'publishTime' in item else 'now()') \
        .replace('{views}', str(item['views'][0]) if 'views' in item else str(randint(100, 999))) \
        .replace('{aid}', str(aid)) \

        sqls = sqls.replace('{content}', item['content'][0]) \
        .replace('{publishTime}', '\'%s\'' % (item['publishTime'][0],) if 'publishTime' in item else 'now()') \
        .replace('{aid}', str(aid)) \

        self.filem.write(sqlm)
        self.files.write(sqls)

        return item

    def spider_closed(self, spider):
        self.filem.close()
        self.files.close()