
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

from .utils import file_storage_path


class GetOrNoneManager(models.Manager):
    """
    Add get_or_none method to objects
    """
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class CustomUser(AbstractUser):

    SUBSCRIPTIONS = (
        ('FREE', 'FREE'),
        ('PREMIUM', 'PREMIUM')
    )

    subscription = models.CharField(
                    max_length=10,
                    choices=SUBSCRIPTIONS,
                    default='FREE'
                )

    def __str__(self):
        return f' {self.pk}). {self.username} with subscription type {self.subscription}'  # noqa


class Card(models.Model):
    """
    * New card is created at the bottom.
    * Change of position of card\list requires 3 queries.
    """
    name = models.CharField(
                    max_length=20,
                    default='Untitled Card'
                )
    due_date = models.DateTimeField(
                    null=True,
                    blank=True
                )
    attachment = models.FileField(
                    upload_to=file_storage_path,
                )
    list = models.ForeignKey(
                    'List',
                    null=True,
                    on_delete=models.SET_NULL,
                    related_name='card_list'
                )
    next = models.OneToOneField(
                    'self',
                    null=True,
                    unique=True,
                    related_name='_next',
                    on_delete=models.CASCADE
                )

    objects = GetOrNoneManager()

    def __str__(self):
        return f'{self.pk}). {self.name}'

    class Meta:
        ordering = ['pk']


class List(models.Model):

    name = models.CharField(
                    max_length=20,
                    default='Untitled List'
                )
    board = models.ForeignKey(
                    'Board',
                    null=True,
                    related_name='list_board',
                    on_delete=models.SET_NULL
                )

    def __str__(self):
        return f'List {self.name}'


class Board(models.Model):

    name = models.CharField(
                    max_length=20,
                    default='Untitled Board'
                )
    user = models.ForeignKey(
                    'CustomUser',
                    related_name='board_user',
                    null=True,
                    on_delete=models.CASCADE
                )

    def save(self, *args, **kwargs):
        user = self.user
        if (user.board_user.all().count() > 3 and
                self.user.subscription == 'FREE'):
            raise ValidationError('Only 3 boards are allowed for FREE subscription')  # noqa
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} by user {self.user}'
