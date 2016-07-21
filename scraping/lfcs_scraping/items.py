# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PersonItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    last = scrapy.Field()
    first = scrapy.Field()
    role = scrapy.Field()
    year = scrapy.Field()

class TimeItem(scrapy.Item):
    url = scrapy.Field()
    date = scrapy.Field()

class ReportItem(scrapy.Item):
    first=scrapy.Field()
    last=scrapy.Field()
    thesis=scrapy.Field()

class GrantItem(scrapy.Item):
    title = scrapy.Field()
    ref = scrapy.Field()
    person = scrapy.Field()
    start = scrapy.Field()
    end = scrapy.Field()
    value = scrapy.Field()
    url = scrapy.Field()

class Grant2Item(scrapy.Item):
    person = scrapy.Field()
    title = scrapy.Field()
    ref = scrapy.Field()
    primary = scrapy.Field()

class TestItem(scrapy.Item):
    num = scrapy.Field()
    person = scrapy.Field()
