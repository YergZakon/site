ПОЛНЫЙ ПЛАН: Django + Railway за 1 день

📋 ОБЗОР ПЛАНА
ЭтапВремяОписание1. Подготовка30 минОкружение, Git, структура2. Модели данных1.5 часаЭксперты, документы, публикации3. Админ-панель1 часКастомизация, фильтры, поиск4. Фронтенд3 часаШаблоны, дизайн, страницы5. Двуязычность1 часKZ/RU переключатель6. Деплой Railway30 минПубликация в интернет7. Контент30 минНаполнение через админкуБуфер1 часНа непредвиденноеИТОГО9 часов

ЭТАП 1: ПОДГОТОВКА (30 минут)
1.1 Требования на компьютере
bash# Проверьте что установлено:
python --version    # Нужен Python 3.10+
git --version       # Нужен Git
pip --version       # Менеджер пакетов
1.2 Создание проекта
bash# Создаём папку проекта
mkdir healthcare_expertise
cd healthcare_expertise

# Виртуальное окружение
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Mac/Linux)
source venv/bin/activate

# Установка Django и зависимостей
pip install django==4.2
pip install pillow           # Для изображений
pip install django-crispy-forms
pip install crispy-bootstrap5
pip install python-dotenv    # Для переменных окружения
pip install gunicorn         # Для продакшена
pip install whitenoise       # Статика на продакшене
pip install psycopg2-binary  # PostgreSQL для Railway
pip install dj-database-url  # URL базы данных
1.3 Инициализация Django
bash# Создание проекта
django-admin startproject config .

# Создание приложений
python manage.py startapp core        # Главная, контакты, о компании
python manage.py startapp experts     # Эксперты
python manage.py startapp documents   # Документы организации
python manage.py startapp publications # Публикации
```

### 1.4 Структура проекта (создать папки)
```
healthcare_expertise/
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── core/
├── experts/
├── documents/
├── publications/
│
├── templates/              # ← СОЗДАТЬ
│   ├── base.html
│   ├── home.html
│   └── includes/
│       ├── header.html
│       └── footer.html
│
├── static/                 # ← СОЗДАТЬ
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── logo.png
│
├── media/                  # ← СОЗДАТЬ
│   ├── experts/
│   ├── certificates/
│   └── publications/
│
├── locale/                 # ← СОЗДАТЬ (для переводов)
│   ├── kk/
│   └── ru/
│
├── manage.py
├── requirements.txt
├── .gitignore
├── .env
├── Procfile               # Для Railway
└── railway.json
1.5 Файл requirements.txt
txtDjango==4.2
gunicorn==21.2.0
whitenoise==6.6.0
psycopg2-binary==2.9.9
dj-database-url==2.1.0
python-dotenv==1.0.0
Pillow==10.1.0
django-crispy-forms==2.1
crispy-bootstrap5==2023.10
1.6 Файл .gitignore
gitignorevenv/
__pycache__/
*.pyc
.env
db.sqlite3
media/
*.log
.DS_Store
staticfiles/
1.7 Файл .env (локальный)
envDEBUG=True
SECRET_KEY=your-super-secret-key-change-me-in-production
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
1.8 Git инициализация
bashgit init
git add .
git commit -m "Initial commit: Django project setup"
✅ Чек-лист этапа 1:

 Python и Git установлены
 Виртуальное окружение создано
 Django установлен
 Приложения созданы
 Папки templates, static, media созданы
 requirements.txt готов
 Git репозиторий инициализирован


ЭТАП 2: МОДЕЛИ ДАННЫХ (1.5 часа)
2.1 Настройки config/settings.py
pythonimport os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Local apps
    'core',
    'experts',
    'documents',
    'publications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Статика
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',   # Локализация
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # Локализация
                'core.context_processors.site_settings',    # Свой контекст
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('ru', 'Русский'),
    ('kk', 'Қазақша'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
2.2 Модель эксперта: experts/models.py
pythonfrom django.db import models
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
2.3 Модель публикаций: publications/models.py
pythonfrom django.db import models
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
2.4 Модель документов организации: documents/models.py
pythonfrom django.db import models
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
2.5 Модели страниц и настроек: core/models.py
pythonfrom django.db import models
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
        obj, created = cls.objects.get_or_create(pk=1)
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
2.6 Миграции
bashpython manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
✅ Чек-лист этапа 2:

 settings.py настроен
 Модель Expert создана
 Модель ExpertCertificate создана
 Модель Publication создана
 Модель Document создана
 Модели core (SiteSettings, Page, News) созданы
 Миграции выполнены
 Суперпользователь создан


ЭТАП 3: АДМИН-ПАНЕЛЬ (1 час)
3.1 Админка экспертов: experts/admin.py
pythonfrom django.contrib import admin
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
3.2 Админка публикаций: publications/admin.py
pythonfrom django.contrib import admin
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
3.3 Админка документов: documents/admin.py
pythonfrom django.contrib import admin
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
3.4 Админка core: core/admin.py
pythonfrom django.contrib import admin
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
3.5 Кастомизация админки: config/admin.py (создать файл)
pythonfrom django.contrib import admin

admin.site.site_header = "Независимая экспертиза | Админ-панель"
admin.site.site_title = "Админ-панель"
admin.site.index_title = "Управление сайтом"
И добавить в config/urls.py:
pythonfrom django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Кастомизация админки
admin.site.site_header = "🏥 Независимая экспертиза"
admin.site.site_title = "Админ-панель"
admin.site.index_title = "Управление сайтом"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
✅ Чек-лист этапа 3:

 Админка экспертов с inline сертификатами
 Админка публикаций с фильтрами
 Админка документов
 Админка настроек сайта
 Кастомизация заголовков админки
 Проверка: зайти в админку и добавить тестового эксперта


ЭТАП 4: ФРОНТЕНД (3 часа)
4.1 Context processor: core/context_processors.py
pythonfrom .models import SiteSettings

def site_settings(request):
    """Добавляет настройки сайта во все шаблоны"""
    return {
        'site_settings': SiteSettings.get_settings(),
        'current_language': request.LANGUAGE_CODE,
    }
4.2 URLs: core/urls.py
pythonfrom django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('experts/', views.expert_list, name='experts'),
    path('experts/<int:pk>/', views.expert_detail, name='expert_detail'),
    path('documents/', views.document_list, name='documents'),
    path('publications/', views.publication_list, name='publications'),
    path('news/', views.news_list, name='news'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('contacts/', views.contacts, name='contacts'),
    path('page/<slug:slug>/', views.page_detail, name='page'),
    path('set-language/<str:lang>/', views.set_language, name='set_language'),
]
4.3 Views: core/views.py
pythonfrom django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import activate, gettext as _
from django.core.paginator import Paginator

from .models import SiteSettings, Page, NewsItem, ContactMessage
from experts.models import Expert, ExpertProfile
from documents.models import Document, DocumentCategory
from publications.models import Publication


def home(request):
    """Главная страница"""
    context = {
        'expert_count': Expert.objects.filter(is_active=True).count(),
        'publication_count': Publication.objects.count(),
        'profiles': ExpertProfile.objects.all(),
        'recent_news': NewsItem.objects.filter(is_published=True)[:3],
    }
    return render(request, 'home.html', context)


def about(request):
    """О компании"""
    page = Page.objects.filter(slug='about').first()
    return render(request, 'about.html', {'page': page})


def services(request):
    """Услуги"""
    page = Page.objects.filter(slug='services').first()
    return render(request, 'services.html', {'page': page})


def expert_list(request):
    """Список экспертов"""
    experts = Expert.objects.filter(is_active=True).select_related('profile')
    profiles = ExpertProfile.objects.all()
    
    # Фильтрация по профилю
    profile_slug = request.GET.get('profile')
    if profile_slug:
        experts = experts.filter(profile__slug=profile_slug)
    
    # Пагинация
    paginator = Paginator(experts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'profiles': profiles,
        'current_profile': profile_slug,
    }
    return render(request, 'experts/expert_list.html', context)


def expert_detail(request, pk):
    """Карточка эксперта"""
    expert = get_object_or_404(
        Expert.objects.prefetch_related('certificates', 'publications'),
        pk=pk, is_active=True
    )
    return render(request, 'experts/expert_detail.html', {'expert': expert})


def document_list(request):
    """Документы организации"""
    categories = DocumentCategory.objects.prefetch_related('documents').all()
    return render(request, 'documents.html', {'categories': categories})


def publication_list(request):
    """Публикации"""
    publications = Publication.objects.prefetch_related('authors').all()
    
    # Фильтрация по году
    year = request.GET.get('year')
    if year:
        publications = publications.filter(year=year)
    
    # Фильтрация по типу
    pub_type = request.GET.get('type')
    if pub_type:
        publications = publications.filter(pub_type=pub_type)
    
    # Пагинация
    paginator = Paginator(publications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Список годов для фильтра
    years = Publication.objects.values_list('year', flat=True).distinct().order_by('-year')
    
    context = {
        'page_obj': page_obj,
        'years': years,
        'current_year': year,
        'current_type': pub_type,
    }
    return render(request, 'publications.html', context)


def news_list(request):
    """Список новостей"""
    news = NewsItem.objects.filter(is_published=True)
    paginator = Paginator(news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/news_list.html', {'page_obj': page_obj})


def news_detail(request, slug):
    """Детальная новость"""
    news = get_object_or_404(NewsItem, slug=slug, is_published=True)
    return render(request, 'news/news_detail.html', {'news': news})


def contacts(request):
    """Контакты и форма обратной связи"""
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        messages.success(request, _('Ваше сообщение отправлено!'))
        return redirect('core:contacts')
    
    return render(request, 'contacts.html')


def page_detail(request, slug):
    """Статическая страница"""
    page = get_object_or_404(Page, slug=slug, is_published=True)
    return render(request, 'page.html', {'page': page})


def set_language(request, lang):
    """Переключение языка"""
    activate(lang)
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie('django_language', lang)
    return response
4.4 Базовый шаблон: templates/base.html
html{% load static i18n %}
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ site_settings.org_name }}{% endblock %}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link href="{% static 'css/style.css' %}" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Header -->
    <header>
        {% include 'includes/header.html' %}
    </header>
    
    <!-- Messages -->
    {% if messages %}
    <div class="container mt-3">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    <footer class="bg-dark text-white mt-5 py-4">
        {% include 'includes/footer.html' %}
    </footer>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="{% static 'js/main.js' %}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
4.5 Header: templates/includes/header.html
html{% load i18n %}
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand d-flex align-items-center" href="{% url 'core:home' %}">
            {% if site_settings.logo %}
            <img src="{{ site_settings.logo.url }}" alt="Logo" height="40" class="me-2">
            {% endif %}
            <span class="d-none d-md-inline">
                {% if current_language == 'kk' and site_settings.org_name_kk %}
                    {{ site_settings.org_name_kk }}
                {% else %}
                    {{ site_settings.org_name }}
                {% endif %}
            </span>
        </a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'core:home' %}">{% trans "Главная" %}</a>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                        {% trans "О компании" %}
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="{% url 'core:about' %}">{% trans "О нас" %}</a></li>
                        <li><a class="dropdown-item" href="{% url 'core:page' slug='mission' %}">{% trans "Миссия" %}</a></li>
                        <li><a class="dropdown-item" href="{% url 'core:documents' %}">{% trans "Документы" %}</a></li>
                    </ul>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'core:services' %}">{% trans "Услуги" %}</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'core:experts' %}">{% trans "Эксперты" %}</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'core:publications' %}">{% trans "Публикации" %}</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'core:news' %}">{% trans "Новости" %}</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'core:contacts' %}">{% trans "Контакты" %}</a>
                </li>
            </ul>
            
            <!-- Language Switcher -->
            <div class="nav-item dropdown">
                <a class="nav-link dropdown-toggle text-white" href="#" data-bs-toggle="dropdown">
                    <i class="bi bi-globe"></i>
                    {% if current_language == 'kk' %}ҚАЗ{% else %}РУС{% endif %}
                </a>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item" href="{% url 'core:set_language' lang='kk' %}">Қазақша</a></li>
                    <li><a class="dropdown-item" href="{% url 'core:set_language' lang='ru' %}">Русский</a></li>
                </ul>
            </div>
        </div>
    </div>
</nav>
4.6 Footer: templates/includes/footer.html
html{% load i18n %}
<div class="container">
    <div class="row">
        <div class="col-md-4 mb-3">
            <h5>{% trans "Контакты" %}</h5>
            <p><i class="bi bi-geo-alt"></i> 
                {% if current_language == 'kk' and site_settings.address_kk %}
                    {{ site_settings.address_kk }}
                {% else %}
                    {{ site_settings.address }}
                {% endif %}
            </p>
            <p><i class="bi bi-telephone"></i> {{ site_settings.phone }}</p>
            <p><i class="bi bi-envelope"></i> {{ site_settings.email }}</p>
        </div>
        <div class="col-md-4 mb-3">
            <h5>{% trans "Навигация" %}</h5>
            <ul class="list-unstyled">
                <li><a href="{% url 'core:about' %}" class="text-white-50">{% trans "О компании" %}</a></li>
                <li><a href="{% url 'core:experts' %}" class="text-white-50">{% trans "Эксперты" %}</a></li>
                <li><a href="{% url 'core:documents' %}" class="text-white-50">{% trans "Документы" %}</a></li>
                <li><a href="{% url 'core:contacts' %}" class="text-white-50">{% trans "Контакты" %}</a></li>
            </ul>
        </div>
        <div class="col-md-4 mb-3">
            <h5>{% trans "Документы" %}</h5>
            {% if site_settings.accreditation_cert %}
            <p><a href="{{ site_settings.accreditation_cert.url }}" class="text-white-50" target="_blank">
                <i class="bi bi-file-pdf"></i> {% trans "Свидетельство об аккредитации" %}
            </a></p>
            {% endif %}
            {% if site_settings.charter %}
            <p><a href="{{ site_settings.charter.url }}" class="text-white-50" target="_blank">
                <i class="bi bi-file-pdf"></i> {% trans "Устав" %}
            </a></p>
            {% endif %}
        </div>
    </div>
    <hr class="border-white-50">
    <div class="text-center">
        <p class="mb-0">© {{ site_settings.org_name }} {% now "Y" %}</p>
    </div>
</div>
4.7 Главная страница: templates/home.html
html{% extends 'base.html' %}
{% load i18n %}

{% block content %}
<!-- Hero Section -->
<section class="bg-primary text-white py-5">
    <div class="container">
        <div class="row align-items-center">
            <div class="col-lg-8">
                <h1 class="display-4 fw-bold">
                    {% if current_language == 'kk' and site_settings.org_name_kk %}
                        {{ site_settings.org_name_kk }}
                    {% else %}
                        {{ site_settings.org_name }}
                    {% endif %}
                </h1>
                <p class="lead">{% trans "Независимая экспертиза качества медицинских услуг" %}</p>
                <a href="{% url 'core:contacts' %}" class="btn btn-light btn-lg">
                    {% trans "Заказать экспертизу" %}
                </a>
            </div>
        </div>
    </div>
</section>

<!-- Stats Section -->
<section class="py-5 bg-light">
    <div class="container">
        <div class="row text-center">
            <div class="col-md-4 mb-4">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body">
                        <i class="bi bi-people display-4 text-primary"></i>
                        <h2 class="display-5 fw-bold">{{ expert_count }}+</h2>
                        <p class="text-muted">{% trans "Экспертов в реестре" %}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body">
                        <i class="bi bi-journal-text display-4 text-primary"></i>
                        <h2 class="display-5 fw-bold">{{ publication_count }}+</h2>
                        <p class="text-muted">{% trans "Публикаций" %}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body">
                        <i class="bi bi-award display-4 text-primary"></i>
                        <h2 class="display-5 fw-bold">5</h2>
                        <p class="text-muted">{% trans "Лет аккредитации" %}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Profiles Section -->
<section class="py-5">
    <div class="container">
        <h2 class="text-center mb-4">{% trans "Профили экспертов" %}</h2>
        <div class="row">
            {% for profile in profiles %}
            <div class="col-md-3 mb-4">
                <a href="{% url 'core:experts' %}?profile={{ profile.slug }}" class="text-decoration-none">
                    <div class="card h-100 border-0 shadow-sm text-center">
                        <div class="card-body">
                            <i class="bi bi-heart-pulse display-4 text-primary"></i>
                            <h5 class="mt-3">
                                {% if current_language == 'kk' and profile.name_kk %}
                                    {{ profile.name_kk }}
                                {% else %}
                                    {{ profile.name }}
                                {% endif %}
                            </h5>
                            <p class="text-muted">{{ profile.experts.count }} {% trans "экспертов" %}</p>
                        </div>
                    </div>
                </a>
            </div>
            {% endfor %}
        </div>
    </div>
</section>

<!-- News Section -->
{% if recent_news %}
<section class="py-5 bg-light">
    <div class="container">
        <h2 class="text-center mb-4">{% trans "Последние новости" %}</h2>
        <div class="row">
            {% for news in recent_news %}
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    {% if news.image %}
                    <img src="{{ news.image.url }}" class="card-img-top" alt="{{ news.title }}">
                    {% endif %}
                    <div class="card-body">
                        <small class="text-muted">{{ news.published_at|date:"d.m.Y" }}</small>
                        <h5 class="card-title">
                            {% if current_language == 'kk' and news.title_kk %}
                                {{ news.title_kk }}
                            {% else %}
                                {{ news.title }}
                            {% endif %}
                        </h5>
                        <a href="{% url 'core:news_detail' news.slug %}" class="btn btn-outline-primary btn-sm">
                            {% trans "Подробнее" %}
                        </a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        <div class="text-center mt-3">
            <a href="{% url 'core:news' %}" class="btn btn-primary">{% trans "Все новости" %}</a>
        </div>
    </div>
</section>
{% endif %}
{% endblock %}
4.8 Список экспертов: templates/experts/expert_list.html
html{% extends 'base.html' %}
{% load i18n %}

{% block title %}{% trans "Эксперты" %} | {{ block.super }}{% endblock %}

{% block content %}
<div class="container py-5">
    <h1 class="mb-4">{% trans "Реестр независимых экспертов" %}</h1>
    
    <!-- Filters -->
    <div class="card mb-4">
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <label class="form-label">{% trans "Фильтр по профилю:" %}</label>
                    <select class="form-select" onchange="window.location.href=this.value">
                        <option value="{% url 'core:experts' %}">{% trans "Все профили" %}</option>
                        {% for profile in profiles %}
                        <option value="{% url 'core:experts' %}?profile={{ profile.slug }}" 
                                {% if current_profile == profile.slug %}selected{% endif %}>
                            {{ profile.name }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Expert Grid -->
    <div class="row">
        {% for expert in page_obj %}
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    {% if expert.photo %}
                    <img src="{{ expert.photo.url }}" class="rounded-circle mb-3" 
                         width="120" height="120" style="object-fit: cover;">
                    {% else %}
                    <div class="rounded-circle bg-secondary d-inline-flex align-items-center justify-content-center mb-3"
                         style="width: 120px; height: 120px;">
                        <i class="bi bi-person-fill text-white display-4"></i>
                    </div>
                    {% endif %}
                    
                    <h5 class="card-title">
                        {% if current_language == 'kk' %}
                            {{ expert.full_name_kk }}
                        {% else %}
                            {{ expert.full_name }}
                        {% endif %}
                    </h5>
                    <p class="text-muted mb-1">{{ expert.profile.name }}</p>
                    <p class="small mb-2">
                        {% trans "Стаж:" %} {{ expert.experience_years }} {% trans "лет" %}
                    </p>
                    <a href="{% url 'core:expert_detail' expert.pk %}" class="btn btn-outline-primary btn-sm">
                        {% trans "Подробнее" %}
                    </a>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-12">
            <div class="alert alert-info">{% trans "Эксперты не найдены" %}</div>
        </div>
        {% endfor %}
    </div>
    
    <!-- Pagination -->
    {% if page_obj.has_other_pages %}
    <nav class="mt-4">
        <ul class="pagination justify-content-center">
            {% if page_obj.has_previous %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.previous_page_number }}{% if current_profile %}&profile={{ current_profile }}{% endif %}">
                    {% trans "Назад" %}
                </a>
            </li>
            {% endif %}
            
            {% for num in page_obj.paginator.page_range %}
            <li class="page-item {% if num == page_obj.number %}active{% endif %}">
                <a class="page-link" href="?page={{ num }}{% if current_profile %}&profile={{ current_profile }}{% endif %}">{{ num }}</a>
            </li>
            {% endfor %}
            
            {% if page_obj.has_next %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.next_page_number }}{% if current_profile %}&profile={{ current_profile }}{% endif %}">
                    {% trans "Далее" %}
                </a>
            </li>
            {% endif %}
        </ul>
    </nav>
    {% endif %}
</div>
{% endblock %}
4.9 CSS стили: static/css/style.css
css/* Custom styles */
:root {
    --primary-color: #0d6efd;
    --secondary-color: #6c757d;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header */
.navbar-brand {
    font-weight: 600;
}

/* Hero */
.hero-section {
    background: linear-gradient(135deg, var(--primary-color), #0056b3);
}

/* Cards */
.card {
    transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

/* Expert photo */
.expert-photo {
    border: 3px solid var(--primary-color);
}

/* Footer */
footer a {
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
    .display-4 {
        font-size: 2rem;
    }
}
✅ Чек-лист этапа 4:

 base.html создан
 header.html и footer.html созданы
 home.html готов
 expert_list.html готов
 URLs настроены
 Views написаны
 CSS стили добавлены
 Проверка: запустить python manage.py runserver и проверить страницы


ЭТАП 5: ДВУЯЗЫЧНОСТЬ (1 час)
5.1 Создание файлов переводов
bash# Создание папок локалей
mkdir -p locale/kk/LC_MESSAGES
mkdir -p locale/ru/LC_MESSAGES

# Сбор строк для перевода
python manage.py makemessages -l kk
python manage.py makemessages -l ru
5.2 Редактирование locale/kk/LC_MESSAGES/django.po
po# Казахский перевод
msgid "Главная"
msgstr "Басты бет"

msgid "О компании"
msgstr "Компания туралы"

msgid "Услуги"
msgstr "Қызметтер"

msgid "Эксперты"
msgstr "Сарапшылар"

msgid "Публикации"
msgstr "Жарияланымдар"

msgid "Новости"
msgstr "Жаңалықтар"

msgid "Контакты"
msgstr "Байланыс"

msgid "Документы"
msgstr "Құжаттар"

msgid "Независимая экспертиза качества медицинских услуг"
msgstr "Медициналық қызметтердің сапасына тәуелсіз сараптама"

msgid "Заказать экспертизу"
msgstr "Сараптамаға тапсырыс беру"

msgid "Экспертов в реестре"
msgstr "Тізілімдегі сарапшылар"

msgid "лет"
msgstr "жыл"

msgid "Стаж:"
msgstr "Тәжірибесі:"

msgid "Подробнее"
msgstr "Толығырақ"
5.3 Компиляция переводов
bashpython manage.py compilemessages
```

### ✅ Чек-лист этапа 5:
- [ ] Папки locale созданы
- [ ] makemessages выполнен
- [ ] Переводы заполнены (хотя бы основные)
- [ ] compilemessages выполнен
- [ ] Проверка: переключить язык на сайте

---

## ЭТАП 6: ДЕПЛОЙ НА RAILWAY (30 минут)

### 6.1 Подготовка файлов

**Procfile** (в корне проекта):
```
web: gunicorn config.wsgi --log-file -
railway.json:
json{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
6.2 Обновление settings.py для продакшена
python# В конец settings.py добавить:

# Production settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
```

### 6.3 Пошаговый деплой на Railway

1. **Создать аккаунт**: https://railway.app (войти через GitHub)

2. **Создать новый проект**:
   - Dashboard → New Project → Deploy from GitHub repo
   - Выбрать ваш репозиторий

3. **Добавить PostgreSQL**:
   - В проекте → Add Service → Database → PostgreSQL
   - Подождать создания

4. **Настроить переменные окружения**:
```
   DATABASE_URL      → (Railway подставит автоматически из PostgreSQL)
   SECRET_KEY        → (сгенерировать: python -c "import secrets; print(secrets.token_urlsafe(50))")
   DEBUG             → False
   ALLOWED_HOSTS     → your-app.up.railway.app

Деплой:

Railway автоматически начнёт сборку
Следить в логах


Создать суперпользователя:

Railway → ваш сервис → Settings → Railway Shell
python manage.py createsuperuser


Получить домен:

Settings → Domains → Generate Domain



6.4 Альтернатива: быстрый деплой через CLI
bash# Установка Railway CLI
npm install -g @railway/cli

# Логин
railway login

# Инициализация в папке проекта
railway init

# Добавление PostgreSQL
railway add --database postgresql

# Деплой
railway up

# Открыть в браузере
railway open
✅ Чек-лист этапа 6:

 Procfile создан
 railway.json создан
 Код запушен в GitHub
 Проект создан на Railway
 PostgreSQL добавлен
 Переменные окружения настроены
 Деплой успешен
 Суперпользователь создан
 Сайт открывается по URL


ЭТАП 7: НАПОЛНЕНИЕ КОНТЕНТОМ (30 минут)
7.1 Через админку добавить:

Настройки сайта (SiteSettings):

Название организации (рус/каз)
Адрес, телефон, email
Загрузить логотип
Загрузить свидетельство об аккредитации


Профили экспертов (минимум 4):

Терапевтический
Хирургический
Акушерско-гинекологический
Педиатрический


Эксперты (минимум 20):

По 2 на каждый основной профиль
Остальные — другие профили
Загрузить сертификаты (минимум 108 часов повышения квалификации)


Категории документов:

Учредительные документы
Нормативные акты
Этический кодекс
Политика конфиденциальности


Страницы:

О компании
Услуги
Миссия


Публикации (минимум 30% экспертов должны иметь)