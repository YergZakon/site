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
ASSISTANT_SESSION_ANSWERS_KEY = "assistant_clarification_answers"
ANSWER_BLOCK_TITLES = [
    "Что делать сейчас",
    "Какие обследования обычно нужны",
    "Как лечат",
    "Какие лекарства могут применяться",
    "Когда нужна госпитализация или срочная помощь",
    "Контроль и профилактика",
]
ANSWER_BLOCK_TITLE_MAP = {title.casefold(): title for title in ANSWER_BLOCK_TITLES}


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


def _build_persistent_answers(
    all_answers: Mapping[str, Any],
    active_question_ids: List[str],
) -> Dict[str, str]:
    active_set = {str(qid).strip() for qid in active_question_ids if str(qid).strip()}
    persistent: Dict[str, str] = {}
    for key, raw_value in all_answers.items():
        qid = str(key or "").strip()
        value = str(raw_value or "").strip().lower()
        if not qid or qid in active_set:
            continue
        if value not in VALID_CLARIFICATION_ANSWERS:
            continue
        if value == "unknown":
            continue
        persistent[qid] = value
    return persistent


def _normalize_answers_map(raw_answers: Mapping[str, Any]) -> Dict[str, str]:
    normalized: Dict[str, str] = {}
    for key, raw_value in raw_answers.items():
        qid = str(key or "").strip()
        if not qid:
            continue
        value = str(raw_value or "").strip().lower()
        if value not in VALID_CLARIFICATION_ANSWERS:
            value = "unknown"
        normalized[qid] = value
    return normalized


def _merge_answers_maps(*maps: Mapping[str, Any]) -> Dict[str, str]:
    merged: Dict[str, str] = {}
    for source in maps:
        merged.update(_normalize_answers_map(source))
    return merged


def _to_session_answers(raw_answers: Mapping[str, Any]) -> Dict[str, str]:
    answers = _normalize_answers_map(raw_answers)
    return {qid: value for qid, value in answers.items() if value in {"yes", "no"}}


def _dedupe_keep_order(items: List[str]) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for raw in items:
        value = " ".join(str(raw or "").split()).strip()
        if not value:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def _strip_bullet_prefix(line: str) -> str:
    value = str(line or "").strip()
    for prefix in ("- ", "• ", "▪ ", "● ", "* "):
        if value.startswith(prefix):
            return value[len(prefix) :].strip()
    if value and value[0] in "-•▪●*":
        return value[1:].strip()
    return value


def _parse_answer_blocks(answer: str) -> Dict[str, Any]:
    lead_lines: List[str] = []
    blocks: List[Dict[str, Any]] = []
    current_block: Optional[Dict[str, Any]] = None

    for raw_line in str(answer or "").splitlines():
        line = " ".join(raw_line.split()).strip()
        if not line:
            continue
        normalized_heading = line.rstrip(":").strip().casefold()
        title = ANSWER_BLOCK_TITLE_MAP.get(normalized_heading)
        if title:
            current_block = {"title": title, "items": []}
            blocks.append(current_block)
            continue

        item = _strip_bullet_prefix(line)
        if not item:
            continue

        if current_block is None:
            lead_lines.append(item)
        else:
            current_block["items"].append(item)

    for block in blocks:
        block["items"] = _dedupe_keep_order(block.get("items", []))
    lead_lines = _dedupe_keep_order(lead_lines)

    return {
        "lead_text": "\n".join(lead_lines),
        "blocks": blocks,
    }


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
    answer_lead_text = ""
    answer_blocks: List[Dict[str, Any]] = []
    awaiting_clarification = False
    clarification_items: List[Dict[str, str]] = []
    persistent_clarification_answers: Dict[str, str] = {}

    if request.method == "POST":
        stage = str(request.POST.get("stage", "query")).strip().lower()
        query = " ".join(str(request.POST.get("query", "")).split())
        words_count = len(query.split())
        session_answers = _normalize_answers_map(
            request.session.get(ASSISTANT_SESSION_ANSWERS_KEY, {})
        )

        if stage == "query":
            session_answers = {}
            request.session.pop(ASSISTANT_SESSION_ANSWERS_KEY, None)

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
                clarification_answers = _merge_answers_maps(
                    session_answers,
                    _extract_clarification_answers(request.POST),
                )
            try:
                payload = _request_protocol_assistant(
                    query=query,
                    top_k=3,
                    clarification_answers=clarification_answers,
                )
                clarification = payload.get("clarification", {})
                required = bool(clarification.get("required"))
                questions = clarification.get("questions") or []
                all_answers = clarification.get("answers") or {}
                if not isinstance(questions, list):
                    questions = []
                if not isinstance(all_answers, dict):
                    all_answers = {}
                all_answers_normalized = _merge_answers_maps(session_answers, all_answers)
                answered_count = int(clarification.get("answered_count") or 0)

                if required and questions:
                    awaiting_clarification = True
                    clarification_items = _normalize_clarification_items(
                        questions=questions,
                        selected_answers=all_answers_normalized,
                    )
                    question_ids = [
                        str(item.get("id", "")).strip()
                        for item in clarification_items
                        if str(item.get("id", "")).strip()
                    ]
                    persistent_clarification_answers = _build_persistent_answers(
                        all_answers=all_answers_normalized,
                        active_question_ids=question_ids,
                    )
                    request.session[ASSISTANT_SESSION_ANSWERS_KEY] = _to_session_answers(
                        all_answers_normalized
                    )
                    request.session.modified = True
                    if stage == "clarify" and answered_count <= 0:
                        messages.warning(
                            request,
                            _("Выберите хотя бы один вариант Да/Нет, иначе рекомендации не уточнятся."),
                        )
                    messages.info(
                        request,
                        _("Чтобы дать точные рекомендации, ответьте на уточняющие вопросы."),
                    )
                else:
                    answer = str(payload.get("assistant_answer", "")).strip()
                    if not answer:
                        raise RuntimeError("assistant response is empty")
                    parsed_answer = _parse_answer_blocks(answer)
                    answer_lead_text = parsed_answer.get("lead_text", "")
                    answer_blocks = parsed_answer.get("blocks", [])
                    request.session.pop(ASSISTANT_SESSION_ANSWERS_KEY, None)
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
        "answer_lead_text": answer_lead_text,
        "answer_blocks": answer_blocks,
        "awaiting_clarification": awaiting_clarification,
        "clarification_items": clarification_items,
        "persistent_clarification_answers": persistent_clarification_answers,
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
