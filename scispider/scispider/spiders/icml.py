import json
import scrapy
from scispider.items import PdfItem


class IcmlSpider(scrapy.Spider):
    name = "icml"
    start_urls = "https://icml.cc/static/virtual/data/icml-2023-orals-posters.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "scispider.pipelines.PdfPipeline": 300,
        },
        'LOG_LEVEL': 'INFO'
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls,
            callback=self.parse_papers,
            method="GET",
            headers=self.headers
        )

    def parse_papers(self, response):
        resp = json.loads(str(response.body, 'utf-8'))
        for paper in resp['results']:
            if paper['eventmedia']:
                if 'uri' in paper['eventmedia'][0] and 'http://' in paper['eventmedia'][0]['uri']:
                    title = paper['name']
                    for _ in "/\:*\"<>|?":
                        title = title.replace(_, "")
                    pdf_url = paper['eventmedia'][0]['uri']
                    pdf_name = f"2023/icml/{title}.pdf"
                    item = PdfItem()
                    item['file_name'] = pdf_name
                    item['file_url'] = pdf_url
                    yield item
