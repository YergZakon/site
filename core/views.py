import json
from typing import Any, Dict, List, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import activate, gettext as _
from django.core.paginator import Paginator

from .models import SiteSettings, Page, NewsItem, ContactMessage
from experts.models import Expert, ExpertProfile
from documents.models import Document, DocumentCategory
from publications.models import Publication

CLARIFICATION_FIELD_PREFIX = "clarify_"
VALID_CLARIFICATION_ANSWERS = {"yes", "no", "unknown"}


def _request_protocol_assistant(
    query: str,
    top_k: int = 3,
    clarification_answers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    endpoint = f"{settings.PROTOCOL_ASSISTANT_URL.rstrip('/')}/assist"
    payload = {"query": query, "top_k": max(1, int(top_k))}
    if clarification_answers:
        payload["clarification_answers"] = clarification_answers
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    timeout = float(getattr(settings, "PROTOCOL_ASSISTANT_TIMEOUT", 30))
    with urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("assistant response has invalid format")
    return data


def _extract_clarification_answers(post_data: Mapping[str, Any]) -> Dict[str, str]:
    answers: Dict[str, str] = {}
    for key, raw_value in post_data.items():
        if not key.startswith(CLARIFICATION_FIELD_PREFIX):
            continue
        qid = key[len(CLARIFICATION_FIELD_PREFIX) :].strip()
        if not qid:
            continue
        value = str(raw_value or "").strip().lower()
        if value not in VALID_CLARIFICATION_ANSWERS:
            value = "unknown"
        answers[qid] = value
    return answers


def _normalize_clarification_items(
    questions: List[Dict[str, Any]],
    selected_answers: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    selected_answers = selected_answers or {}
    items: List[Dict[str, str]] = []
    for raw_question in questions:
        if not isinstance(raw_question, dict):
            continue
        qid = str(raw_question.get("id", "")).strip()
        qtext = str(raw_question.get("question", "")).strip()
        if not qid or not qtext:
            continue
        selected = str(selected_answers.get(qid, "unknown")).strip().lower()
        if selected not in VALID_CLARIFICATION_ANSWERS:
            selected = "unknown"
        items.append(
            {
                "id": qid,
                "question": qtext,
                "selected": selected,
            }
        )
    return items


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


def assistant(request):
    """Ассистент по клиническим протоколам: только вопрос -> ответ."""
    query = ""
    answer = ""
    awaiting_clarification = False
    clarification_items: List[Dict[str, str]] = []

    if request.method == "POST":
        stage = str(request.POST.get("stage", "query")).strip().lower()
        query = " ".join(str(request.POST.get("query", "")).split())
        words_count = len(query.split())

        if not query:
            messages.error(
                request,
                _("Опишите состояние пациента перед отправкой."),
            )
        elif stage == "query" and words_count < 10:
            messages.error(
                request,
                _("Опишите состояние подробнее: минимум 10 слов."),
            )
        else:
            clarification_answers = {}
            if stage == "clarify":
                clarification_answers = _extract_clarification_answers(request.POST)
            try:
                payload = _request_protocol_assistant(
                    query=query,
                    top_k=3,
                    clarification_answers=clarification_answers,
                )
                clarification = payload.get("clarification", {})
                required = bool(clarification.get("required"))
                questions = clarification.get("questions") or []
                if not isinstance(questions, list):
                    questions = []

                if required and questions:
                    awaiting_clarification = True
                    clarification_items = _normalize_clarification_items(
                        questions=questions,
                        selected_answers=clarification_answers,
                    )
                    messages.info(
                        request,
                        _("Чтобы дать точные рекомендации, ответьте на уточняющие вопросы."),
                    )
                else:
                    answer = str(payload.get("assistant_answer", "")).strip()
                    if not answer:
                        raise RuntimeError("assistant response is empty")
            except HTTPError:
                messages.error(
                    request,
                    _("Ассистент временно недоступен. Попробуйте снова через несколько минут."),
                )
            except URLError:
                messages.error(
                    request,
                    _("Не удалось подключиться к сервису ассистента."),
                )
            except Exception:
                messages.error(
                    request,
                    _("Не удалось получить ответ. Попробуйте уточнить описание."),
                )

    context = {
        "query": query,
        "answer": answer,
        "awaiting_clarification": awaiting_clarification,
        "clarification_items": clarification_items,
        "example_query": (
            "Пациент 35 лет, кашель с мокротой 4 дня, температура 38.2, "
            "боль в грудной клетке при вдохе, одышка при нагрузке."
        ),
    }
    return render(request, "assistant.html", context)


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
