import django_filters

from cooking.models import Recipe, Ingredient


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author__id')
    is_favorited = django_filters.CharFilter(
        field_name='is_favorited', method='filter_is_favorited')
    tags = django_filters.CharFilter(field_name='tags', method='filter_tags')
    is_in_shopping_cart = django_filters.CharFilter(
        field_name='is_in_shopping_cart', method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author']

    def filter_is_favorited(self, queryset, name, value):
        if value == 'true':
            queryset = Recipe.objects.filter(
                favorites__recipe__in=queryset.values_list('pk', flat=True),
                favorites__user=self.request.user
            ).all()
        elif value == 'false':
            queryset = Recipe.objects.exclude(
                favorites__recipe__in=queryset.values_list('pk', flat=True),
                favorites__user=self.request.user
            ).all()
        return queryset

    def filter_tags(self, queryset, name, value):
        tags_slug = self.request.query_params.getlist('tags')
        queryset = queryset.filter(tags__slug__in=tags_slug).distinct().all()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 'true':
            queryset = queryset.filter(
                in_cart__recipe__in=queryset.values_list('pk', flat=True),
                in_cart__user=self.request.user
            ).all()
        elif value == 'false':
            queryset = queryset.exclude(
                in_cart__recipe__in=queryset.values_list('pk', flat=True),
                in_cart__user=self.request.user
            ).all()
        return queryset


class CustomIngredientsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
