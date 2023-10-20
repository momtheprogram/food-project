import csv

import django_filters.rest_framework
from django.db.models import Sum
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from cooking.models import (Cart, Favorite, Ingredient, IngredientQuantity,
                            Recipe, Tag)
from users.models import Subscribe, User

from .filters import CustomIngredientsFilter, RecipeFilter
from .paginators import CustomPagination
from .permissions import IsOwnerOrAcceptedMethods
from .serializers import (AuthorSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeLinkedModelsSerializer,
                          RecipeSerializer, SubscribeListSerializer,
                          TagSerializer, UserCreateSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrAcceptedMethods,)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def patch(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeCreateSerializer(
            recipe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201, data=serializer.data)
        return Response(status=400, data="wrong parameters")

    @action(detail=True, permission_classes=[permissions.IsAuthenticated],
            methods=['get', 'delete'])
    def shopping_cart(self, request, pk=None, model_name: str = 'cart'):
        kwargs = self.do_action_with_model(request, pk, model_name)
        return Response(**kwargs)

    @action(detail=True, permission_classes=[permissions.IsAuthenticated],
            methods=['get', 'delete'])
    def favorite(self, request, pk=None, model_name: str = 'favorite'):
        kwargs = self.do_action_with_model(request, pk, model_name)
        return Response(**kwargs)

    def do_action_with_model(self, request, pk: int, model_name: str):
        model = {
            'cart': Cart,
            'favorite': Favorite,
        }.get(model_name)

        if request.method == 'GET':
            kwargs = self.add_recipe_to_model(request, pk, model)  # noqa
            return kwargs
        elif request.method == 'DELETE':
            kwargs = self.delete_model_with_recipe(request, pk, model)  # noqa
            return kwargs

    def add_recipe_to_model(self, request, pk, model: Cart or Favorite):
        recipe = get_object_or_404(Recipe, pk=pk)
        new_model = model.objects.filter(
            recipe=recipe,
            user=request.user,
        )
        if new_model:
            return {'status': status.HTTP_400_BAD_REQUEST}
        model.objects.create(
            recipe=recipe,
            user=request.user,
        )
        serializer = RecipeLinkedModelsSerializer(recipe)
        return {'data': serializer.data, 'status': status.HTTP_200_OK}

    def delete_model_with_recipe(self, request, pk, model: Cart or Favorite):
        recipe = get_object_or_404(Recipe, pk=pk)
        model_with_recipe = model.objects.get(
            user=request.user,
            recipe=recipe
        )
        if not model_with_recipe:
            return status.HTTP_400_BAD_REQUEST
        model_with_recipe.delete()
        return {'status': status.HTTP_204_NO_CONTENT}

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user_cart = (
            Cart.objects.filter(user=request.user)
            .values_list('recipe', flat=True)
        )
        ingredients = (
            IngredientQuantity.objects.filter(recipe__id__in=user_cart)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amounts=Sum('amount')).all()
        )
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition':
                    'attachment; filename="Список покупок.csv"'
            },
        )

        writer = csv.writer(response)
        for ing in ingredients:
            writer.writerow(
                [str(ing['ingredient__name']),
                 str(ing['amounts']),
                 str(ing['ingredient__measurement_unit'])]
            )
        return response


class IngredientViewSet(ListAPIView, RetrieveAPIView, viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = CustomIngredientsFilter
    pagination_class = None


class TagViewSet(ListAPIView, RetrieveAPIView, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class UserSet(mixins.ListModelMixin,
              mixins.CreateModelMixin,
              viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = AuthorSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in {'create'}:
            return UserCreateSerializer
        return AuthorSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return get_object_or_404(User, id=user_id)
        queryset = User.objects.all()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if isinstance(queryset, User):
            serializer = self.get_serializer(queryset)
            return JsonResponse(serializer.data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data)

    @action(detail=True, permission_classes=[permissions.IsAuthenticated],
            methods=['delete', 'get'])
    def subscribe(self, request, pk=None):
        if request.method == 'DELETE':
            kwargs = self.delete_subscribe(request, pk)
            return Response(**kwargs)

        elif request.method == 'GET':
            kwargs = self.create_subscribe(request, pk)
            return Response(**kwargs)

    def create_subscribe(self, request, author_id: int) -> dict:
        author = get_object_or_404(User, pk=author_id)
        subscribe = Subscribe.objects.filter(
            author=author,
            user=request.user,
        )
        if subscribe or author_id == request.user.pk:
            return {
                'data': {'error_400': 'Ошибка подписки'},
                'status': status.HTTP_400_BAD_REQUEST,
            }
        new_subscribe = Subscribe.objects.create(
            author=author,
            user=request.user,
        )
        serializer = SubscribeListSerializer(new_subscribe)
        return {'data': serializer.data, 'status': status.HTTP_200_OK}

    def delete_subscribe(self, request, pk) -> dict:
        if pk == request.user.id:
            return {'status': status.HTTP_400_BAD_REQUEST}
        subscribe = get_object_or_404(
            Subscribe, author=pk, user=request.user.id)
        subscribe.delete()
        return {'status': status.HTTP_204_NO_CONTENT}


class SubscriptionsListSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubscribeListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Subscribe.objects.filter(user=self.request.user)
        return queryset
