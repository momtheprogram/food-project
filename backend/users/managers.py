from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **kwargs):
        if username is None:
            raise TypeError('Заполните поле "username"')
        if email is None:
            raise TypeError('Заполните поле "email"')

        user = self.model(
            username=username, email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password, **kwargs):
        if password is None:
            raise TypeError('Суперпользователь должен иметь пароль!')

        user = self.create_user(username, email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
