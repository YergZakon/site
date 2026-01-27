from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Expert, ExpertProfile, ExpertCertificate


class ExpertCertificateInline(admin.TabularInline):
    """Inline для сертификатов в карточке эксперта"""
    model = ExpertCertificate
    extra = 1
    fields = ['cert_type', 'title', 'issuer', 'issue_date', 'hours', 'document']


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'profile_type', 'expert_count']
    prepopulated_fields = {'slug': ('name',)}

    def expert_count(self, obj):
        return obj.experts.filter(is_active=True).count()
    expert_count.short_description = _('Кол-во экспертов')


@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    list_display = [
        'photo_preview', 'full_name', 'profile',
        'experience_years', 'expertise_count', 'is_active'
    ]
    list_display_links = ['full_name']
    list_filter = ['profile', 'is_active', 'registry_date']
    search_fields = ['last_name', 'first_name', 'iin', 'registry_number']
    list_editable = ['is_active']

    inlines = [ExpertCertificateInline]

    fieldsets = (
        (_('Основная информация'), {
            'fields': (
                ('last_name', 'first_name', 'middle_name'),
                ('last_name_kk', 'first_name_kk', 'middle_name_kk'),
                'iin', 'photo'
            )
        }),
        (_('Контакты'), {
            'fields': (('email', 'phone'),),
            'classes': ('collapse',)
        }),
        (_('Профессиональные данные'), {
            'fields': (
                'profile',
                ('specialization', 'specialization_kk'),
                ('education', 'education_kk'),
                ('workplace', 'workplace_kk'),
                'workplace_address',
                'experience_years'
            )
        }),
        (_('Реестр'), {
            'fields': (
                ('registry_number', 'registry_date'),
                'expertise_count'
            )
        }),
        (_('Статус'), {
            'fields': ('is_active',)
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return "—"
    photo_preview.short_description = _('Фото')


@admin.register(ExpertCertificate)
class ExpertCertificateAdmin(admin.ModelAdmin):
    list_display = ['expert', 'cert_type', 'title', 'issue_date', 'hours']
    list_filter = ['cert_type', 'issue_date']
    search_fields = ['expert__last_name', 'title']
    autocomplete_fields = ['expert']
