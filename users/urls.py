from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),          
    path('logout/', views.logout_view, name='logout'),        
    path('profile/', views.profile_dashboard, name='profile_dashboard'),
    path('register/', views.register_view, name='register'),
]
