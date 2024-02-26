from paperspider.spiders.aaai_pdf import AaaiPdfSpider
from paperspider.spiders.ijcai_pdf import IjcaiPdfSpider
from paperspider.spiders.neurips_pdf import NeuripsPdfSpider
from paperspider.spiders.icml_pdf import IcmlPdfSpider
from paperspider.spiders.kdd_pdf import KddPdfSpider
from paperspider.spiders.ieee_pdf import IeeePdfSpider
import os
import sys
from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
sys.path.append(os.path.join(settings.BASE_DIR.parent, "paperspider"))


def crawl(process: CrawlerProcess):
    process.crawl(IeeePdfSpider)
    # process.crawl(IcmlPdfSpider)
    # process.crawl(KddPdfSpider)
    # process.crawl(NeuripsPdfSpider)
    # process.crawl(IjcaiPdfSpider)
    # process.crawl(AaaiPdfSpider)


class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        # Set scrapy configuration file
        os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "paperspider.settings")
        scrapy_settings = get_project_settings()
        process = CrawlerProcess(settings=scrapy_settings)
        crawl(process)
        process.start()
        message = f"{timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')} crawled successfully."
        self.stdout.write(self.style.SUCCESS(message))
