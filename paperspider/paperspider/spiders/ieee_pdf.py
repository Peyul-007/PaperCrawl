import os
import sqlite3
from PyPDF2 import PdfReader
import scrapy
from paperspider.items import PdfItem
from paperspider.settings import BASE_DIR


class IeeePdfSpider(scrapy.Spider):
    name = "ieeepdf"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "paperspider.pipelines.PdfPipeline": 300,
        },
        'LOG_LEVEL': 'ERROR',
        'RANDOM_DELAY': 2,
        'DOWNLOAD_DELAY': 5,
    }

    def __init__(self, db):
        self.db = db
        self.get_urls_from_db(db)

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
            'SELECT pdf_url,author,year,journal,id,file_url FROM crawler_info WHERE journal=? and year=? and file_url!=?', ("ieee", "2021", ""))
        # cursor.execute(
        #     'SELECT pdf_url,author,year,journal,id FROM crawler_info WHERE journal=? and file_url=? and year=?', ("ieee", "", "2023"))
        self.ieee = cursor.fetchall()
        cursor.close()
        conn.close()

    def start_requests(self):
        yield scrapy.Request(
            url="https://ieeexplore.ieee.org",
            callback=self.parse,
            method="GET",
            headers=self.headers,
        )

        # yield scrapy.Request(
        #     url=url,
        #     callback=self.parse_pdf,
        #     method="GET",
        #     headers=self.headers,
        #     meta={
        #         'file_name': pdf_name,
        #         'file_url': url,
        #         'paper_id': row[4]
        #     }
        # )

    # def parse_pdf(self, response):
    #     item = PdfItem()
    #     item['file_name'] = response.meta['file_name']
    #     item['file_url'] = response.meta['file_url']
    #     item['paper_id'] = response.meta['paper_id']
    #     yield item

    def parse(self, response):
        for row in self.ieee:
            filepath = os.path.join(f"D:\_z\python_workplace\PaperCrawl\paperspider\paperspider\downloads/", row[5])
            if not self.isValidPDF_pathfile(filepath):
                if os.path.exists(filepath):
                    os.remove(filepath)
                author = row[1]
                url = row[0].replace("stamp/stamp.", "stampPDF/getPDF.")
                for _ in "/\:*\"<>|?*":
                    author = author.replace(_, "")
                pdf_name = f"{row[2]}/{row[3]}/{author}_{row[4]}.pdf"
                item = PdfItem()
                item['file_name'] = pdf_name
                item['file_url'] = url
                item['paper_id'] = row[4]
                yield item

    def isValidPDF_pathfile(self, pathfile):
        bValid = True
        try:
            # PdfFileReader(open(pathfile, 'rb'))
            reader = PdfReader(pathfile)
            if len(reader.pages) < 1:  # 进一步通过页数判断。
                bValid = False
        except:
            bValid = False
        return bValid