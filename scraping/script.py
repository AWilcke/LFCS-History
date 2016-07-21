from scrapy.utils.project import get_project_settings
import scrapy
import json
from scrapy.crawler import CrawlerProcess
from lfcs_scraping.items import Grant2Item
from lfcs_scraping.spiders.grants import Grant2

class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('items.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

settings = get_project_settings()
settings.set('ITEM_PIPELINES', {
    '__main__.JsonWriterPipeline': 100
})

process = CrawlerProcess(settings)
spider = Grant2()
process.crawl(spider)
process.start()
