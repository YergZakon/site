from django.shortcuts import render, get_object_or_404, redirect
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
