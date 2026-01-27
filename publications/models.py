from django.db import models
from django.utils.translation import gettext_lazy as _


class Publication(models.Model):
    """Публикация эксперта"""

    PUB_TYPE_CHOICES = [
        ('article', _('Научная статья')),
        ('book', _('Книга/Монография')),
        ('thesis', _('Диссертация')),
        ('guideline', _('Методические рекомендации')),
        ('patent', _('Патент/Изобретение')),
        ('other', _('Другое')),
    ]

    title = models.CharField(_('Название'), max_length=500)
    title_kk = models.CharField(_('Название (каз.)'), max_length=500, blank=True)

    pub_type = models.CharField(
        _('Тип публикации'),
        max_length=20,
        choices=PUB_TYPE_CHOICES
    )

    # Авторы (связь с экспертами)
    authors = models.ManyToManyField(
        'experts.Expert',
        verbose_name=_('Авторы (эксперты)'),
        related_name='publications',
        blank=True
    )
    authors_text = models.CharField(
        _('Авторы (текст)'),
        max_length=500,
        help_text=_('Укажите всех авторов, включая внешних')
    )

    # Издание
    journal = models.CharField(_('Журнал/Издательство'), max_length=300, blank=True)
    year = models.PositiveIntegerField(_('Год публикации'))
    volume = models.CharField(_('Том/Выпуск'), max_length=50, blank=True)
    pages = models.CharField(_('Страницы'), max_length=50, blank=True)

    # Ссылки
    doi = models.CharField(_('DOI'), max_length=100, blank=True)
    url = models.URLField(_('Ссылка'), blank=True)

    # Файл
    file = models.FileField(
        _('Файл публикации'),
        upload_to='publications/',
        blank=True,
        null=True
    )

    # Описание
    abstract = models.TextField(_('Аннотация'), blank=True)
    abstract_kk = models.TextField(_('Аннотация (каз.)'), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Публикация')
        verbose_name_plural = _('Публикации')
        ordering = ['-year', 'title']

    def __str__(self):
        return f"{self.title} ({self.year})"
