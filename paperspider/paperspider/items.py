# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from crawler.models import Info


class PdfItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    file_url = scrapy.Field()
    file_name = scrapy.Field()
    paper_id = scrapy.Field()


class InfoItem(DjangoItem):
    django_model = Info
