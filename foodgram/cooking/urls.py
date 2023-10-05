from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.index),
    # Отдельная страница с описанием конкретного рецепта
    path('recipe/<slug:slug>/', views.recipe_detail),
]
