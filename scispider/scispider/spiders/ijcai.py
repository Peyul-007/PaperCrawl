import scrapy
from scispider.items import PdfItem


class IjcaiSpider(scrapy.Spider):
    name = "ijcai"
    start_urls = "https://www.ijcai.org/proceedings/2023/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "scispider.pipelines.PdfPipeline": 300,
        },
        'LOG_LEVEL': 'ERROR'
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls,
            callback=self.parse_papers,
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
