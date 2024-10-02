from datetime import datetime
from django.db import models


class ShortUrl(models.Model):
    short = models.CharField(max_length=255, unique=True)
    url = models.URLField(max_length=255)
    note = models.CharField(max_length=255, blank=True, default='')
    viewed = models.PositiveIntegerField(default=0)
    created_date = models.DateField(default=datetime.now)

    class Meta:
        get_latest_by = 'id'

    def __str__(self):
        return f'{self.short} -> {self.url}'
