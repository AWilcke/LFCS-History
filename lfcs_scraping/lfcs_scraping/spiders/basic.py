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
        #two cases for name formatting
        for name in response.xpath('//table//a/strong | //table//strong/a'):
            try:
                m = re.search('(.+) (\S+)', name.xpath('text()').extract()[0])
            except:
                print name
                pass

            if m:
                item = PersonItem()
                item['first'] = m.group(1)
                item['last']= m.group(2)
                role = name.xpath('preceding::h2[1]/text()').extract()
                item['role'] = role
                yield item
            else:
                print name.xpath('text()').extract()[0]
                pass
