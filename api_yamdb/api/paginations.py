from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    pass


class PaginatorPageSize2(CustomPagination):
    page_size = 2


class PaginatorPageSize3(CustomPagination):
    page_size = 3


class PaginatorPageSize4(CustomPagination):
    page_size = 4
