import scrapy
import scrapy.http
import json
from paperspider.items import InfoItem


class IeeeSpider(scrapy.Spider):
    name = "ieee"
    # start_urls = "https://ieeexplore.ieee.org"
    conference_id = ["6488907", "9424", "6221020", "7755", "83", "25", "34"]
    base_url = "https://ieeexplore.ieee.org"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            "paperspider.pipelines.InfoPipeline": 300,
        },
        'LOG_LEVEL': 'ERROR',
        'RANDOM_DELAY': 1,
        'DOWNLOAD_DELAY': 3,
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.base_url+"/xpl/issues?punumber=6488907",
            callback=self.parse_volume,
            method="GET",
            headers=self.headers
        )

    def parse_volume(self, response):
        for cid in self.conference_id:
            yield scrapy.Request(
                url=self.base_url+f"/rest/publication/{cid}/regular-issues",
                callback=self.parse_issue,
                method="GET",
                headers=self.headers,
            )

    def parse_issue(self, response):
        list = json.loads(response.body)
        for dec in list['issuelist'][0:2]:
            for year in dec['years']:
                for issue in year['issues']:
                    yield scrapy.http.JsonRequest(
                        url=self.base_url +
                        f"/rest/search/pub/{str(issue['publicationNumber'])}/issue/{str(issue['issueNumber'])}/toc",
                        callback=self.parse_info,
                        method="POST",
                        data={
                            "isnumber": f"{str(issue['issueNumber'])}",
                            "punumber": f"{str(issue['publicationNumber'])}",
                            "sortType": "vol-only-seq",
                            "rowsPerPage": "100",
                            "pageNumber": 1
                        },
                        meta={
                            "isnumber": str(issue['issueNumber']),
                            "punumber": str(issue['publicationNumber']),
                            'current': 1
                        },
                        headers=self.headers
                    )
                    # yield scrapy.Request(
                    #     url=self.base_url +
                    #     f"/xpl/tocresult.jsp?isnumber={str(issue['issueNumber'])}&punumber={str(issue['publicationNumber'])}",
                    #     callback=self.parse_paper,
                    #     method="GET",
                    #     headers=self.headers,
                    #     meta={
                    #         "isnumber": str(issue['issueNumber']),
                    #         "punumber": str(issue['publicationNumber'])
                    #     }
                    # )

    # def parse_paper(self, response):
    #     yield scrapy.http.JsonRequest(
    #         url=self.base_url +
    #         f"/rest/search/pub/{response.meta['punumber']}/issue/{response.meta['isnumber']}/toc",
    #         callback=self.parse_info,
    #         method="POST",
    #         data={
    #             "isnumber": f"{response.meta['isnumber']}",
    #             "punumber": f"{response.meta['punumber']}",
    #             "sortType": "vol-only-seq",
    #             "rowsPerPage": "100",
    #             "pageNumber": 1
    #         },
    #         errback=self.parse_info,
    #         headers=self.headers
    #     )

    def parse_info(self, response):
        item = InfoItem()
        data = json.loads(response.text)
        for record in data['records']:
            if record['accessType']['type'] != "ephemera":
                if 'abstract' in record:
                    item['abstract'] = record['abstract']
                item['title'] = record['articleTitle']
                if 'authors' in record:
                    item['author'] = record['authors'][0]['preferredName']
                item['journal'] = 'ieee'
                if 'doi' in record:
                    item['doi'] = record['doi']
                item['pdf_url'] = self.base_url+record['pdfLink']
                item['year'] = record['publicationYear']
                item['track'] = record['publicationTitle']
                # print(item)
                yield item
        if response.meta['current'] < data['totalPages']:
            yield scrapy.http.JsonRequest(
                url=self.base_url +
                f"/rest/search/pub/{response.meta['punumber']}/issue/{response.meta['isnumber']}/toc",
                callback=self.parse_info,
                method="POST",
                data={
                    "isnumber": f"{response.meta['isnumber']}",
                    "punumber": f"{response.meta['punumber']}",
                    "sortType": "vol-only-seq",
                    "rowsPerPage": "100",
                    "pageNumber": response.meta['current']+1
                },
                meta={
                    "isnumber": response.meta['isnumber'],
                    "punumber": response.meta['punumber'],
                    'current': response.meta['current']+1
                },
                headers=self.headers
            )
