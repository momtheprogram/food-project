from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, )
    color = models.CharField(max_length=50, unique=True, )
    slug = models.SlugField(max_length=100, unique=True, db_index=True)

    class Meta:
        ordering = ['pk']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.pk}, {self.name[:50]}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=100, verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ['pk']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'], name='unique ingredient'
        )]

    def __str__(self):
        return self.name[:30]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        db_index=True,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(max_length=200, verbose_name='Название блюда')
    image = models.ImageField(
        upload_to='recipes/images', verbose_name='Фото блюда'
    )
    text = models.TextField(verbose_name='Рецепт')
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through='IngredientQuantity',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Тег', )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)]
    )
    carts = models.ManyToManyField(
        User, through='Cart', related_name='recipes_in_cart'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
        )

    def __str__(self):
        return f'{self.name}. {self.author.username}'

    @admin.display(description='Добавили в избранное')
    def in_favorite_count(self):
        return self.favorites.count()


class IngredientQuantity(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество инргредиентов в рецепте'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient'
        )]

    def __str__(self):
        return f'{self.ingredient.name}: {self.amount}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ['pk']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='favorites_recipes_user_recipe_unique'
        )]


class Cart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_cart',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customers',
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ['pk']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_list_user_recipe_unique'
            )
        ]

    def __str__(self):
        return f'{self.pk}'
