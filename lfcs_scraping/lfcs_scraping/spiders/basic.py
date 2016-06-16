import scrapy
from lfcs_scraping.items import PersonItem
import re

class CurrentLfcs(scrapy.Spider):
    name = "currentlfcs"
    allowed_domains = ["http://wcms.inf.ed.ac.uk/"]
    start_urls = [
            "http://wcms.inf.ed.ac.uk/lfcs/people"
            ]

    def parse(self, response):
        #case where link has bold text
        for name in response.xpath('//table//a/strong/text()').re('.+ \S+'):
            m = re.search('(.+) (\S*)', name)
            item = PersonItem()
            item['first'] = m.group(1)
            item['last']= m.group(2)
            yield item
        #case where link is in bold
        for name in response.xpath('//table//strong/a/text()').re('.+ \S+'):
            m = re.search('(.+) (\S*)', name)
            item = PersonItem()
            item['first'] = m.group(1)
            item['last'] = m.group(2)
            yield item
