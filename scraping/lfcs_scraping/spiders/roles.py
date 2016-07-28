import scrapy
from lfcs_scraping.items import RoleItem

class ResearchEx(scrapy.Spider):
    name = 'research'
    start_urls = [
            'http://www.research.ed.ac.uk/portal/'
            ]
    
    def parse(self, response):
        with open('names.txt','r') as f:
            names = f.read().splitlines()

        for person in names:
            request = scrapy.FormRequest.from_response(
                    response,
                    formdata = {'searchall':person},
                    callback=self.getlink
                    )
            request.meta['person'] = person
            yield request

    def getlink(self, response):
        link = response.xpath('//div[./ul/li/a[@rel="Organisation"]/span[text()="Laboratory for Foundations of Computer Science"] and ./preceding::h2[1]/a/span[text()="Staff"]]/h2/a/@href').extract()
        if not link:
            return
        item = ExplorerItem()
        item['link'] = link[0]
        item['person'] = response.meta['person']
        yield item

class ExploreRole(scrapy.Spider):
    
    name = 'explorerole'
    start_urls = [
            'http://www.research.ed.ac.uk/portal/'
            ]

    def parse(self, response):
        with open('names.txt','r') as f:
            names = f.read().splitlines()

        for person in names:
            request = scrapy.FormRequest.from_response(
                    response,
                    formdata = {'searchall':person},
                    callback=self.getlink
                    )
            request.meta['person'] = person
            yield request

    def getlink(self, response):
        link = response.xpath('//div[./ul/li/a[@rel="Organisation"]/span[text()="Laboratory for Foundations of Computer Science"] and ./preceding::h2[1]/a/span[text()="Staff"]]/h2/a/@href').extract()
        if not link:
            return
        request = scrapy.Request(response.urljoin(link[0]), callback=self.parse_roles)
        request.meta['person'] = response.meta['person']
        yield request

    def parse_roles(self, response):
        role = response.xpath('//h2[@class="title"]/following::p[@class="type"][1]/text()').extract()
        if not role:
            return
        item = RoleItem()
        item['person'] = response.meta['person']
        item['role'] = role[0]
        yield item
