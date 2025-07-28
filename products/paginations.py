from rest_framework.pagination import CursorPagination

class CustomCursorPagination(CursorPagination):
    page_size = 7  # how many items per page
    ordering = '-id'  # MUST be unique + ordered


