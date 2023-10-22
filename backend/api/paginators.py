from rest_framework.pagination import PageNumberPagination

from foodgram.constants import MAX_PAGE_SIZE, LIMIT, PAGE_SIZE


class CustomPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = LIMIT
    max_page_size = MAX_PAGE_SIZE
