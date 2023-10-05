from django.shortcuts import render
from django.http import HttpResponse


# Главная страница
def index(request):
    return HttpResponse('Рецепты')


# Страница конкретного рецепта
# view-функция принимает параметр slug из path()
def recipe_detail(request, slug):
    return HttpResponse(f'Рецепт {slug}')
