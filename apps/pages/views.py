import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm
from .decorators import api_login_required
from .utils import clear_api_session
from django.http import JsonResponse

# Create your views here.

@api_login_required
def index(request):

    # Page from the theme 
    return render(request, 'pages/index.html')

@api_login_required
def get_todays_sales(request):
    """
    Fetch today's sales data from the API
    """
    try:
        from .utils import make_authenticated_request
        
        response = make_authenticated_request(
            request, 
            'GET', 
            'http://127.0.0.1:8080/api/sales/today/'
        )
        
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse(
                {'error': f'API Error: {response.status_code}'}, 
                status=response.status_code
            )
    except Exception as e:
        return JsonResponse(
            {'error': f'Connection Error: {str(e)}'}, 
            status=500
        )

def register(request):
    success_message = None
    error_message = None
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = {
                'storename': form.cleaned_data['storename'],
                'client_name': form.cleaned_data['client_name'],
                'phone_number': form.cleaned_data['phone_number'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
                'password_confirmation': form.cleaned_data['password_confirmation'],
                'address': form.cleaned_data['address'],
            }
            try:
                response = requests.post('http://127.0.0.1:8080/api/clients/', json=data)
                print(f"API POST response: {response.status_code} {response.text}")  # Debug print
                if response.status_code == 201:
                    success_message = 'Registration successful! You can now log in.'
                    form = RegistrationForm()  # Reset the form
                else:
                    error_message = f"API Error: {response.status_code} {response.text}"
                    print(f"Error message set: {error_message}")  # Debug print
            except Exception as e:
                error_message = f"API Connection Error: {e}"
                print(f"Exception: {error_message}")  # Debug print
        else:
            error_message = "Form validation failed. Please correct the errors below."
            print("Form validation failed.")  # Debug print
    else:
        form = RegistrationForm()
    print(f"Rendering register page with success_message: {success_message}, error_message: {error_message}")  # Debug print
    return render(request, 'accounts/register.html', {'form': form, 'success_message': success_message, 'error_message': error_message})

def login(request):
    success_message = None
    error_message = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = {
                'phone_number': form.cleaned_data['phone_number'],
                'password': form.cleaned_data['password'],
            }
            try:
                response = requests.post('http://127.0.0.1:8080/api/token/', json=data)
                print(f"API Login response: {response.status_code} {response.text}")  # Debug print
                
                if response.status_code == 200:
                    # API returns JWT tokens and user data directly
                    api_data = response.json()
                    
                    # Store API tokens and user data in session
                    request.session['access_token'] = api_data.get('access')
                    request.session['refresh_token'] = api_data.get('refresh')
                    request.session['user_client_id'] = api_data.get('user_client_id')
                    
                    # Store user details from login response
                    request.session['user_name'] = api_data.get('client_name', 'User')
                    request.session['store_name'] = api_data.get('storename', '')
                    request.session['user_role'] = api_data.get('role', 'Client')
                    
                    # Mark user as authenticated in session
                    request.session['is_authenticated'] = True
                    
                    success_message = 'Login successful!'
                    return redirect('index')  # or wherever you want to redirect after login
                else:
                    # Handle specific error cases
                    try:
                        error_data = response.json()
                        if response.status_code == 401:
                            error_message = "Invalid phone number or password. Please check your credentials."
                        elif 'detail' in error_data:
                            error_message = f"Login failed: {error_data['detail']}"
                        else:
                            error_message = f"Login failed: {response.text}"
                    except:
                        error_message = f"Login failed: {response.text}"
            except Exception as e:
                error_message = f"API Connection Error: {e}"
        else:
            error_message = "Please correct the errors below."
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'success_message': success_message,
        'error_message': error_message
    })

def logout(request):
    # Clear all API authentication data from session
    clear_api_session(request)
    
    # Redirect to login page
    return redirect('login')

def test_api_auth(request):
    """
    Test view to help debug API authentication requirements
    """
    if request.method == 'POST':
        # Test different field name combinations
        test_cases = [
            {
                'phone_number': request.POST.get('phone_number'),
                'password': request.POST.get('password')
            },
            {
                'username': request.POST.get('phone_number'),
                'password': request.POST.get('password')
            },
            {
                'email': request.POST.get('phone_number'),
                'password': request.POST.get('password')
            }
        ]
        
        results = []
        for i, data in enumerate(test_cases):
            try:
                response = requests.post('http://127.0.0.1:8080/api/token/', json=data)
                results.append({
                    'case': f'Case {i+1}: {list(data.keys())}',
                    'status': response.status_code,
                    'response': response.text[:200]  # First 200 chars
                })
            except Exception as e:
                results.append({
                    'case': f'Case {i+1}: {list(data.keys())}',
                    'status': 'Error',
                    'response': str(e)
                })
        
        return render(request, 'pages/test_api.html', {
            'results': results,
            'phone_number': request.POST.get('phone_number')
        })
    
    return render(request, 'pages/test_api.html')

@api_login_required
def pos(request):
    return render(request, 'pages/pos.html')

@api_login_required
def purchases(request):
    return render(request, 'pages/purchases.html')

@api_login_required
def inventory(request):
    return render(request, 'pages/inventory.html')

@api_login_required
def sales(request):
    return render(request, 'pages/sales.html')

@api_login_required
def expenses(request):
    return render(request, 'pages/expenses.html')

@api_login_required
def users(request):
    return render(request, 'pages/users.html')

@api_login_required
def reports(request):
    return render(request, 'pages/reports.html')