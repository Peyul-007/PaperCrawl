# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from .settings import FILES_STORE
from scrapy.pipelines.files import FilesPipeline


class PdfPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request(item['file_url'], meta={"download_timeout": 36000})

    def file_path(self, request, response=None, info=None, *, item=None):
        return f"downloads/{item['file_name']}"
    
    def get_downloaded_path(self, item) -> str:
        return f'{str(FILES_STORE)}/{item["file_name"]}'
    