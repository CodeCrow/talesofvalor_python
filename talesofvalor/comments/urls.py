"""Router for views for events."""
from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import CommentViewSet

app_name = 'comments'

router = DefaultRouter()
router.register(r'', CommentViewSet)


urlpatterns = router.urls
