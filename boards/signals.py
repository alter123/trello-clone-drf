
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import CustomUser, Board


@receiver(pre_save, sender=CustomUser)
def set_user_password(instance, **kwargs):
    password = instance.password
    instance.set_password(password)
    return instance


@receiver(pre_save, sender=Board)
def create_new_board(instance, **kwargs):
    """
    Creates Validation error when a 'FREE' tier user
    tries to create more than '3' boards.

    Currently been overrided in APIView.

    """
    pass
    # user_board_count = CustomUser.objects.get( 
    #                         pk = str(instance).split(').')[0].split()[-1] 
    #                     ).board_user.all().count()
    # user_subscription = CustomUser.objects.get( 
    #                         pk = str(instance).split(').')[0].split()[-1] 
    #                     ).subscription
    # if user_board_count > 2 and user_subscription == 'FREE' :
    #     raise ValidationError('Max boards in free tier reached')
