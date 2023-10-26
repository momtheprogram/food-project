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
from .permissions import IsOwnerOrAcceptedMethods, IsAuthor
from .serializers import (AuthorSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeLinkedModelsSerializer,
                          RecipeSerializer, SubscribeListSerializer,
                          TagSerializer, UserCreateSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrAcceptedMethods,
        IsAuthor
    )

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def patch(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeCreateSerializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                status=status.HTTP_201_CREATED,
                data=serializer.data
            )
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data="wrong parameters"
        )

    @action(detail=True, permission_classes=[permissions.IsAuthenticated],
            methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        kwargs = self.do_action_with_model(request, pk, 'cart')
        return Response(**kwargs)

    @action(detail=True, permission_classes=[permissions.IsAuthenticated],
            methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        kwargs = self.do_action_with_model(request, pk, 'favorite')
        return Response(**kwargs)

    def do_action_with_model(self, request, pk: int, model_name: str):
        model = {
            'cart': Cart,
            'favorite': Favorite,
        }.get(model_name)

        if request.method == 'POST':
            recipe = Recipe.objects.filter(pk=pk).first()
            if not recipe:
                kwargs = {'status': status.HTTP_400_BAD_REQUEST}
            else:
                kwargs = self.add_recipe_to_model(request, recipe, model)  # noqa
            return kwargs
        elif request.method == 'DELETE':
            kwargs = self.delete_model_with_recipe(request, pk, model)  # noqa
            return kwargs

    def add_recipe_to_model(self, request, recipe: Recipe, model: Cart | Favorite):
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
        return {'data': serializer.data, 'status': status.HTTP_201_CREATED}

    def delete_model_with_recipe(self, request, pk, model: Cart or Favorite):
        recipe = get_object_or_404(Recipe, pk=pk)
        model_with_recipe = model.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()
        if not model_with_recipe:
            return {'status': status.HTTP_400_BAD_REQUEST}
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
    filterset_class = CustomIngredientsFilter
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

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated, IsAuthor],
            methods=['delete', 'post'])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        if request.method == 'DELETE':
            kwargs = self.delete_subscribe(request, author.pk)
            return Response(**kwargs)

        elif request.method == 'POST':
            kwargs = self.create_subscribe(request, author)
            return Response(**kwargs)

    def create_subscribe(self, request, author: User) -> dict:
        is_subscribed = Subscribe.objects.filter(
            author=author,
            user=request.user,
        ).exists()
        if is_subscribed or (author.pk == request.user.pk):
            return {
                'data': {'error_400': 'Ошибка подписки'},
                'status': status.HTTP_400_BAD_REQUEST,
            }
        new_subscribe = Subscribe.objects.create(
            author=author,
            user=request.user,
        )
        context = super().get_serializer_context()
        serializer = SubscribeListSerializer(new_subscribe, context=context)
        return {'data': serializer.data, 'status': status.HTTP_201_CREATED}

    def delete_subscribe(self, request, author) -> dict:
        subscribe = Subscribe.objects.filter(
            author=author, user=request.user).first()
        if not subscribe:
            return {'status': status.HTTP_400_BAD_REQUEST}

        subscribe.delete()
        return {'status': status.HTTP_204_NO_CONTENT}


class SubscriptionsListSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubscribeListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Subscribe.objects.filter(user=self.request.user)
        return queryset
