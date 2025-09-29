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
from .utils import make_authenticated_request

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
    products = []
    categories = []
    units = []
    total_stock = 0
    low_stock_count = 0

    # Fetch Products
    resp_products = make_authenticated_request(request, "GET", "http://127.0.0.1:8080/api/products/")
    if resp_products.status_code == 200:
        products = resp_products.json()
        total_stock = sum(p.get("stock", 0) for p in products)
        low_stock_count = sum(1 for p in products if p.get("stock", 0) <= p.get("minQuantity", 0))

    # Fetch Categories
    resp_cats = make_authenticated_request(request, "GET", "http://127.0.0.1:8080/api/categories/")
    if resp_cats.status_code == 200:
        categories = resp_cats.json()

    # Fetch Units
    resp_units = make_authenticated_request(request, "GET", "http://127.0.0.1:8080/api/units/")
    if resp_units.status_code == 200:
        units = resp_units.json()

    context = {
        "products": products,
        "categories": categories,
        "units": units,
        "total_stock": total_stock,
        "low_stock_count": low_stock_count,
    }
    return render(request, "pages/inventory.html", context)

@api_login_required
def add_product(request):
    if request.method == "POST":
        user_client = request.session.get("user_client_id")
        if not user_client:
            messages.error(request, "⚠️ Missing user_client_id. Please re-login.")
            return redirect("inventory")

        category_id = request.POST.get("category")
        unit_id = request.POST.get("unit")

        if not category_id or not unit_id:
            messages.error(request, "⚠️ Please select both a category and a unit.")
            return redirect("inventory")

        data = {
            "user_client": user_client,          # UUID
            "category": category_id,             # UUID string ✅
            "unit": unit_id,                     # UUID string ✅
            "name": request.POST.get("name"),
            "sku": request.POST.get("sku") or "",
            "barcode": request.POST.get("barcode") or "",
            "description": request.POST.get("description") or "",
            "minQuantity": int(request.POST.get("minQuantity") or 0),
            "price": str(request.POST.get("price") or "0.00"),
            "cost": str(request.POST.get("cost") or "0.00"),
            "stock": int(request.POST.get("stock") or 0),
        }

        # print("📦 ADD PRODUCT DATA:", data)
        resp = make_authenticated_request(request, "POST", "http://127.0.0.1:8080/api/products/", data=data)
        # print("📦 RESPONSE:", resp.status_code, resp.text)

        if resp.status_code in [200, 201]:
            messages.success(request, "✅ Product added successfully.")
        else:
            messages.error(request, f"❌ Failed to add product: {resp.text}")

    return redirect("inventory")

# ----------------- EDIT PRODUCT -----------------
@api_login_required
def edit_product(request, product_id):
    if request.method == "POST":
        user_client = request.session.get("user_client_id")
        if not user_client:
            messages.error(request, "⚠️ Missing user client. Please re-login.")
            return redirect("inventory")

        data = {
            "user_client": user_client,                      # UUID string
            "category": request.POST.get("category"),         # UUID string
            "unit": request.POST.get("unit"),                 # UUID string
            "name": request.POST.get("name"),
            "sku": request.POST.get("sku") or "",
            "barcode": request.POST.get("barcode") or "",
            "description": request.POST.get("description") or "",
            "minQuantity": int(request.POST.get("minQuantity") or 0),
            "price": str(request.POST.get("price") or "0.00"),
            "cost": str(request.POST.get("cost") or "0.00"),
            "stock": int(request.POST.get("stock") or 0),
        }

        url = f"http://127.0.0.1:8080/api/products/{product_id}/"
        print("✏️ EDIT PRODUCT:", data)

        response = make_authenticated_request(request, "PUT", url, data=data)
        print("✏️ RESPONSE:", response.status_code, response.text)

        if response.status_code in (200, 201):
            messages.success(request, "✅ Product updated successfully.")
        else:
            messages.error(request, f"❌ Failed to update product: {response.text}")

    return redirect("inventory")

# ----------------- DELETE PRODUCT(S) -----------------
@api_login_required
def delete_products(request):
    if request.method == "POST":
        ids = request.POST.getlist("product_ids")
        deleted = 0
        for pid in ids:
            url = f"http://127.0.0.1:8080/api/products/{pid}/"
            resp = make_authenticated_request(request, "DELETE", url)
            if resp.status_code in (200, 204):
                deleted += 1

        if deleted:
            messages.success(request, f"🗑️ Deleted {deleted} product(s).")
        else:
            messages.error(request, "⚠️ No products deleted.")
    return redirect("inventory")

# ----------------- UPLOAD CSV -----------------
@api_login_required
def upload_products_csv(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        decoded = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))

        user_client = request.session.get("user_client_id")
        if not user_client:
            messages.error(request, "⚠️ Missing user client. Please re-login.")
            return redirect("inventory")

        count = 0
        for row in reader:
            # Validate required fields exist
            if not row.get("name") or not row.get("category") or not row.get("unit"):
                continue  # skip incomplete rows

            data = {
                "user_client": user_client,
                "category": row.get("category"),     # UUID or ID
                "unit": row.get("unit"),             # UUID or ID
                "name": row.get("name"),
                "sku": row.get("sku") or "",
                "barcode": row.get("barcode") or "",
                "description": row.get("description") or "",
                "minQuantity": int(row.get("minQuantity") or 0),
                "price": str(row.get("price") or "0.00"),
                "cost": str(row.get("cost") or "0.00"),
                "stock": int(row.get("stock") or 0),
            }

            resp = make_authenticated_request(request, "POST", "http://127.0.0.1:8080/api/products/", data=data)
            if resp.status_code in (200, 201):
                count += 1
            else:
                print("⚠️ Failed row:", row, resp.text)

        messages.success(request, f"📦 Uploaded {count} products from CSV.")
    else:
        messages.error(request, "⚠️ No file selected or invalid format.")

    return redirect("inventory")

API_BASE = "http://127.0.0.1:8080/api/"

@api_login_required
def product_management(request):
    """Show product management dashboard with categories, units, alerts, etc."""
    products = make_authenticated_request(request, "GET", f"{API_BASE}products/").json()
    categories = make_authenticated_request(request, "GET", f"{API_BASE}categories/").json()
    units = make_authenticated_request(request, "GET", f"{API_BASE}units/").json()
    alerts = make_authenticated_request(request, "GET", f"{API_BASE}stock-alerts/").json()

    return render(request, "pages/product_management.html", {
        "products": products,
        "categories": categories,
        "units": units,
        "alerts": alerts,
    })

# ----------------- CATEGORY CRUD -----------------
@api_login_required
def add_category(request):
    if request.method == "POST":
        data = {
            "user_client": request.session.get("user_client_id"),
            "name": request.POST.get("name"),
            "description": request.POST.get("description") or "",
        }
        resp = make_authenticated_request(request, "POST", f"{API_BASE}categories/", data=data)
        if resp.status_code in (200, 201):
            messages.success(request, "✅ Category added successfully.")
        else:
            messages.error(request, f"❌ Failed to add category: {resp.text}")
    return redirect("product_management")

@api_login_required
def edit_category(request, category_id):
    if request.method == "POST":
        user_client = request.session.get("user_client_id")

        data = {
            "user_client": user_client,
            "name": request.POST.get("name"),
            "description": request.POST.get("description") or "",
        }

        url = f"{API_BASE}categories/{category_id}/"
        resp = make_authenticated_request(request, "PUT", url, data=data)

        if resp.status_code in [200, 201]:
            messages.success(request, "✏️ Category updated successfully.")
        else:
            messages.error(request, f"❌ Failed to update: {resp.text}")

    return redirect("product_management")

@api_login_required
def delete_category(request, category_id):
    url = f"{API_BASE}categories/{category_id}/"
    resp = make_authenticated_request(request, "DELETE", url)
    if resp.status_code in (200, 204):
        messages.success(request, "🗑️ Category deleted.")
    else:
        messages.error(request, f"❌ Delete failed: {resp.text}")
    return redirect("product_management")

# ----------------- UNIT CRUD -----------------
@api_login_required
def add_unit(request):
    if request.method == "POST":
        data = {
            "user_client": request.session.get("user_client_id"),
            "unit_name": request.POST.get("unit_name"),
            "description": request.POST.get("description") or "",
        }
        resp = make_authenticated_request(request, "POST", f"{API_BASE}units/", data=data)
        if resp.status_code in (200, 201):
            messages.success(request, "✅ Unit added successfully.")
        else:
            messages.error(request, f"❌ Failed to add unit: {resp.text}")
    return redirect("product_management")

@api_login_required
def edit_unit(request, unit_id):
    if request.method == "POST":
        user_client = request.session.get("user_client_id")

        data = {
            "user_client": user_client,
            "unit_name": request.POST.get("unit_name"),
            "description": request.POST.get("description") or "",
        }

        url = f"{API_BASE}units/{unit_id}/"
        resp = make_authenticated_request(request, "PUT", url, data=data)

        if resp.status_code in [200, 201]:
            messages.success(request, "✏️ Unit updated successfully.")
        else:
            messages.error(request, f"❌ Failed to update: {resp.text}")

    return redirect("product_management")

@api_login_required
def delete_unit(request, unit_id):
    url = f"{API_BASE}units/{unit_id}/"
    resp = make_authenticated_request(request, "DELETE", url)
    if resp.status_code in (200, 204):
        messages.success(request, "🗑️ Unit deleted.")
    else:
        messages.error(request, f"❌ Delete failed: {resp.text}")
    return redirect("product_management")


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