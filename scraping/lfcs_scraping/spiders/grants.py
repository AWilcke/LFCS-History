import scrapy
from lfcs_scraping.items import GrantItem, Grant2Item

class Grant(scrapy.Spider):

    name = 'grant'
    start_urls = [
            'http://gow.epsrc.ac.uk/PersonSearch.aspx'
            ]
    
    def parse(self, response):
        with open('names.txt','r') as f:
            names = f.read().splitlines()

        for person in names:
            request = scrapy.FormRequest.from_response(
                    response,
                    formdata={'txtSurname':person.split(' ')[-1]},
                    callback=self.find_person
            )
            request.meta['person'] = person
            yield request

    def find_person(self, response):

        people = response.xpath('//tr[./td/text()="Sch of Informatics"]/td/a[@title="University of Edinburgh"]')
        for person in people:
            name = person.xpath('text()').extract()[0]
            print name
            if name.split(' ')[-1] == response.meta['person'].split(' ')[-1]:
                url = person.xpath('@href').extract()[0]
                request = scrapy.Request(response.urljoin(url), callback=self.parse_person)
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
        item['ref'] = response.xpath('//span[@id="lblGrantReference"]/text()').extract()[0]
        yield item


class Grant2(scrapy.Spider):

    name = 'grant_secondary'
    start_urls = [
            'http://gow.epsrc.ac.uk/PersonSearch.aspx'
            ]
    
    def parse(self, response):
        with open('names.txt','r') as f:
            names = f.read().splitlines()

        for person in names:
            request = scrapy.FormRequest.from_response(
                    response,
                    formdata={'txtSurname':person.split(' ')[-1]},
                    callback=self.find_person
            )
            request.meta['person'] = person
            yield request

    def find_person(self, response):

        people = response.xpath('//tr[./td/text()="Sch of Informatics"]/td/a[@title="University of Edinburgh"]')
        for person in people:
            name = person.xpath('text()').extract()[0]
            if name.split(' ')[-1] == response.meta['person'].split(' ')[-1]:
                url = person.xpath('@href').extract()[0]
                request = scrapy.Request(response.urljoin(url), callback=self.parse_person)
                request.meta['person'] = response.meta['person']
                yield request

    def parse_person(self, response):

        grants = response.xpath('//tr[./td/text()="(C)" or ./td/text()="(R)"]/td/b/a/@href')

        for grant in grants:
            request = scrapy.Request(response.urljoin(grant.extract()), callback=self.parse_grant)
            request.meta['person'] = response.meta['person']
            yield request

    def parse_grant(self, response):
        item = Grant2Item()
        item['title'] = response.xpath('//span[@id="lblTitle"]/strong/text()').extract()[0]
        item['person'] = response.meta['person']
        item['primary'] = response.xpath('//td[./a[@id="hlPrincipalInvestigator"]]/a[@href]/text()').extract()[0]
        item['ref'] = response.xpath('//span[@id="lblGrantReference"]/text()').extract()[0]
        yield item
