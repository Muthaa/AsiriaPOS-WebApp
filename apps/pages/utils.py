import requests
from django.conf import settings

def get_api_headers(request):
    """
    Get headers for API requests including authentication token
    """
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Add access token if available
    access_token = request.session.get('access_token')
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'
    
    return headers

def refresh_api_token(request):
    """
    Refresh the API access token using the refresh token
    """
    refresh_token = request.session.get('refresh_token')
    if not refresh_token:
        return False
    
    try:
        response = requests.post(
            'http://127.0.0.1:8080/api/token/refresh/',
            json={'refresh': refresh_token},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            request.session['access_token'] = data.get('access')
            return True
        else:
            # Refresh failed, clear session
            clear_api_session(request)
            return False
    except Exception:
        clear_api_session(request)
        return False

def clear_api_session(request):
    """
    Clear all API-related session data
    """
    session_keys_to_clear = [
        'access_token', 
        'refresh_token', 
        'user_client_id', 
        'is_authenticated',
        'user_name',
        'store_name',
        'user_role'
    ]
    
    for key in session_keys_to_clear:
        if key in request.session:
            del request.session[key]

def make_authenticated_request(request, method, url, data=None, **kwargs):
    """
    Make an authenticated API request with automatic token refresh
    """
    headers = get_api_headers(request)
    
    # Make the request
    response = requests.request(
        method=method,
        url=url,
        json=data,
        headers=headers,
        **kwargs
    )
    
    # If token expired, try to refresh
    if response.status_code == 401:
        if refresh_api_token(request):
            # Retry with new token
            headers = get_api_headers(request)
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                **kwargs
            )
    
    return response 