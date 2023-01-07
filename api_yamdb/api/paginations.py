from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    pass


class Paginator_page_size_2(CustomPagination):
    page_size = 2


class Paginator_page_size_3(CustomPagination):
    page_size = 3


class Paginator_page_size_4(CustomPagination):
    page_size = 4
