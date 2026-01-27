from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'pub_type', 'year', 'authors_text']
    list_filter = ['pub_type', 'year']
    search_fields = ['title', 'authors_text']
    filter_horizontal = ['authors']

    fieldsets = (
        (_('Основная информация'), {
            'fields': (
                ('title', 'title_kk'),
                'pub_type',
                'authors',
                'authors_text',
            )
        }),
        (_('Издание'), {
            'fields': (
                'year',
                ('journal', 'volume', 'pages'),
            )
        }),
        (_('Ссылки'), {
            'fields': (('doi', 'url'), 'file'),
            'classes': ('collapse',)
        }),
        (_('Аннотация'), {
            'fields': (('abstract', 'abstract_kk'),),
            'classes': ('collapse',)
        }),
    )
