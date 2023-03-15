from django.contrib.gis.db import models

from test_backend.base.models import TestBaseModel



class File(TestBaseModel):
    name = models.CharField(verbose_name="File name", max_length=255, blank=False, unique=True)

    mime_type = models.CharField(
        verbose_name="MIME Type of file", max_length=255, blank=False
    )

    file_metadata = models.JSONField(verbose_name="Metadata of the file", blank=True, null=True)

    file = models.FileField(upload_to='file_uploads/')

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "Files"

        verbose_name = "File"

        verbose_name_plural = "Files"
