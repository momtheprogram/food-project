from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(unique=True, max_length=200)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
     follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')

     class Meta:
         constraints = [models.UniqueConstraint(fields=['author', 'follower'], name='author_follower')]
         verbose_name = 'Подписка'
         verbose_name_plural = 'Подписки'
