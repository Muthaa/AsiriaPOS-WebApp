from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/logout/', views.logout, name='logout'),
    path('dashboard-api/sales/today/', views.get_todays_sales, name='get_todays_sales'),
    path('test-api/', views.test_api_auth, name='test_api_auth'),
    # App sections
    path('pos/', views.pos, name='pos'),
    path('purchases/', views.purchases, name='purchases'),
    path('inventory/', views.inventory, name='inventory'),
    path('sales/', views.sales, name='sales'),
    path('expenses/', views.expenses, name='expenses'),
    path('users/', views.users, name='users'),
    path('reports/', views.reports, name='reports'),
]
