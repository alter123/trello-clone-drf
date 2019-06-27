
from contextlib import suppress

from rest_framework import serializers
from .models import CustomUser, Board, Card, List


class CardSerializer(serializers.HyperlinkedModelSerializer):
    attachment = serializers.FileField(
                                required=False,
                                max_length=None,
                                allow_empty_file=True,
                            )

    class Meta:
        model = Card
        fields = ('__all__')
        read_only_fields = ('next',)

    def create(self, validated_data):
        validated_data.pop('next', None)
        with suppress(Card.DoesNotExist):
            card = Card.objects.get(
                            list=validated_data['list'],
                            next=None
                        )
        instance = Card.objects.create(
                        **validated_data,
                    )
        if 'card' in locals():
            card.next = instance
            card.save()
        return instance


class ListSerializer(serializers.HyperlinkedModelSerializer):
    cards = CardSerializer(source='card_list', many=True, read_only=True)

    class Meta:
        model = List
        fields = ('url', 'name', 'board', 'cards')


class BoardSerializer(serializers.HyperlinkedModelSerializer):
    lists = ListSerializer(source='list_board', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ('url', 'name', 'lists')


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('username', 'subscription', 'email', 'password')


class CardSwapDemoSerializer(serializers.Serializer):
    # authenticate the user.
    token = serializers.CharField(max_length=64)

    card = serializers.IntegerField()
    # Mode card to different position.
    to_pos = serializers.IntegerField()
    # Move card to different list.
    to_list = serializers.IntegerField()

    def create(self, validated_data):
        print(validated_data)
        return True
