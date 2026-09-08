from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/generate/', views.api_generate_quiz, name='api_generate_quiz'),
    path('api/save-history/', views.api_save_history, name='api_save_history'),
]
