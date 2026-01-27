from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings, Page, NewsItem, ContactMessage


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Организация'), {
            'fields': (
                ('org_name', 'org_name_kk'),
                'bin_iin',
            )
        }),
        (_('Контакты'), {
            'fields': (
                ('address', 'address_kk'),
                ('phone', 'email'),
            )
        }),
        (_('Документы'), {
            'fields': ('accreditation_cert', 'charter', 'logo')
        }),
        (_('Соцсети'), {
            'fields': (('facebook', 'instagram'),),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Только одна запись
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_published', 'order']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'order']

    fieldsets = (
        (None, {
            'fields': (
                ('title', 'title_kk'),
                'slug',
                ('content', 'content_kk'),
                ('is_published', 'order'),
            )
        }),
    )


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at', 'is_published']
    list_filter = ['is_published', 'published_at']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    list_editable = ['is_read']

    def has_add_permission(self, request):
        return False
