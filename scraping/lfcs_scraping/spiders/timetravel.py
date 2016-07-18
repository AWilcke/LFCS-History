import scrapy
from lfcs_scraping.items import TimeItem

class TimeTravel(scrapy.Spider):
    name = 'timetravel'
    #allowed_domains = ['http://web.archive.org/']
    start_urls = [
            'http://web.archive.org/web/20160615173215/http://wcms.inf.ed.ac.uk/lfcs/people'
            ]

    def parse(self, response):
        
        item = TimeItem()
        
        nextpage = response.xpath('//tr[@class="y"]/td[@class="b"]/a/@href').extract() 
        item['url'] = response.url
        item['date'] = response.xpath('//tr[@class="y"]/td[@class="c"]/text()').extract()[0]
        yield item

        if nextpage:
            yield scrapy.Request(response.urljoin(nextpage[0]), callback=self.parse)
