from django.urls import path

from . import views

app_name = 'mill'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-account/', views.my_account, name='my_account'),

    path('api/track/', views.track_order_api, name='track_order_api'),
    path('api/estimate-fare/', views.estimate_fare_api, name='estimate_fare_api'),

    path('mill-admin/login/', views.admin_login_view, name='admin_login'),
    path('mill-admin/logout/', views.admin_logout_view, name='admin_logout'),
    path('mill-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('mill-admin/orders/<str:tracking_number>/status/', views.admin_update_status, name='admin_update_status'),
]
