from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionsListSet,
                    TagViewSet, UserSet)

app_name = 'api'

router = DefaultRouter()

router.register(r'^tags', TagViewSet, basename='tags')
router.register(r'^ingredients', IngredientViewSet, basename='ingredients')
router.register(r'^recipes', RecipeViewSet, basename='recipes')
router.register(r'^users', UserSet, basename='users')
router.register(r'^users/(?P<user_id>\d+)', UserSet, basename='users')
router.register(
    r'^users/subscriptions', SubscriptionsListSet, basename='subscriptions'
)

urlpatterns = [
    path('', include(router.urls)),
    url('', include('djoser.urls')),
    url('auth/', include('djoser.urls.authtoken')),
]
