import os
import re
import scrapy
from scispider.items import PdfItem


class PdfSpider(scrapy.Spider):
    name = "pdf"
    allowed_domains = ["proceedings.mlr.press"]
    start_urls = "https://proceedings.mlr.press"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES' : {
            "scispider.pipelines.PdfPipeline": 300,
        },
        'LOG_LEVEL': 'ERROR'
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
                    yield scrapy.Request(
                        url=self.start_urls+'/' +
                        proceeding.xpath('./a/@href').get(),
                        callback=self.parse,
                        method="GET",
                        headers=self.header,
                        meta={
                            'kind': kind,
                            'year': year
                        }
                    )

    def parse(self, response):
        for paper in response.xpath('//div[@class="paper"]'):
            title = paper.xpath(
                './p[@class="title"]/text()').get()
            for w in "/\:*\"<>|?":
                title=title.replace(w,"")
            href = paper.xpath('./p[@class="links"]/a[2]/@href').get()
            filename = response.meta['year'] + \
                '/'+response.meta['kind']+'/'+title+'.pdf'
            item = PdfItem()
            item['file_name'] = filename
            item['file_url'] = href
            yield item
