import scrapy
from lfcs_scraping.items import GrantItem, Grant2Item, ExplorerItem
import re
from datetime import datetime

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
        item['org'] = 'EPSRC'
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

class ExploreGrants(scrapy.Spider):
    
    name = 'exploregrant'
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
        request = scrapy.Request(response.urljoin(link[0]), callback=self.get_projects)
        request.meta['person'] = response.meta['person']
        yield request

    def get_projects(self, response):
        link = response.xpath('//a[./span[text()="\n\t\t\t\t\t\t\t\tProjects\n\t\t\t\t\t\t\t"]]/@href').extract()[0]
        request = scrapy.Request(response.urljoin(link), callback=self.get_all)
        request.meta['person'] = response.meta['person']
        request.meta['url'] = response.url
        yield request

    def get_all(self, response):
        link = response.xpath('//div[@class="portal_navigator_popup_content"]/ul/li/a[./span[text()="100"]]/@href').extract()[0]
        request = scrapy.Request(response.urljoin(link), callback=self.get_grants)
        request.meta['person'] = response.meta['person']
        request.meta['url'] = response.meta['url']
        yield request

    def get_grants(self, response):
        grant_links = response.xpath('//h2[@class="title"]/a[@rel="FundedProject"]/@href').extract()
        for link in grant_links:
            request = scrapy.Request(response.urljoin(link), callback=self.parse_grant)
            request.meta['person'] = response.meta['person']
            request.meta['url'] = response.meta['url']
            yield request

    def parse_grant(self, response):
        principal = response.xpath('//span[@class="dimmed" and text()=" (Principal investigator)"]/preceding-sibling::a[1]/@href').extract()[0]
        if principal != response.meta['url']:
            return
        item = GrantItem()
        value = response.xpath('//table[@class="properties"]/tbody/tr[@class="total-award"]/td/text()').extract()[0]
        item['value'] = int(re.sub('[^\d.]','', value).split('.')[0])
        ref = response.xpath('//table[@class="properties"]/tbody/tr[@class="funder-project-reference"]/td/text()').extract()
        if ref:
            item['ref'] = ref[0]
        else:
            item['ref'] = None
        item['org'] = response.xpath('//table[@class="properties"]/tbody/tr[@class="funding-organisation"]/td/text()').extract()[0]
        item['url'] = response.url
        item['person'] = response.meta['person']
        item['title'] = response.xpath('//h2/span/text()').extract()[0]
        dates = response.xpath('//table[@class="properties"]/tbody/tr[@class="period"]/td/span/text()').extract()
        item['start'] = datetime.strptime(dates[0], '%d/%m/%y').year
        item['end'] = datetime.strptime(dates[1], '%d/%m/%y').year
        yield item

class ExploreGrants2(scrapy.Spider):
    
    name = 'exploregrant2'
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
        request = scrapy.Request(response.urljoin(link[0]), callback=self.get_projects)
        request.meta['person'] = response.meta['person']
        yield request

    def get_projects(self, response):
        link = response.xpath('//a[./span[text()="\n\t\t\t\t\t\t\t\tProjects\n\t\t\t\t\t\t\t"]]/@href').extract()[0]
        request = scrapy.Request(response.urljoin(link), callback=self.get_all)
        request.meta['person'] = response.meta['person']
        request.meta['url'] = response.url
        yield request

    def get_all(self, response):
        link = response.xpath('//div[@class="portal_navigator_popup_content"]/ul/li/a[./span[text()="100"]]/@href').extract()[0]
        request = scrapy.Request(response.urljoin(link), callback=self.get_grants)
        request.meta['person'] = response.meta['person']
        request.meta['url'] = response.meta['url']
        yield request

    def get_grants(self, response):
        grant_links = response.xpath('//h2[@class="title"]/a[@rel="FundedProject"]/@href').extract()
        for link in grant_links:
            request = scrapy.Request(response.urljoin(link), callback=self.parse_grant)
            request.meta['person'] = response.meta['person']
            request.meta['url'] = response.meta['url']
            yield request

    def parse_grant(self, response):
        principal = response.xpath('//span[@class="dimmed" and text()=" (Principal investigator)"]/preceding-sibling::a[1]/@href').extract()[0]
        if principal == response.meta['url']:
            return
        item = Grant2Item()
        ref = response.xpath('//table[@class="properties"]/tbody/tr[@class="funder-project-reference"]/td/text()').extract()
        if ref:
            item['ref'] = ref[0]
        else:
            item['ref'] = None
        item['person'] = response.meta['person']
        item['title'] = response.xpath('//h2/span/text()').extract()[0]
        item['primary'] = response.xpath('//span[@class="dimmed" and text()=" (Principal investigator)"]/preceding-sibling::a[1]/span/text()').extract()[0].split(', ')[0]
        yield item
