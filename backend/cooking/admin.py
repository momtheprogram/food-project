from django.contrib import admin

from .models import Cart, Favorite, Ingredient, IngredientQuantity, Recipe, Tag


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    empty_value_display = '-пусто-'


@admin.register(IngredientQuantity)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'in_favorite_count',
    )
    empty_value_display = '-пусто-'
    search_fields = ('name', 'author__username', 'tags',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    empty_value_display = '-пусто-'
    search_fields = ('name',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user',)
    empty_value_display = '-пусто-'
