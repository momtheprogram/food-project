from rest_framework import serializers

from cooking.models import RecipeIngredients, Tag, Recipe, Ingredient
from users.models import Follow, User


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe

    def validate(self, data):
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError({'tags': 'Нужно указать хотя бы один тег'})
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({'tags': 'Теги уже существуют'})
        return data

    def create(self):
        ...  # создать рецепт, теги. ингредиенты

    def update(self):
        ...  # обновить рецепт, теги. ингредиенты


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientsSerializer(many=True, source='recipe_ingredients')
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self):
        ...


class FollowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'time')



class FollowListSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source=)
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields =('id', 'name', 'first_name', 'last_name')

    def get_recipes(self, obj):
        recipes = [] # получить рецепты из БД
        ...
        return FollowRecipeSerializer(recipes, many=True, context=self.context).data

    def get_is_subscribed(self, obj):
        ...

