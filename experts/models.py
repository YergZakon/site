from django.db import models
from django.utils.translation import gettext_lazy as _


class ExpertProfile(models.Model):
    """Профиль/специализация эксперта"""

    PROFILE_CHOICES = [
        ('therapeutic', _('Терапевтический')),
        ('surgical', _('Хирургический')),
        ('obstetric', _('Акушерско-гинекологический')),
        ('pediatric', _('Педиатрический')),
        ('other', _('Другой')),
    ]

    name = models.CharField(_('Название профиля'), max_length=100)
    name_kk = models.CharField(_('Название (каз.)'), max_length=100, blank=True)
    slug = models.SlugField(unique=True)
    profile_type = models.CharField(
        _('Тип профиля'),
        max_length=20,
        choices=PROFILE_CHOICES,
        default='other'
    )

    class Meta:
        verbose_name = _('Профиль эксперта')
        verbose_name_plural = _('Профили экспертов')

    def __str__(self):
        return self.name


class Expert(models.Model):
    """Эксперт организации"""

    # Основная информация
    last_name = models.CharField(_('Фамилия'), max_length=100)
    first_name = models.CharField(_('Имя'), max_length=100)
    middle_name = models.CharField(_('Отчество'), max_length=100, blank=True)

    last_name_kk = models.CharField(_('Фамилия (каз.)'), max_length=100, blank=True)
    first_name_kk = models.CharField(_('Имя (каз.)'), max_length=100, blank=True)
    middle_name_kk = models.CharField(_('Отчество (каз.)'), max_length=100, blank=True)

    # ИИН и контакты
    iin = models.CharField(_('ИИН'), max_length=12, unique=True)
    email = models.EmailField(_('Email'), blank=True)
    phone = models.CharField(_('Телефон'), max_length=20, blank=True)

    # Профессиональные данные
    profile = models.ForeignKey(
        ExpertProfile,
        on_delete=models.PROTECT,
        verbose_name=_('Профиль'),
        related_name='experts'
    )
    specialization = models.CharField(_('Специализация'), max_length=200)
    specialization_kk = models.CharField(_('Специализация (каз.)'), max_length=200, blank=True)

    # Образование
    education = models.TextField(_('Образование (ВУЗ, год, специальность)'))
    education_kk = models.TextField(_('Образование (каз.)'), blank=True)

    # Место работы
    workplace = models.CharField(_('Основное место работы'), max_length=300)
    workplace_kk = models.CharField(_('Место работы (каз.)'), max_length=300, blank=True)
    workplace_address = models.CharField(_('Адрес места работы'), max_length=300, blank=True)

    # Стаж
    experience_years = models.PositiveIntegerField(_('Стаж в здравоохранении (лет)'))

    # Дата включения в реестр
    registry_date = models.DateField(_('Дата включения в реестр'))
    registry_number = models.CharField(_('Номер в реестре'), max_length=50, unique=True)

    # Количество экспертиз
    expertise_count = models.PositiveIntegerField(_('Количество проведённых экспертиз'), default=0)

    # Фото
    photo = models.ImageField(
        _('Фото'),
        upload_to='experts/photos/',
        blank=True,
        null=True
    )

    # Статус
    is_active = models.BooleanField(_('Активен'), default=True)

    # Мета
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлён'), auto_now=True)

    class Meta:
        verbose_name = _('Эксперт')
        verbose_name_plural = _('Эксперты')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)

    @property
    def full_name_kk(self):
        parts = [self.last_name_kk or self.last_name,
                 self.first_name_kk or self.first_name]
        if self.middle_name_kk or self.middle_name:
            parts.append(self.middle_name_kk or self.middle_name)
        return ' '.join(parts)


class ExpertCertificate(models.Model):
    """Сертификат/документ эксперта"""

    CERT_TYPE_CHOICES = [
        ('diploma', _('Диплом')),
        ('certificate', _('Сертификат специалиста')),
        ('qualification', _('Повышение квалификации')),
        ('other', _('Другой документ')),
    ]

    expert = models.ForeignKey(
        Expert,
        on_delete=models.CASCADE,
        verbose_name=_('Эксперт'),
        related_name='certificates'
    )
    cert_type = models.CharField(
        _('Тип документа'),
        max_length=20,
        choices=CERT_TYPE_CHOICES
    )
    title = models.CharField(_('Название'), max_length=300)
    title_kk = models.CharField(_('Название (каз.)'), max_length=300, blank=True)

    issuer = models.CharField(_('Кем выдан'), max_length=300)
    issue_date = models.DateField(_('Дата выдачи'))
    expiry_date = models.DateField(_('Срок действия'), blank=True, null=True)
    hours = models.PositiveIntegerField(_('Количество часов'), blank=True, null=True)

    document = models.FileField(
        _('Файл документа'),
        upload_to='experts/certificates/'
    )

    class Meta:
        verbose_name = _('Сертификат эксперта')
        verbose_name_plural = _('Сертификаты экспертов')
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.expert.full_name} - {self.title}"
