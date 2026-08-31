from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),          
    path('logout/', views.logout_view, name='logout'),        
    path('profile/', views.profile_dashboard, name='profile_dashboard'),
    path('register/', views.register_view, name='register'),
    path('cancel/<int:pk>/', views.appointment_cancel, name='appointment_cancel'),
    path('update/<int:pk>/', views.appointment_update, name='appointment_update'),

]
