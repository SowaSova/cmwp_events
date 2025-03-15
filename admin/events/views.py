import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Получаем логгер Django
logger = logging.getLogger('django')

@csrf_exempt
@require_POST
def log_from_frontend(request):
    """
    Обработчик для логов, отправленных с фронтенда через AJAX.
    Принимает POST-запросы с параметрами:
    - level: уровень лога (debug, info, warning, error)
    - message: сообщение для логирования
    - source: источник сообщения (например, имя JS-файла)
    """
    try:
        level = request.POST.get('level', 'info')
        message = request.POST.get('message', '')
        source = request.POST.get('source', 'frontend')
        
        # Формируем сообщение для лога
        log_message = f"[{source}] {message}"
        
        # Логируем сообщение с соответствующим уровнем
        if level == 'debug':
            logger.debug(log_message)
        elif level == 'warning':
            logger.warning(log_message)
        elif level == 'error':
            logger.error(log_message)
        else:  # По умолчанию используем info
            logger.info(log_message)
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Ошибка при обработке лога с фронтенда: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500) 