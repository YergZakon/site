from django.db import models
from django.utils.translation import gettext_lazy as _


class DocumentCategory(models.Model):
    """Категория документов"""

    name = models.CharField(_('Название'), max_length=100)
    name_kk = models.CharField(_('Название (каз.)'), max_length=100, blank=True)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Категория документов')
        verbose_name_plural = _('Категории документов')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Document(models.Model):
    """Документ организации"""

    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        verbose_name=_('Категория'),
        related_name='documents'
    )

    title = models.CharField(_('Название'), max_length=300)
    title_kk = models.CharField(_('Название (каз.)'), max_length=300, blank=True)

    description = models.TextField(_('Описание'), blank=True)
    description_kk = models.TextField(_('Описание (каз.)'), blank=True)

    file = models.FileField(_('Файл'), upload_to='documents/')

    is_public = models.BooleanField(_('Публичный'), default=True)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Документ')
        verbose_name_plural = _('Документы')
        ordering = ['category', 'order', 'title']

    def __str__(self):
        return self.title
