import os
import sys
from django.conf import settings


sys.path.append(os.path.join(settings.BASE_DIR.parent, "paperspider"))
os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "paperspider.settings")
