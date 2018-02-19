from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view
from rest_framework.routers import DefaultRouter

from student.views import StudentViewSet

schema_view = get_swagger_view(title='Tom API')
router = DefaultRouter()

router.register(r'student', StudentViewSet)

urlpatterns = [
    path('', schema_view),
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
