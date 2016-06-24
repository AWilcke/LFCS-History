import scrapy
from lfcs_scraping.items import PersonItem
import re

class First(scrapy.Spider):
    name = "first"
    start_urls = [
                    'http://web.archive.org/web/20160506183023/http://wcms.inf.ed.ac.uk/lfcs/people',
                    'http://web.archive.org/web/20110319001651/http://wcms.inf.ed.ac.uk/lfcs/people'
             ]

    def parse(self, response):

        for name in response.xpath('//a/strong/u | //a/strong[not(u)] | //strong/a[not(strong)]'):
            try:
                m = re.search('([^\d]+) (\S+)', name.xpath('text()').extract()[0])
            #if fails, it's because there was no text to extract, was a false positive
            except:
                m = None

            if m:
                item = PersonItem()
                item['url'] = name.xpath('@href | ../@href | ../../@href').re('.*(http.*)')[0]
                item['role'] = re.sub('.*\xa0', '', name.xpath('preceding::h2[1]/text() | preceding::h2[1]/a/text() | preceding::h3[1]/text()').extract()[0])
                item['last'] = m.group(2)
                item['first'] = m.group(1)
                item['year'] = response.xpath('//tr[@class="y"]/td[@class="c"]/text()').extract()[0]
                yield item
        
        nextpage = response.xpath('//tr[@class="y"]/td[@class="f"]/a/@href').extract()
        if nextpage:
            yield scrapy.Request(response.urljoin(nextpage[0]), callback=self.parse)

class Second(scrapy.Spider):
    name = "second"
    start_urls = [
            "http://web.archive.org/web/20070611175309/http://www.lfcs.inf.ed.ac.uk/people/"
            ]

    def parse(self, response):
        for name in response.xpath("//div[not(@id='wm-ipp')]//table//a"):
            
            try:
                m = re.search('([^\d]+) (\S+)', re.sub('\xa0', ' ', name.xpath("text()").extract()[0]))
            except:
                m = None
            if m:
                item = PersonItem()
                item['role'] = name.xpath("preceding::h3[1]/text()").extract()[0]
                item['last'] = m.group(2)
                item['first'] = m.group(1)
                item['year'] = response.xpath('//tr[@class="y"]/td[@class="c"]/text()').extract()[0]
                yield item
        
        nextpage = response.xpath('//tr[@class="y"]/td[@class="b"]/a/@href').extract()
        if nextpage:
            yield scrapy.Request(response.urljoin(nextpage[0]), callback=self.parse)

class Third(scrapy.Spider):
    name='third'
    start_urls = [
            "http://web.archive.org/web/20040109002116/http://www.inf.ed.ac.uk/research/lfcs/members.html",
            "http://web.archive.org/web/20040109002125/http://www.inf.ed.ac.uk/research/lfcs/support.html",
            "http://web.archive.org/web/20040109002026/http://www.inf.ed.ac.uk/research/lfcs/students.html"
            ]

    def parse(self, response):
        return
        #to be completed
