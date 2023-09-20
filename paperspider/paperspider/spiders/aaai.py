import scrapy
from paperspider.items import InfoItem


class AaaiSpider(scrapy.Spider):
    name = "aaai"
    start_urls = "https://ojs.aaai.org/index.php/AAAI/issue/archive"

    # start_urls = "https://ojs.aaai.org/index.php/AAAI/issue/view/"
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
            callback=self.parse_tracks,
            method="GET",
            headers=self.headers
        )

    def parse_tracks(self, response):
        for track_url in response.xpath('//ul[@class="issues_archive"]/li/div/h2/a/@href').getall():
            yield scrapy.Request(
                    url=track_url,
                    callback=self.parse_detail,
                    method="GET",
                    headers=self.headers
                )
        if response.xpath('//a[@class="next"]/@href').get():
            yield scrapy.Request(
                url=response.xpath('//a[@class="next"]/@href').get(),
                callback=self.parse_tracks,
                method="GET",
                headers=self.headers
            )
        
    def parse_detail(self, response):
        papers = response.xpath("//ul[@class='cmp_article_list articles']/li")
        for paper in papers:
            yield scrapy.Request(
                url=paper.xpath("./div/h3[@class='title']/a/@href").get(),
                callback=self.parse_info,
                method="GET",
                headers=self.headers
            )

    def parse_info(self,response):
        item = InfoItem()
        item['title'] = response.xpath('//h1[@class="page_title"]/text()').get().strip()
        item['author'] = response.xpath('//ul[@class="authors"]/li[1]/span[@class="name"]/text()').get().strip()
        if response.xpath('//ul[@class="authors"]/li[1]/span[@class="affiliation"]/text()').get():
            item['institution'] = response.xpath('//ul[@class="authors"]/li[1]/span[@class="affiliation"]/text()').get().strip()
        item['year'] = response.xpath('//div[@class="item published"]/section/div[@class="value"]/span/text()').get().strip().split('-')[0]
        item['journal'] = 'aaai'
        item['doi'] = response.xpath('//section[@class="item doi"]/span/a/text()').get().strip()
        if response.xpath('//section[@class="item abstract"]/text()[2]').get():
            item['abstract'] = response.xpath('//section[@class="item abstract"]/text()[2]').get().strip()
        item['pdf_url'] = response.xpath('//a[@class="obj_galley_link pdf"]/@href').get()
        item['track'] = response.xpath('//div[@class="item issue"]/section[2]/div/text()').get().strip()
        yield item

    def parse_pdf(self, response):
        papers = response.xpath("//ul[@class='cmp_article_list articles']/li")
        for paper in papers:
            title = paper.xpath("./div/h3[@class='title']/a/text()").get()
            for _ in "/\:*\"<>|?":
                title = title.replace(_, "").strip()
            pdf_url = paper.xpath(
                ".//a[@class='obj_galley_link pdf']/@href").get()
            pdf_name = f"2023/aaai/{title}.pdf"
            item = InfoItem()
            item['file_name'] = pdf_name
            item['file_url'] = pdf_url
            yield item
