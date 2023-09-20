import os
import sys
from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
sys.path.append(os.path.join(settings.BASE_DIR.parent, "paperspider"))
from paperspider.spiders.aaai import AaaiSpider 

def crawl(process: CrawlerProcess):
    process.crawl(AaaiSpider)

class Command(BaseCommand):
    help=(
        "Crawl Fundermental from mysteel and save extracted information in database."
    )
    def handle(self, *args, **kwargs):
        os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "paperspider.settings")  # Set scrapy configuration file    
        scrapy_settings = get_project_settings()
        process = CrawlerProcess(settings=scrapy_settings)
        crawl(process)
        process.start()
        message = f"{timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')} -aaai crawled successfully."
        self.stdout.write(self.style.SUCCESS(message))
