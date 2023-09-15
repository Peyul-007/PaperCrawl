# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PdfItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    file_url = scrapy.Field()
    file_name = scrapy.Field()

class InfoItem(scrapy.Item):
    file_name = scrapy.Field()
    author = scrapy.Field()
    title = scrapy.Field()
    proceedings = scrapy.Field()
    abstract = scrapy.Field()