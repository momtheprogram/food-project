from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueValidator

from cooking.models import (Cart, Favorite, Ingredient, IngredientQuantity,
                            Recipe, Tag)
from users.models import Subscribe, User


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj) -> bool:
        subscribe = Subscribe.objects.filter(
            user=self.context['request'].user.id,
            author=obj,
        ).exists()
        return subscribe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', required=False
    )
    id = serializers.IntegerField(
        source='ingredient.id', required=True
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = IngredientQuantity
        fields = ('id', 'amount', 'name', 'measurement_unit',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True, allow_null=False
    )
    ingredients = IngredientRecipeSerializer(
        source='ingredientquantity_set',
        many=True,
        required=True,
        write_only=True
    )
    image = Base64ImageField(required=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=False,
        queryset=User.objects.all(),
        default=CurrentUserDefault()
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',)

    def create(self, validated_data):
        tags_list = validated_data.pop('tags')
        ingredients_list = validated_data.pop('ingredientquantity_set')
        new_recipe = Recipe.objects.create(
            author=validated_data.pop('author'),
            name=validated_data.pop('name'),
            image=validated_data.pop('image'),
            text=validated_data.pop('text'),
            cooking_time=validated_data.pop('cooking_time'),
        )
        new_recipe.tags.set(tags_list)
        new_recipe.save()
        new_recipe = self.add_ingredients(new_recipe, ingredients_list)

        return new_recipe

    def validate(self, attrs):
        ingredients = attrs.get('ingredientquantity_set', [])
        tags = attrs.get('tags', [])
        cooking_time = attrs.get('cooking_time')
        image = attrs.get('image')
        self.__validate_ingredients(ingredients)
        self.__validate_tags(tags)
        self.__validate_cooking_time(cooking_time)
        self.__validate_image(image)

        return attrs

    def update(self, instance, validated_data):
        tags_list = validated_data.pop('tags')
        ingredients_list = validated_data.get('ingredientquantity_set', )
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.pop('text', instance.text)
        instance.cooking_time = validated_data.pop(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        instance.tags.clear()
        instance.tags.set(tags_list)
        instance.save()
        instance = self.add_ingredients(instance, ingredients_list, True)
        instance.save()
        return instance

    def add_ingredients(
            self, recipe, ingredients: list or tuple,
            clear_ingredients: bool = False
    ):
        if clear_ingredients:
            recipe.ingredients.clear()

        recipe.save()

        for ingredient in ingredients:
            ingredient_description = get_object_or_404(
                Ingredient, id=ingredient['ingredient']['id']
            )
            ingredient_quantity, created = (
                IngredientQuantity.objects.get_or_create(
                    ingredient=ingredient_description,
                    defaults={'amount': abs(ingredient['amount'])},
                    recipe=recipe,
                )
            )
            if not created:
                ingredient_quantity.amount += abs(ingredient['amount'])
                ingredient_quantity.save()
        recipe.save()
        return recipe

    def __validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Картинка не должна быть пустой!')
        return value

    def __validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Время готовки не может быть отрицательным')
        return value

    def __validate_tags(self, value):
        if value is None or len(value) <= 0:
            raise serializers.ValidationError(
                'Не добавлено ни одного тега')
        self.unique_validator(value)

        return value

    def __validate_ingredients(self, value):
        """One item in for cycle is:

        OrderedDict([('ingredient', {'id': 22222, 'name':
        'абрикосовое пюре', 'measurement_unit': 'г'}),
        ('amount', 1)])
        """
        count_ingredients = len(value)
        if value is None or count_ingredients <= 0:
            raise serializers.ValidationError(
                'Не добавлено ни одного ингредиента.')

        unique_ingredients = set()
        for item in value:

            if item['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество в ингредиенте не может быть отрицательным.')
            ingredient = item['ingredient']

            id_ = ingredient.get('id')
            ingredient_entity = Ingredient.objects.filter(
                pk=id_,
            )
            if not ingredient_entity.exists():
                raise serializers.ValidationError(
                    'Нет такого ингредиента!')
            unique_ingredients.add(id_)

        if len(unique_ingredients) != count_ingredients:
            raise serializers.ValidationError(
                'Не уникальные ингредиенты!')
        return value

    def unique_validator(self, value) -> bool:
        len_set_values = len(set(value))
        if len_set_values != len(value):
            raise serializers.ValidationError(
                'Неуникальные значения в поле.')
        return True

    def to_representation(self, instance):
        """Для приведения ответа к виду в соответствии с api."""
        return RecipeSerializer(instance, context=self.context).data


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        source='ingredientquantity_set', many=True, required=True
    )
    image = Base64ImageField()
    author = AuthorSerializer(default=CurrentUserDefault())
    tags = TagSerializer(many=True, required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time',)

    def get_is_favorited(self, obj):
        is_favorited = Favorite.objects.filter(
            user=self.context['request'].user.id,
            recipe=obj.id,
        ).exists()
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        is_in_shopping_cart = Cart.objects.filter(
            user=self.context['request'].user.id,
            recipe=obj.id,
        ).exists()
        return is_in_shopping_cart


class RecipeLinkedModelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        ordering = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password',
        )
        model = User
        extra_kwargs = {
            'email': {'required': True,
                      'validators': [
                          UniqueValidator(queryset=User.objects.all())
                      ]
                      },
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True, 'write_only': True},
        }

    def create(self, validated_data) -> User:
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")
        return user

    def perform_create(self, validated_data) -> User:
        with transaction.atomic():
            user = User.objects.create_user(
                is_active=True, **validated_data)
        return user


class SubscribeListSerializer(serializers.Serializer):  # noqa
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField('get_recipes', read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj) -> int:
        return obj.author.recipes.count()

    def get_is_subscribed(self, obj) -> bool:
        subscribe = Subscribe.objects.filter(
            author=obj.author,
            user=self.context['request'].user,
        ).exists()
        return subscribe

    def get_recipes(self, obj) -> dict:
        recipes_limit = (
            self.context['view'].request.query_params.get('recipes_limit')
            if self.context else None
        )
        recipes = (obj.author.recipes.all()[:int(recipes_limit)]
                   if recipes_limit
                   else obj.author.recipes.all())
        serializer = RecipeLinkedModelsSerializer(instance=recipes, many=True)
        return serializer.data
