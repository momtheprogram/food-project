from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model() 


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True,)
    color = models.CharField(max_length=50, unique=True,)
    slug = models.SlugField(max_length=100, unique=True,)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    measurement_unit = models.CharField(max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe', verbose_name='Автор рецепта')
    name = models.CharField(max_length=100, verbose_name='Название')
    image = models.ImageField(null=True, blank=True, upload_to='cooking/media/', verbose_name='Фото блюда')
    text = models.TextField(verbose_name='Рецепт')
    ingredient = models.ManyToManyField(Ingredient, blank=False, through='RecipeIngredients', verbose_name='Ингридиенты')
    tag = models.ManyToManyField(Tag, verbose_name='Тег',)
    time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления', default=15, validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            models.UniqueConstraint(fields=('name', 'author'), name='unique_for_author',),
        )

    def __str__(self):
        return f'{self.name}. {self.author.username}'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,)
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE,)
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Количество ингридиентов'

    def __str__(self):
        return f'{self.amount} {self.ingredient.name}'


class SelectedRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='selected',
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='selected',
    )

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='selected_recipes_user_recipe_unique')]


class ShoppingList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_list',
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_list',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'], name='shopping_list_user_recipe_unique')]
