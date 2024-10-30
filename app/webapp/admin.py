from .models import ShortUrl, UserUrl
from django.contrib import admin


class ShortUrlAdmin(admin.ModelAdmin):
    list_display = ('id', 'headline', 'viewed', 'created_date')
    list_display_links = ('headline',)

    def headline(self, obj):
        return obj


admin.site.register(ShortUrl, ShortUrlAdmin)
admin.site.register(UserUrl)
