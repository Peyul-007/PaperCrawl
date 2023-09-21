import scrapy
from paperspider.items import PdfItem
from paperspider.items import InfoItem


class IjcaiSpider(scrapy.Spider):
    name = "ijcai"
    start_urls = "https://www.ijcai.org/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "paperspider.pipelines.InfoPipeline": 300,
        },
        'LOG_LEVEL': 'INFO'
    }

    def start_requests(self):
        for i in range(2017, 2024):
            yield scrapy.Request(
                url=f"{self.start_urls}proceedings/{i}",
                callback=self.parse_detail,
                method="GET",
                headers=self.headers,
                meta={
                    'year': i
                }
            )

    def parse_detail(self, response):
        if response.meta['year'] == 2017 or response.meta['year'] == 2018:
            start = 2
        else:
            start = 1
        main_track = response.xpath('//div[@class="section"]')[start]
        for subsection in main_track.xpath('./div[@class="subsection"]'):
            sub_title = subsection.xpath(
                './div[@class="subsection_title"]/text()').get().strip()
            for paper in subsection.xpath("./div[@class='paper_wrapper']/div[@class='details']/a[2]/@href").getall():
                yield scrapy.Request(
                    url=self.start_urls+paper,
                    callback=self.parse_info,
                    method="GET",
                    headers=self.headers,
                    meta={
                        'year': response.meta['year'],
                        'track': sub_title
                    }
                )
        for track in response.xpath('//div[@class="section"]')[start+1:]:
            track_titile = track.xpath(
                './div[@class="section_title"]/h3/text()').get().strip()
            for paper in track.xpath(".//div[@class='paper_wrapper']/div[@class='details']/a[2]/@href").getall():
                yield scrapy.Request(
                    url=self.start_urls+paper,
                    callback=self.parse_info,
                    method="GET",
                    headers=self.headers,
                    meta={
                        'year': response.meta['year'],
                        'track': track_titile
                    }
                )

    def parse_info(self, response):
        item = InfoItem()
        item['title'] = response.xpath(
            '//h1[@class="page-title"]/text()').get().strip()
        item['author'] = response.xpath(
            '//h2/text()').get().split(',')[0].strip()
        item['year'] = response.meta['year']
        item['journal'] = 'ijcai'
        item['doi'] = response.xpath(
            '//a[@class="doi"]/text()').get().strip()
        item['abstract'] = response.xpath(
            '//div[@class="container-fluid proceedings-detail"]/div[3]/div[1]/text()').get().strip()
        item['pdf_url'] = response.xpath(
            '//a[@class="button btn-lg btn-download"][1]/@href').get()
        item['track'] = response.meta['track']
        yield item

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
