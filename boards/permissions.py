
from enum import Enum
from rest_framework.permissions import BasePermission
from .models import Card, Board, List


class IsAllowedToAccess(BasePermission):
    """
    Can be only accessed by user belonging
    to a particular card/list/board.
    """
    def has_object_permission(self, request, view, obj):

        if isinstance(obj, Card):
            return (request.user == obj.list.board.user)
        elif isinstance(obj, List):
            return (request.user == obj.board.user)
        elif isinstance(obj, Board):
            return (request.user == obj.user)
        else:
            return False
