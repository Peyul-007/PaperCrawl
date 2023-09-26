import sqlite3
import scrapy
from paperspider.items import PdfItem
from paperspider.settings import BASE_DIR


class PdfSpider(scrapy.Spider):
    name = "pdf"
    start_urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "paperspider.pipelines.PdfPipeline": 300,
        },
        'LOG_LEVEL': 'ERROR',
        'DOWNLOAD_DELAY': 5
    }

    def __init__(self, db):
        self.db = db
        self.rows = self.get_urls_from_db(db)

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        spider = self(
            db=f'{BASE_DIR}/backend/db.sqlite3'
        )
        spider._set_crawler(crawler)
        return spider

    def get_urls_from_db(self, db):
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT pdf_url,author,year,journal,id FROM crawler_info')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def start_requests(self):
        for row in self.rows:
            author = row[1]
            for _ in "/\:*\"<>|?":
                author = author.replace(_, "")
            pdf_name = f"{row[2]}/{row[3]}/{row[1]}_{row[4]}.pdf"
            yield scrapy.Request(
                url=row[0],
                callback=self.parse_pdf,
                method="GET",
                headers=self.headers,
                meta={
                    'file_name':pdf_name,
                    'file_url':row[0]
                }
            )

    def parse_pdf(self, response):
        item = PdfItem()
        item['file_name'] = response.meta['file_name']
        item['file_url'] = response.meta['file_url']
        yield item
