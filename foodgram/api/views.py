from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .serializers import RecipeSerializer, RecipeListSerializer, IngredientSerializer, TagSerializer, FollowListSerializer
from cooking.models import Recipe, Ingredient, Tag
from users.models import User


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FollowListViewSet(ListAPIView):
    serializer_class = FollowListSerializer

    def get_queryset(self):
        return User.objects.filter(author__user=self.request.user)