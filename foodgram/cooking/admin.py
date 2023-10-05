from django.contrib import admin

from .models import Recipe, Ingredient, Tag, ShoppingList, SelectedRecipes


class PostAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('name', 'author', 'image')
    # Добавляем интерфейс для поиска
    search_fields = ('name', 'tag', 'author')
    # Добавляем возможность фильтрации по дате
    list_filter = ('name',) 


admin.site.register(Recipe, PostAdmin)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(ShoppingList)
admin.site.register(SelectedRecipes)
