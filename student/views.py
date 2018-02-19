from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from .models import Information,Attendance
from .serializers import StudentSerializer

class StudentViewSet(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Information.objects.filter(is_active=True)
    serializer_class = StudentSerializer

    def list(self,request):
        student_list = Information.objects.filter(is_active=True)[:10]
        response = StudentSerializer(student_list, many=True)
        return Response(response.data)

    @list_route(methods=['get'], url_path="kuy")
    def kuy():
        return Response({"kuy": "kuy"})
