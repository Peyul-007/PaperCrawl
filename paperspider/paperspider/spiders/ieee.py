import scrapy


class IeeeSpider(scrapy.Spider):
    name = "ieee"
    start_urls = "https://ojs.aaai.org/index.php/AAAI/issue/view/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         "paperspider.pipelines.PdfPipeline": 300,
    #     },
    #     'LOG_LEVEL': 'INFO'
    # }

    def start_requests(self):
        pass        