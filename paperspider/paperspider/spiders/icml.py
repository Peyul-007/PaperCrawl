import json
import re
import scrapy
from paperspider.items import InfoItem


class IcmlSpider(scrapy.Spider):
    name = "icml"
    start_urls = "https://proceedings.mlr.press/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "paperspider.pipelines.InfoPipeline": 300,
        },
        'LOG_LEVEL': 'ERROR'
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls,
            callback=self.parse_icml,
            method="GET",
            headers=self.headers
        )
        # yield scrapy.Request(
        #     url="https://proceedings.mlr.press/v202/hizli23a.html",
        #     callback=self.parse_info,
        #     method="GET",
        #     headers=self.headers,
        #     meta={
        #         'year': 2023
        #     }
        # )

    def parse_icml(self, response):
        list = response.xpath('//ul[@class="proceedings-list"]/li')
        pattern = re.compile(r'\d+')
        for pro in list:
            if pro.xpath('./text()').get():
                if 'ICML' in pro.xpath('./text()').get() and 'Workshop' not in pro.xpath('./text()').get():
                    year = pattern.search(pro.xpath('./text()').get()).group()
                    yield scrapy.Request(
                        url=self.start_urls+pro.xpath('./a/@href').get(),
                        callback=self.parse_detail,
                        method="GET",
                        headers=self.headers,
                        meta={
                            'year': year
                        }
                    )

    def parse_detail(self, response):
        for paper in response.xpath('//div[@class="paper"]'):
            yield scrapy.Request(
                url=paper.xpath('./p[@class="links"]/a[1]/@href').get(),
                callback=self.parse_info,
                method="GET",
                headers=self.headers,
                meta={
                    'year': response.meta['year']
                }
            )

    def parse_info(self, response):
        item = InfoItem()
        item['journal'] = 'icml'
        item['author'] = response.xpath(
            '//span[@class="authors"]/text()').get().split(',')[0]
        item['title'] = response.xpath(
            '//article[@class="post-content"]/h1/text()').get().strip()
        item['abstract'] = response.xpath(
            'string(//div[@class="abstract"])').get().strip()
        item['year'] = response.meta['year']
        item['pdf_url'] = response.xpath(
            '//div[@id="extras"]/ul/li[1]/a/@href').get()
        # print(item)
        # bibtex = response.xpath('//code[@id="bibtex"]/text()').get()
        # for field in re.findall(r'(\w+)\s*=\s*\{(.*?)\}', bibtex):
        #     if field[0] == 'pdf':
        #         item['pdf_url'] = field[1]
        # print(item)
        yield item

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
