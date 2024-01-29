from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'media', StudentFileViewSet, basename='media')
urlpatterns = router.urls

