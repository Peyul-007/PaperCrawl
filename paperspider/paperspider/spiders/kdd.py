import scrapy
from paperspider.items import PdfItem


class KddSpider(scrapy.Spider):
    name = "kdd"
    start_urls = "https://dl.acm.org/doi/proceedings/10.1145/3580305"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "paperspider.pipelines.PdfPipeline": 300,
        },
        'RANDOM_DELAY' : 1
        # 'LOG_LEVEL': 'ERROR'
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls,
            callback=self.parse_detail,
            method="GET",
            headers=self.headers,
            dont_filter=True
        )

    def parse_detail(self, response):
        dois = []
        papers = response.xpath("//input[@class='section--dois']/@value").getall()
        for paper in papers:
            dois.extend(paper.split(','))
        for d in dois:
            yield scrapy.Request(
            url=f"https://dl.acm.org/doi/{d}",
            callback=self.parse_papers,
            method="GET",
            headers=self.headers,
            meta={'doi':d}
        )


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
