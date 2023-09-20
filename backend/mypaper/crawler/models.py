from django.db import models

# Create your models here.


class Info(models.Model):
    author = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="作者",
    )
    institution = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="机构",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="标题",
    )
    year = models.SmallIntegerField(
        blank=True,
        verbose_name="年份"
    )
    journal = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="期刊",
    )
    doi = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="doi",
    )
    abstract = models.TextField(
        blank=True,
        verbose_name="摘要",
    )
    track = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="track",
    )
    pdf_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="pdf下载地址",
    )
    file_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="pdf本地地址",
    )

    class Meta:
        indexes = models.Index(
            fields=["doi", "journal"],
            name="idx_paper"
        ),
        verbose_name = "论文信息"
