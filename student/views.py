from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.views import APIView

from .models import Information
from .serializers import StudentSerializer, UpdateStudentSerializer,CheckSerializer, \
                         RunSerializer, RunResponseSerializer, CreateStudentSerializer, ImageUploadSerializer


class CSVUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, filename, format='csv'):
        import pandas as pd
        file_obj = request.data['file']
        data = pd.read_csv(file_obj)
        for index, row in data.iterrows():
            if not Information.objects.filter(student_id=row.student_id).exists():
                student = Information.objects.create(
                    student_id=row.student_id,
                    name_title=row.name_title,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    faculty=row.faculty,
                    major=row.major
                ).save()
            else:
                print('eiei')
        return Response({'name': file_obj.name}, status=status.HTTP_200_OK)


class ImageUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, filename, format='jpg'):
        file_obj = request.data['file']
        print(filename.split(".")[0])
        student = Information.objects.filter(student_id=filename.split(".")[0]).first()
        if not student:
            return Response({"error": "Student Not found."}, status=status.HTTP_404_NOT_FOUND)
        student.image = file_obj
        student.save()
        return Response(status=status.HTTP_200_OK)


class StudentViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    queryset = Information.objects.filter(is_active=True)
    # serializer_class = StudentSerializer

    action_serializers = {
        'create': CreateStudentSerializer,
        'list': StudentSerializer,
        'update': UpdateStudentSerializer,
        'partial_update': UpdateStudentSerializer,
        'check' : CheckSerializer,
        'run' : RunSerializer
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Information.objects.filter(student_id=serializer.data["student_id"]).exists():
            return Response({"error": "student is exist"}, status=status.HTTP_400_BAD_REQUEST)
        student = Information.objects.create(
            student_id=serializer.data["student_id"],
            name_title=serializer.data["name_title"],
            first_name=serializer.data["first_name"],
            last_name=serializer.data["last_name"],
            faculty=serializer.data["faculty"],
            major=serializer.data["major"],
            first_check=serializer.data["first_check"],
            second_check=serializer.data["second_check"],
            third_check=serializer.data["third_check"]
        )
        student.save()
        return Response(status=status.HTTP_200_OK)


    def partial_update(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if len(serializer.data['student_id']) < 8:
            return Response({"error": "student id length should be 8"}, status=status.HTTP_400_BAD_REQUEST)

        student = Information.objects.filter(id=pk,is_active=True).first()
        if not student:
            return Response({"error": "Student Not found."}, status=status.HTTP_404_NOT_FOUND)

        check = Information.objects.filter(student_id=serializer.data['student_id'],is_active=True)
        for stud in check:
            if stud.id != student.id:
                return Response({"error": "student id has repeat"}, status=status.HTTP_400_BAD_REQUEST)

        student.student_id = serializer.data['student_id']
        student.name_title = serializer.data['name_title']
        student.first_name = serializer.data['first_name']
        student.last_name = serializer.data['last_name']
        student.faculty = serializer.data['faculty']
        student.major = serializer.data['major']
        student.save()
        return Response(status=status.HTTP_200_OK)

    @list_route(methods=["post"],url_path="check")
    def check(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = Information.objects.filter(student_id=serializer.data["student_id"],is_active=True).first()
        if not student:
            return Response("Student Not Found", status=status.HTTP_404_NOT_FOUND)

        from datetime import datetime
        if serializer.data["check"] == 1:
            if not student.first_check:
                student.first_check = True
                student.first_stamp = datetime.now()
        elif serializer.data["check"] == 2:
            if not student.second_check:
                student.second_check = True
                student.second_stamp = datetime.now()
        elif serializer.data["check"] == 3:
            if not student.third_check:
                student.third_check = True
                student.third_stamp = datetime.now()

        student.save()
        response = StudentSerializer(student).data
        return Response(response)

    @detail_route(methods=["get"], url_path="delete")
    def delete(self, request, pk=None):
        student = Information.objects.filter(id=pk,is_active=True).first()
        if not student:
            return Response("Student Not Found", status=status.HTTP_404_NOT_FOUND)

        student.is_active = False
        student.save()
        return Response(status=status.HTTP_200_OK)

    @list_route(methods=["get"],url_path="count_all_check")
    def count_all_check(self,request):
        student_list = Information.objects.filter(first_check=True,second_check=True,third_check=True,is_active=True)
        return Response({"all_student":student_list.count(),
                         "first_student_id": student_list.first().student_id})

    @list_route(methods=["get"],url_path="eiei")
    def eiei(self,request):
        for student in Information.objects.all():
            student.first_check = True
            student.second_check = True
            student.third_check = True
            student.save()
        return Response({})

    @list_route(methods=["post"],url_path="run")
    def run(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = Information.objects.filter(student_id=serializer.data["student_id"],is_active=True).first()
        if not student:
            return Response("Student Not Found", status=status.HTTP_404_NOT_FOUND)
        next_student = False
        count = 1
        while not next_student:
            next_student = Information.objects.filter(student_id=str(int(student.student_id)+count),
                                                      first_check=True,
                                                      second_check=True,
                                                      third_check=True,is_active=True).first()
            count+=1

        response = RunResponseSerializer(student).data
        response.update({
            "next" : {
                "student_id" : next_student.student_id,
                "name_title" : next_student.name_title,
                "first_name" : next_student.first_name,
                "last_name" : next_student.last_name
            }
        })
        return Response(response)

    @list_route(methods=["get"], url_path="report")
    def report(self, request):
        import os
        import pandas as pd
        from django.conf import settings
        from django.http import HttpResponse

        path = settings.MEDIA_ROOT
        file_name = "report.xlsx"
        for root, dirs, files in os.walk(path):
            if file_name in files:
                try:
                    os.remove(os.path.join(path, file_name), dir_fd=None)
                except:
                    pass

        data = pd.DataFrame(columns=["ทอม", "ดิว"])
        writer = pd.ExcelWriter(os.path.join(path,file_name), engine='xlsxwriter')
        data.to_excel(os.path.join(path,file_name), sheet_name='report')
        writer.save()
        csv = open(os.path.join(path, file_name), 'rb').read()
        response = HttpResponse(csv, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=report.xlsx'
        return response
