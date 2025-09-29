import requests
from django.conf import settings
from django.utils import timezone

def global_context(request):
    # API liveness
    api_url = getattr(settings, 'API_URL', 'http://127.0.0.1:8080/api/')
    try:
        response = requests.options(api_url, timeout=2)
        api_status = 'Online' if response.status_code in [200, 204, 401, 403, 405] else 'Offline'
    except Exception:
        api_status = 'Offline'

    # Example: unread notifications (placeholder, replace with your model/query)
    unread_notifications = 0
    if request.user.is_authenticated:
        # Example: Notification.objects.filter(user=request.user, read=False).count()
        pass

    # Feature flags (placeholder, could be from settings or DB)
    feature_flags = {
        'new_dashboard': False,
        'beta_feature': False,
    }

    # Maintenance mode (placeholder, could be from settings or DB)
    maintenance_mode = getattr(settings, 'MAINTENANCE_MODE', False)

    return {
        'api_status': api_status,
        'api_url': api_url,
        'site_name': getattr(settings, 'SITE_NAME', 'AsiriaPOS'),
        'current_time': timezone.now(),
        'unread_notifications': unread_notifications,
        'is_admin': request.user.is_superuser if request.user.is_authenticated else False,
        'feature_flags': feature_flags,
        'maintenance_mode': maintenance_mode,
    } 