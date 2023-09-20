# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
import threading
from scrapy_djangoitem import DjangoItem
from .settings import FILES_STORE, NUM_THREADS
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
    def get_media_requests(self, item, info):
        yield scrapy.Request(item['file_url'], meta={"download_timeout": 36000})

    def file_path(self, request, response=None, info=None, *, item=None):
        return f"downloads/{item['file_name']}"

    def get_downloaded_path(self, item) -> str:
        return f'{str(FILES_STORE)}/{item["file_name"]}'
