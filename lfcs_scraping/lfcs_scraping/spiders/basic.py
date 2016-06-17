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
        
        
        for name in response.xpath('//a/strong/u | //a/strong[not(u)] | //strong/a'):
            try:
                m = re.search('(.+) (\S+)', name.xpath('text()').extract()[0])
            #if fails, it's because there was no text to extract, was a false positive
            except:
                pass

            if m:
                item = PersonItem()
                item['url'] = name.xpath('@href | ../@href | ../../@href').extract()
                
                item['role'] = name.xpath('preceding::h2[1]/text() | preceding::h2[1]/a/text()').extract()
                item['last'] = m.group(2)
                item['first'] = m.group(1)
                yield item
            #if no match then it isnt a name
            else:
                pass
