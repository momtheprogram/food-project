from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from cooking.models import Recipe
from serializers import RecipeSerializers, RecipeListSerializers


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer # написать

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer  # написать сериализатор на отображение
        return RecipeSerializer  # написать сериализатор на создание


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = ...
    serializer_class = ...


class TagViewSet(ReadOnlyModelViewSet):
    queryset = ...
    serializer_class = ...
