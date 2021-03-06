import scrapy
from lfcs_scraping.items import GrantItem

class Grant(scrapy.Spider):

    name = 'grant_single'
    start_urls = [
            'http://gow.epsrc.ac.uk/PersonSearch.aspx'
            ]
    
    def parse(self, response):
        person = 'Aspinall'
        request = scrapy.FormRequest.from_response(
                response,
                formdata={'txtSurname':person},
                callback=self.find_person
        )
        request.meta['person'] = person
        yield request

    def find_person(self, response):
        print "RESPONSE"
        print response.url
        people = response.xpath('//tr[./td/text()="Sch of Informatics"]/td/a[@title="University of Edinburgh"]/@href').extract()
        print people
        for person in people:
            request = scrapy.Request(response.urljoin(person), callback=self.parse_person)
            request.meta['person'] = response.meta['person']
            yield request

    def parse_person(self, response):

        grants = response.xpath('//tr[./td/text()="(P)"]/td/b/a/@href').extract()
        for grant in grants:
            request = scrapy.Request(response.urljoin(grant), callback=self.parse_grant)
            request.meta['person'] = response.meta['person']
            yield request

    def parse_grant(self, response):
        item = GrantItem()
        item['title'] = response.xpath('//span[@id="lblTitle"]/strong/text()').extract()[0]
        item['start'] = response.xpath('//span[@id="lblStarts"]/text()').extract()[0]
        item['end'] = response.xpath('//span[@id="lblEnds"]/text()').extract()[0]
        item['value'] = response.xpath('//span[@id="lblValue"]/text()').extract()[0]
        item['person'] = response.meta['person']
        item['url'] = response.url
        yield item


