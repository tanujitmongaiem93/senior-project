from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view
from rest_framework.routers import DefaultRouter

from student.views import StudentViewSet, CSVUploadView, ImageUploadView, \
                          PracticeCSVUploadView, FacultyViewSet, PlaceViewSet

schema_view = get_swagger_view(title='Tom API')
router = DefaultRouter()

router.register(r'student', StudentViewSet)
router.register(r'faculty', FacultyViewSet)
router.register(r'place', PlaceViewSet)

urlpatterns = [
    path('upload/practice/<filename>', PracticeCSVUploadView.as_view()),
    path('upload/csv/<filename>', CSVUploadView.as_view()),
    path('upload/student-image/<filename>', ImageUploadView.as_view()),
    path('', schema_view),
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
