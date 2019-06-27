
import traceback
from collections import defaultdict
from contextlib import suppress

from django.http import JsonResponse
from django.shortcuts import render

from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Board, Card, CustomUser, List
from .permissions import IsAllowedToAccess
from .serializers import (BoardSerializer, CardSerializer, ListSerializer,
                          UserSerializer)
from .utils import (IsBoardOwnerFilterBackend, IsCardOwnerFilterBackend,
                    IsListOwnerFilterBackend)


class CardViewSet(viewsets.ModelViewSet):

    queryset = Card.objects.all()
    serializer_class = CardSerializer
    filter_backends = (IsCardOwnerFilterBackend, )
    permission_classes = (IsAllowedToAccess, )  # noqa

    def destroy(self, *args, pk=None):
        card = Card.objects.get(pk=pk)
        prev = Card.objects.filter(next=card)
        if len(prev) == 1:
            # Otherwise card is first in stack
            prev[0].next = card.next or None
            # Maintain Unique Constraint
            card.next = None
            card.save()
            prev[0].save()
        self.perform_destroy(card)  # destruction XD
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListViewSet(viewsets.ModelViewSet):

    queryset = List.objects.all()
    serializer_class = ListSerializer
    filter_backends = (IsListOwnerFilterBackend, )
    permission_classes = (IsAllowedToAccess, )  # noqa


class BoardViewSet(viewsets.ModelViewSet):

    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    filter_backends = (IsBoardOwnerFilterBackend, )
    permission_classes = (IsAllowedToAccess, )  # noqa

    def create(self, request):
        """
        Only allow three boards for a FREE user.
        """
        if not (Board.objects.filter(user=request.user).count() > 2 and
                request.user.subscription == 'FREE'):
            instance = BoardSerializer(data=request.data)
            if instance.is_valid():
                board = Board.objects.create(
                                user=request.user,
                                **instance.validated_data
                            )
                if board:
                    return Response(
                                instance.validated_data,
                                status=status.HTTP_201_CREATED
                            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class CardSwipeDemo(APIView):
    """
    Handles card view template.
    """

    _response = lambda self, msg, res: JsonResponse({  # noqa
                        'message': msg,
                        'response': res
                    })

    def get(self, request):
        return render(
            request, 'boards/demo.html', {
                'token': Token.objects.get(user=request.user)
            })

    def post(self, request):
        data = request.data
        if (
            not data.get('operation', None) or
            not data.get('card', None) or
            not data.get('pos', None)
        ):
            return self._response('Invalid Params', 'Failed')

        try:
            card_id, pos_id = int(data['card']), int(data['pos'])

            if card_id == 0:
                return self._response('Card Id cannot be 0', 'Failed')

            _card = Card.objects.get(pk=card_id)
            cards = List.objects.filter(
                                board__user=request.user,
                                pk=_card.list.pk
                            ).values(
                                'card_list',
                                'card_list__next',
                                'pk'
                            )

            if data.get('operation') == 'swap' and cards.count() >= 1:
                # Check if both cards are in same list.
                if (pos_id and card_id) not in \
                        [card['card_list'] for card in cards]+[0]:
                    return self._response('Invalid Params 1', 'Failed')

                _card = next(filter(
                        lambda x: x['card_list'] == card_id,
                        cards
                    ))
                _prev = Card.objects.filter(next=_card['card_list']).first()

                if _prev:
                    _prev.next = None
                    _prev.save()

                if pos_id != 0:
                    """
                    Case: Move _card to next of _pos.
                    _prev.next = _card
                    _pos.next = x

                    Operation:
                        _prev.next = _card.next
                        _pos.next = _card
                        _card.next = x
                    """
                    _pos = next(filter(
                            lambda x: x['card_list'] == pos_id,
                            cards
                        ))
                    Card.objects.filter(
                                pk=_pos['card_list']
                            ).update(next=_card['card_list'])
                    Card.objects.filter(
                                pk=_card['card_list']
                            ).update(next=_pos['card_list__next'] or None)

                else:
                    id = set(
                            (card['card_list'] for card in cards)
                        ).symmetric_difference(
                            (card['card_list__next'] for card in cards)
                        )
                    # id = { id, None }
                    id = next(filter(None.__ne__, id))
                    Card.objects.filter(
                                pk=_card['card_list']
                            ).update(next=id)

                if _prev and _card['card_list__next']:
                    _prev.next = Card.objects.get(
                                        pk=_card['card_list__next']
                                    )
                    _prev.save()
                return self._response('Success', 'Success')

            elif data.get('operation') == 'swapList' and pos_id != 0:
                _board = Card.objects.filter(
                                    pk=card_id
                                ).values_list(
                                    'list__board__pk', flat=True
                                )
                if not _board.exists():
                    return self._response('Invalid Card id.1', 'Failed')
                
                cards = Board.objects.filter(
                    pk=_board[0]
                ).values(
                    'list_board',
                    'list_board__card_list',
                    'list_board__card_list__next'
                )

                if card_id not in (card['list_board__card_list']
                    for card in cards) and pos_id not in \
                        (list['list_board'] for list in cards):
                    return self._response('Invalid Params 1', 'Failed')

                _card = next(filter(
                        lambda x: x['list_board__card_list'] == card_id,
                        cards
                    ))
                with suppress(StopIteration):
                    _prev = next(filter(
                            lambda x: x['list_board__card_list__next'] == card_id,
                            cards
                        ))
                with suppress(StopIteration):
                    _new_pos = next(filter(
                            lambda x: not x['list_board__card_list__next'],
                                filter(
                                    lambda x: x['list_board'] == pos_id,
                                cards
                            )))

                Card.objects.filter(pk=card_id).update(
                                                list=pos_id,
                                                next=None
                                            )
                if '_prev' in locals():
                    Card.objects.filter(
                        pk=_prev['list_board__card_list']
                    ).update(
                        next=_card['list_board__card_list__next'] or None
                    )

                if '_new_pos' in locals():  # len(new_list) > 0
                    Card.objects.filter(
                        pk=_new_pos['list_board__card_list']
                    ).update(
                        next=Card.objects.get(pk=card_id)
                    )

                return self._response('Success', 'Success')
            else:
                return self._response('Invalid Params 2', 'Failed')

        except Exception as err:
            traceback.print_exc(err)
            # traceback.print_tb(err.__traceback__)
            return self._response('Internal error', 'Failed')
