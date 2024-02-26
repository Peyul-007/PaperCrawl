import scrapy
from paperspider.items import InfoItem, PdfItem


class KddSpider(scrapy.Spider):
    name = "kdd"
    start_urls = "https://dl.acm.org"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Host': 'dl.acm.org'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "paperspider.pipelines.InfoPipeline": 300,
        },
        'RANDOM_DELAY': 1,
        'DOWNLOAD_DELAY': 3,
        'LOG_LEVEL': 'DEBUG',
    }

    def start_requests(self):
        yield scrapy.Request(
            url=f"{self.start_urls}/conference/kdd/proceedings",
            callback=self.parse_year,
            method="GET",
            headers=self.headers,
            dont_filter=True,

        )

    def parse_year(self, response):
        list = response.xpath(
            '//div[@class="conference__title left-bordered-title"]')[0:15]
        for pro in list:
            yield scrapy.Request(
                url=f"{self.start_urls}{pro.xpath('./a/@href').get()}",
                callback=self.parse_detail,
                method="GET",
                headers=self.headers,
                dont_filter=True
            )

    def parse_detail(self, response):
        dois = []
        year = response.xpath('//div[@class="coverDate"]/text()').get().strip()
        papers = response.xpath(
            "//input[@class='section--dois']/@value").getall()
        for paper in papers:
            dois.extend(paper.split(','))
        for d in dois:
            yield scrapy.Request(
                url=f"https://dl.acm.org/doi/{d}",
                callback=self.parse_info,
                method="GET",
                headers=self.headers,
                meta={
                    'doi': d,
                    'year': year
                }
            )

    def parse_info(self, response):
        item = InfoItem()
        item['journal'] = 'kdd'
        item['author'] = response.xpath(
            '//span[@class="loa__author-name"][1]/span/text()').get().strip()
        item['institution'] = response.xpath(
            '//span[@class="loa_author_inst"][1]/p/text()').get()
        item['title'] = response.xpath(
            "string(//h1[@class='citation__title'])").get().strip()
        item['year'] = response.meta['year']
        item['doi'] = f"https://doi.org/{response.meta['doi']}"
        item['abstract'] = response.xpath(
            'string(//div[@class="abstractSection abstractInFull"])').get().strip()
        item['pdf_url'] = f"https://dl.acm.org/doi/pdf/{response.meta['doi']}"
        yield item

    def parse_papers(self, response):
        title = response.xpath("//h1[@class='citation__title']/text()").get()
        for _ in "/\:*\"<>|?":
            title = title.replace(_, "")
        pdf_url = f"https://dl.acm.org/doi/pdf/{response.meta['doi']}"
        pdf_name = f"2023/kdd/{title}.pdf"
        item = PdfItem()
        item['file_name'] = pdf_name
        item['file_url'] = pdf_url
        yield item
