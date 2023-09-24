import sqlite3
import scrapy
from scrapy import signals
from paperspider.items import PdfItem
from paperspider.settings import BASE_DIR


class PdfSpider(scrapy.Spider):
    name = "pdf"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "paperspider.pipelines.PdfPipeline": 300,
        },
        'RANDOM_DELAY' : 10,
        'LOG_LEVEL': 'ERROR',
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(PdfSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def __init__(self):
        conn = sqlite3.connect(f'{BASE_DIR}/backend/db.sqlite3')
        self.conn = conn
        self.logger.info('Connection to database opened')
        super(PdfSpider, self)

    def spider_closed(self, spider):
        self.conn.close()
        self.logger.info('Connection to database closed')

    def errback_httpbin(self):
        self.logger.info('http error')

    def start_requests(self):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT pdf_url,author,year,journal,id FROM crawler_info')
        rows = cursor.fetchall()
        item = PdfItem()
        for row in rows:
            author = row[1]
            for _ in "/\:*\"<>|?":
                author = author.replace(_, "")
            pdf_name = f"{row[2]}/{row[3]}/{row[1]}_{row[4]}.pdf"
            item['file_name'] = pdf_name
            item['file_url'] = row[0]
            yield item
        cursor.close()
