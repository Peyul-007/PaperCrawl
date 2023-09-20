import scrapy
from paperspider.items import PdfItem


class IjcaiSpider(scrapy.Spider):
    name = "ijcai"
    start_urls = "https://www.ijcai.org/proceedings/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "paperspider.pipelines.PdfPipeline": 300,
        },
        'LOG_LEVEL': 'ERROR'
    }

    def start_requests(self):
        for i in range(2017,2024):
            yield scrapy.Request(
                url=self.start_urls+i,
                callback=self.parse_detail,
                method="GET",
                headers=self.headers
            )

    def parse_detail(self, response):
        for paper in response.xpath("//div[@class='paper_wrapper']/div[@class='details']/a[2]/@href").getall():
            yield scrapy.Request(
                url=self.start_urls+paper,
                callback=self.parse_detail,
                method="GET",
                headers=self.headers
            )

    def parse_papers(self, response):
        papers = response.xpath("//div[@class='paper_wrapper']")
        for paper in papers:
            title = paper.xpath("./div[@class='title']/text()").get()
            for _ in "/\:*\"<>|?":
                title = title.replace(_, "")
            pdf_url = paper.xpath("./div[@class='details']/a[1]/@href").get()
            pdf_name = f"2023/ijcai/{title}.pdf"
            item = PdfItem()
            item['file_name'] = pdf_name
            item['file_url'] = self.start_urls+pdf_url
            yield item
