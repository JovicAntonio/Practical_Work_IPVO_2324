from rest_framework.routers import DefaultRouter
from .views import StudentFileViewSet

router = DefaultRouter()
router.register(r'media', StudentFileViewSet, basename='media')
urlpatterns = router.urls

