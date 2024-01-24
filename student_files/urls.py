from rest_framework.routers import DefaultRouter
from .views import StudentFileViewSet

router = DefaultRouter()
router.register(r'student_files', StudentFileViewSet, basename='student_files')
urlpatterns = router.urls

