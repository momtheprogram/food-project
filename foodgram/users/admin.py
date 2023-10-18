from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('first_name', 'last_name')
    ordering = ('username',)
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class Subscribe(admin.ModelAdmin):
    list_display = (
        'pk', 'user', 'author',
    )
    empty_value_display = '-пусто-'
