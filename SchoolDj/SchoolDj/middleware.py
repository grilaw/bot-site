
from django.http import JsonResponse
from django.conf import settings


class RestrictExternalRefererMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем только GET запросы
        if request.method == 'GET':
            # Получаем referer или origin
            referer = request.META.get('HTTP_REFERER', '')
            origin = request.META.get('HTTP_ORIGIN', '')
            
            # Ваш домен
            allowed_host = settings.ALLOWED_HOSTS[0]  # или конкретный домен
            
            # Проверяем, что запрос пришел с вашего сайта
            is_from_site = False
            
            if referer and allowed_host in referer:
                is_from_site = True
            if origin and allowed_host in origin:
                is_from_site = True
            
            # Для API эндпоинтов, которые должны быть доступны только с вашего сайта
            if request.path.startswith('/api/protected/') and not is_from_site:
                return JsonResponse({'error': 'Access denied'}, status=403)
        
        return self.get_response(request)