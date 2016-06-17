import scrapy
from lfcs_scraping.items import PersonItem
import re

class FirstTime(scrapy.Spider):
    name = "first"
    start_urls = [
            'http://web.archive.org/web/20160615173215/http://wcms.inf.ed.ac.uk/lfcs/people'
             ]

    def parse(self, response):

        for name in response.xpath('//a/strong/u | //a/strong[not(u)] | //strong/a[not(strong)]'):
            try:
                m = re.search('(.+) (\S+)', name.xpath('text()').extract()[0])
            #if fails, it's because there was no text to extract, was a false positive
            except:
                pass

            if m:
                item = PersonItem()
                item['url'] = name.xpath('@href | ../@href | ../../@href').re('.*(http.*)')[0]
                item['role'] = name.xpath('preceding::h2[1]/text() | preceding::h2[1]/a/text() | preceding::h3[1]/text()').extract()
                item['last'] = m.group(2)
                item['first'] = m.group(1)
                item['year'] = response.xpath('//tr[@class="y"]/td[@class="c"]/text()').extract()[0]
                yield item
            #if no match then it isnt a name
            else:
                pass
        
        nextpage = response.xpath('//tr[@class="y"]/td[@class="b"]/a/@href').extract()
        if nextpage:
            yield scrapy.Request(response.urljoin(nextpage[0]), callback=self.parse)
 
