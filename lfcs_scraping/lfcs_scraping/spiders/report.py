import scrapy
from lfcs_scraping.items import ReportItem
import re

class Report(scrapy.Spider):
    name='report'
    start_urls = [
            'http://www.lfcs.inf.ed.ac.uk/reports/'
            ]

    def parse(self, response):

        links = response.xpath('//a[preceding::strong/text() = "By Author:"]/@href').extract()

        for link in links:
            m=re.match('^author/.*', link)
            if m:
                yield scrapy.Request(response.urljoin(link), callback=self.parse_letter)

    def parse_letter(self, response):

        names = response.xpath('//dt/b')

        for name in names:
            item = ReportItem()
            item['last'], item['first'] = name.xpath('text()').extract()[0].split(', ')

            publications = name.xpath('following::dd[1]//li')
            
            for publication in publications:
                #check if is PhD thesis
                if publication.xpath('a/i/text()').re('.*CST.*'):
                    thesis = re.sub('\\n','', publication.xpath('b/text()').extract()[0])
                    date = publication.xpath('a/@href').re('/reports/(\d\d)/.*')[0]

                    item['thesis'] = thesis + ' (19' + date + ')'

            yield item

                


