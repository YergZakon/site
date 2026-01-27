from .models import SiteSettings


def site_settings(request):
    """Добавляет настройки сайта во все шаблоны"""
    return {
        'site_settings': SiteSettings.get_settings(),
        'current_language': request.LANGUAGE_CODE,
    }
