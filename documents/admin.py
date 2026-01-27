from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Document, DocumentCategory


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'document_count']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']

    def document_count(self, obj):
        return obj.documents.count()
    document_count.short_description = _('Документов')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_public', 'order', 'updated_at']
    list_filter = ['category', 'is_public']
    search_fields = ['title']
    list_editable = ['is_public', 'order']
