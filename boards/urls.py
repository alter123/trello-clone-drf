
from django.urls import include, path

from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.documentation import include_docs_urls

from .views import (BoardViewSet, CardSwipeDemo, CardViewSet,
                    UserViewSet, ListViewSet)

API_TITLE = 'Trello Clone'
API_DESCRIPTION = 'Trello Clone Backend using DRF'


router = routers.DefaultRouter()
router.register(r'board', BoardViewSet)
router.register(r'list', ListViewSet)
router.register(r'card', CardViewSet)
router.register(r'user', UserViewSet)

urlpatterns = [
    path('swap-demo/', CardSwipeDemo.as_view(), name='card_swap_demo'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api-auth/', include('rest_framework.urls', )),
    path('docs/', include_docs_urls(
                        title=API_TITLE,
                        description=API_DESCRIPTION
                    ))

] + router.urls
