
from rest_framework import filters
# from django.contrib.auth import user


class IsBoardOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only users to see their own board objects.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)


class IsCardOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only users to see their own card objects.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(list__board__user=request.user)


class IsListOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only users to see their own list objects.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(board__user=request.user)


def file_storage_path(instance, filename):
    # return f'{user.username}/{filename}'
    return 'attachments/'
