import os
import re
import scrapy
from scispider.items import PdfItem


class TestSpider(scrapy.Spider):
    name = "test"
    start_urls = "https://proceedings.mlr.press"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "scispider.pipelines.PdfPipeline": 300,
        },
        'DOWNLOAD_MAXSIZE' : 0,
        "DOWNLOAD_DELAY": 10,
        # 'LOG_LEVEL': 'ERROR'
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls,
            callback=self.parseurl,
            method="GET",
            headers=self.header
        )

    def parseurl(self, response):
        proceedings = response.xpath("//ul[@class='proceedings-list']/li")
        target = "ICML|AAAI|IJCAI| KDD|NeurIPS"
        for proceeding in proceedings:
            proname = proceeding.xpath('./text()').get()
            if proname:
                proname = proname.strip()
                if re.search(target, proname):
                    kind = re.search(target, proname).group().strip()
                    year = re.search(
                        r'\d+', proname).group().strip() if re.search(r'\d+', proname) else 'unknown'
                    volume = proceeding.xpath('./a/b/text()').get()
                    num = volume.split(' ')[1]
                    item = PdfItem()
                    item['file_name'] = f'{year}/{kind}_{volume}.zip'
                    item['file_url'] = f'https://codeload.github.com/mlresearch/v{num}/zip/refs/heads/gh-pages'
                    yield item
