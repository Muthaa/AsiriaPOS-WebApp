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
    path("inventory/add/", views.add_product, name="add_product"),
    # path("inventory/<int:product_id>/edit/", views.edit_product, name="edit_product"),
    path("inventory/edit/<uuid:product_id>/", views.edit_product, name="edit_product"),
    path("inventory/delete/", views.delete_products, name="delete_products"),
    path("inventory/upload/", views.upload_products_csv, name="upload_products_csv"),

    path("inventory/management/", views.product_management, name="product_management"),

    path("inventory/category/add/", views.add_category, name="add_category"),
    path("inventory/category/edit/<uuid:category_id>/", views.edit_category, name="edit_category"),
    path("inventory/category/delete/<uuid:category_id>/", views.delete_category, name="delete_category"),

    path("inventory/unit/add/", views.add_unit, name="add_unit"),
    path("inventory/unit/edit/<uuid:unit_id>/", views.edit_unit, name="edit_unit"),
    path("inventory/unit/delete/<uuid:unit_id>/", views.delete_unit, name="delete_unit"),

    path('sales/', views.sales, name='sales'),
    path('expenses/', views.expenses, name='expenses'),
    path('users/', views.users, name='users'),
    path('reports/', views.reports, name='reports'),
]
