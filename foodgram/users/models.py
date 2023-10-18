from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(max_length=254, blank=False, null=False, unique=True)
    username = models.CharField(max_length=150, blank=True, unique=True)
    password = models.CharField(verbose_name='Пароль', null=False, blank=False, max_length=150)
    first_name = models.CharField(verbose_name='Имя', max_length=150, null=False, blank=False)
    last_name = models.CharField(verbose_name='Фамилия', max_length=150, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField('Персонал сайта', default=False)

    objects = UserManager()

    class Meta:
        ordering = ['pk']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscribe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', verbose_name='Автор')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower', verbose_name='Подписчик')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['author', 'user'], name='author_follower')]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Пользователь {self.user.username} подписан на {self.author.username}'
