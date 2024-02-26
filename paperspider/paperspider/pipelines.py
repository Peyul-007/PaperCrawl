# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
from itemadapter import ItemAdapter
import scrapy
import threading
from scrapy.exceptions import DropItem
from scrapy_djangoitem import DjangoItem
from .settings import BASE_DIR, FILES_STORE, NUM_THREADS
from scrapy.pipelines.files import FilesPipeline
from concurrent.futures import ThreadPoolExecutor


class InfoPipeline():
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=NUM_THREADS)
        self.lock = threading.Lock()

    def process_item(self, item: DjangoItem, spider: scrapy.Spider):
        model = item.django_model
        self.thread_pool.submit(self.save_data, dict(item), model)
        return item

    def save_data(self, item: dict, model):
        with self.lock:
            model.objects.get_or_create(**item)


class PdfPipeline(FilesPipeline):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    def open_spider(self, spider):
        self.spiderinfo = self.SpiderInfo(spider)
        self.db = f'{BASE_DIR}/backend/db.sqlite3'
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()

    # def close_spider(self,spider):
    #     self.cursor.close()
    #     self.conn.close()

    def get_media_requests(self, item, info):
        print(item['file_url'])
        yield scrapy.Request(item['file_url'], meta={"download_timeout": 36000}, dont_filter=True, headers=self.headers)

    def file_path(self, request, response=None, info=None, *, item=None):
        return f"downloads/{item['file_name']}"

    def get_downloaded_path(self, item) -> str:
        return f'{str(FILES_STORE)}/{item["file_name"]}'

    def item_completed(self, results, item, info):
        pdf_paths = [x['path'] for ok, x in results if ok]
        if not pdf_paths:
            raise DropItem('Pdf Downloaded Failed')
        else:
            self.cursor.execute(
                "UPDATE crawler_info SET file_url=? WHERE id=?", (item['file_name'], str(item['paper_id'])))
            self.conn.commit()
        return item
