import scrapy
from scispider.items import PdfItem


class AaaiSpider(scrapy.Spider):
    name = "aaai"
    start_urls = "https://ojs.aaai.org/index.php/AAAI/issue/view/553"
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
        papers = response.xpath("//ul[@class='cmp_article_list articles']/li")
        for paper in papers:
            title = paper.xpath("./div/h3[@class='title']/a/text()").get()
            for _ in "/\:*\"<>|?":
                title = title.replace(_, "").strip()
            pdf_url = paper.xpath(".//a[@class='obj_galley_link pdf']/@href").get()
            pdf_name = f"2023/aaai/{title}.pdf"
            item = PdfItem()
            item['file_name'] = pdf_name
            item['file_url'] = pdf_url
            yield item
