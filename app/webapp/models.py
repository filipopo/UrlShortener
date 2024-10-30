from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

class ShortUrl(models.Model):
    path = models.CharField(max_length=255, unique=True)
    url = models.URLField(max_length=255)
    note = models.CharField(max_length=255, blank=True, default='')
    viewed = models.PositiveIntegerField(default=0)
    created_date = models.DateField(default=datetime.now)

    class Meta:
        get_latest_by = 'id'

    def __str__(self):
        return f'{self.path} -> {self.url}'

class UserUrl(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.ForeignKey(ShortUrl, on_delete=models.CASCADE)
    favorite = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'url'], name='user_url')
        ]

    def __str__(self):
        return f'{self.user} -> {self.url.path}'
