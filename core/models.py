from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """Настройки сайта (синглтон)"""

    # Название организации
    org_name = models.CharField(_('Название организации'), max_length=300)
    org_name_kk = models.CharField(_('Название (каз.)'), max_length=300, blank=True)

    # Контакты
    address = models.TextField(_('Адрес'))
    address_kk = models.TextField(_('Адрес (каз.)'), blank=True)
    phone = models.CharField(_('Телефон'), max_length=50)
    email = models.EmailField(_('Email'))

    # Реквизиты
    bin_iin = models.CharField(_('БИН/ИИН'), max_length=12)
    bank_details = models.TextField(_('Банковские реквизиты'), blank=True)

    # Документы
    accreditation_cert = models.FileField(
        _('Свидетельство об аккредитации'),
        upload_to='org/',
        blank=True
    )
    charter = models.FileField(
        _('Устав'),
        upload_to='org/',
        blank=True
    )

    # Логотип
    logo = models.ImageField(_('Логотип'), upload_to='org/', blank=True)

    # Соцсети
    facebook = models.URLField(_('Facebook'), blank=True)
    instagram = models.URLField(_('Instagram'), blank=True)

    class Meta:
        verbose_name = _('Настройки сайта')
        verbose_name_plural = _('Настройки сайта')

    def save(self, *args, **kwargs):
        # Гарантируем синглтон
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1, defaults={
            'org_name': 'Организация',
            'address': 'Адрес',
            'phone': '+7 (777) 777-77-77',
            'email': 'info@example.com',
            'bin_iin': '000000000000',
        })
        return obj


class Page(models.Model):
    """Статические страницы"""

    SLUG_CHOICES = [
        ('about', _('О компании')),
        ('services', _('Услуги')),
        ('mission', _('Миссия и ценности')),
        ('ethics', _('Этический кодекс')),
        ('confidentiality', _('Политика конфиденциальности')),
    ]

    title = models.CharField(_('Заголовок'), max_length=200)
    title_kk = models.CharField(_('Заголовок (каз.)'), max_length=200, blank=True)

    slug = models.SlugField(_('URL'), unique=True)

    content = models.TextField(_('Содержимое'))
    content_kk = models.TextField(_('Содержимое (каз.)'), blank=True)

    is_published = models.BooleanField(_('Опубликовано'), default=True)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Страница')
        verbose_name_plural = _('Страницы')
        ordering = ['order']

    def __str__(self):
        return self.title


class NewsItem(models.Model):
    """Новости"""

    title = models.CharField(_('Заголовок'), max_length=300)
    title_kk = models.CharField(_('Заголовок (каз.)'), max_length=300, blank=True)

    slug = models.SlugField(unique=True)

    excerpt = models.TextField(_('Краткое описание'), max_length=500)
    excerpt_kk = models.TextField(_('Краткое описание (каз.)'), max_length=500, blank=True)

    content = models.TextField(_('Содержимое'))
    content_kk = models.TextField(_('Содержимое (каз.)'), blank=True)

    image = models.ImageField(_('Изображение'), upload_to='news/', blank=True)

    is_published = models.BooleanField(_('Опубликовано'), default=True)
    published_at = models.DateTimeField(_('Дата публикации'))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Новость')
        verbose_name_plural = _('Новости')
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """Сообщения с формы обратной связи"""

    name = models.CharField(_('Имя'), max_length=100)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Телефон'), max_length=20, blank=True)
    subject = models.CharField(_('Тема'), max_length=200)
    message = models.TextField(_('Сообщение'))

    is_read = models.BooleanField(_('Прочитано'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Сообщение')
        verbose_name_plural = _('Сообщения')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
