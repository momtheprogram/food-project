from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import RecipeViewSet, IngredientViewSet, TagViewSet


app_name = 'api'

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
]