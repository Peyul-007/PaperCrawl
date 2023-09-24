import scrapy
from paperspider.items import InfoItem, PdfItem


class NeuripsSpider(scrapy.Spider):
    name = "neurips"
    start_urls = "https://proceedings.neurips.cc"
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
        for i in range(2010, 2023):
            yield scrapy.Request(
                url=f"{self.start_urls}/paper_files/paper/{i}",
                callback=self.parse_detail,
                method="GET",
                headers=self.headers,
                meta={
                    'year': i
                }
            )

        # yield scrapy.Request(
        #         url="https://proceedings.neurips.cc/paper_files/paper/2018/hash/fc325d4b598aaede18b53dca4ecfcb9c-Abstract.html",
        #         callback=self.parse_info,
        #         method="GET",
        #         headers=self.headers,
        #         meta={
        #             'year': 2016
        #         }
        #     )

    def parse_detail(self, response):
        papers = response.xpath(
            "//ul[@class=' paper-list']/li/a/@href").getall()
        for paper in papers:
            yield scrapy.Request(
                url=f"{self.start_urls}{paper}",
                callback=self.parse_info,
                method="GET",
                headers=self.headers,
                meta={
                    'year': response.meta['year']
                }
            )

    def parse_info(self, response):
        item = InfoItem()
        item['title'] = response.xpath(
            "//div[@class='col']/h4[1]/text()").get().strip()
        item['author'] = response.xpath(
            "//div[@class='col']/p[2]/i/text()").get().split(',')[0].strip()
        item['year'] = response.meta['year']
        item['journal'] = 'neurips'
        abstract = response.xpath(
            "string(//div[@class='col']/p[3])").get()+response.xpath(
            "string(//div[@class='col']/p[4])").get()
        item['abstract'] = abstract.strip()
        for a in response.xpath(
                "//div[@class='col']/div[1]/a"):
            if a.xpath('./text()').get().strip() == 'Paper':
                item['pdf_url'] = f"{self.start_urls}{a.xpath('./@href').get()}"
        yield item

    def parse_papers(self, response):
        title = response.xpath("//div[@class='col']/h4[1]/text()").get()
        for _ in "/\:*\"<>|?":
            title = title.replace(_, "")
        pdf_url = response.xpath(
            "//a[@class='btn btn-primary btn-spacer']/@href").get()
        pdf_name = f"2022/neurips/{title}.pdf"
        item = PdfItem()
        item['file_name'] = pdf_name
        item['file_url'] = f"https://proceedings.neurips.cc{pdf_url}"
        yield item
