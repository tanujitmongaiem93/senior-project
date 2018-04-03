from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.views import APIView
from django.db.models import Q

from .models import Information, Faculty, Major, Degree, Practice
from .serializers import StudentSerializer, UpdateStudentSerializer,CheckSerializer, \
                         RunSerializer, RunResponseSerializer, CreateStudentSerializer, \
                         ImageUploadSerializer, RegisterSerializer, SearchSerializer, \
                         FacultySerializer


class PracticeCSVUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, filename):
        import pandas as pd
        file_obj = request.data['file']
        data = pd.read_csv(file_obj, keep_default_na=False)
        for index, row in data.iterrows():
            order = row.order_range.split(' - ')
            Practice.objects.create(
                order_first=int(order[0]),
                order_last=int(order[1]),
                day=row.day if row.day else "-",
                period=row.period if row.period else "-",
                load_place=row.load_place if row.load_place else "-",
                place=row.place if row.place else "-"
            ).save()
        return Response({'name': file_obj.name}, status=status.HTTP_200_OK)


class CSVUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, filename):
        import pandas as pd
        file_obj = request.data['file']
        data = pd.read_csv(file_obj)

        temp_faculty = Faculty.objects.create(name="test")
        temp_major = Major.objects.create(name="test")
        temp_degree = Degree.objects.create(name="test")
        delete_degree = temp_degree
        delete_faculty = temp_faculty
        delete_major = temp_major
        for index, row in data.iterrows():
            if row.faculty not in temp_faculty.name:
                faculty = Faculty.objects.filter(name__icontains=row.faculty).first()
                if not faculty:
                    faculty = Faculty.objects.create(name=row.faculty)
                    faculty.save()
                temp_faculty = faculty

            if row.major not in temp_major.name:
                major = Major.objects.filter(name__icontains=row.major).first()
                if not major:
                    major = Major.objects.create(faculty=faculty, name=row.major)
                    major.save()
                temp_major = major

            if row.degree not in temp_degree.name:
                degree = Degree.objects.filter(name__icontains=row.degree).first()
                if not degree:
                    degree = Degree.objects.create(name=row.degree)
                    degree.save()
                temp_degree = degree

            if not Information.objects.filter(student_id=row.student_id).exists():
                student = Information.objects.create(
                    order=row.order,
                    student_id=row.student_id,
                    name_title=row.name_title,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    degree=temp_degree,
                    faculty=temp_faculty,
                    major=temp_major
                ).save()
            else:
                print('eiei')
        delete_degree.delete()
        delete_faculty.delete()
        delete_major.delete()
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
        'update': CreateStudentSerializer,
        'partial_update': CreateStudentSerializer,
        'check' : CheckSerializer,
        'run' : RunSerializer,
        'register': RegisterSerializer,
        'search': SearchSerializer
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if len(serializer.data['student_id']) < 8:
            return Response({"error": "student id length should be 8"}, status=status.HTTP_400_BAD_REQUEST)

        if Information.objects.filter(student_id=serializer.data["student_id"]).exists():
            return Response({"error": "student is exist"}, status=status.HTTP_400_BAD_REQUEST)

        faculty = Faculty.objects.filter(name__icontains=serializer.data["faculty"]).first()
        if not faculty:
            faculty = Faculty.objects.create(name=serializer.data["faculty"])
            faculty.save()

        major = Major.objects.filter(name__icontains=serializer.data["major"]).first()
        if not major:
            major = Major.objects.create(name=serializer.data["major"])
            major.save()

        degree = Degree.objects.filter(name__icontains=serializer.data["degree"]).first()
        if not degree:
            degree = Degree.objects.create(name=serializer.data["degree"])
            degree.save()

        student = Information.objects.create(
            student_id=serializer.data["student_id"],
            name_title=serializer.data["name_title"],
            first_name=serializer.data["first_name"],
            last_name=serializer.data["last_name"],
            degree=degree,
            faculty=faculty,
            major=major,
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

        faculty = Faculty.objects.filter(name__icontains=serializer.data["faculty"]).first()
        if not faculty:
            faculty = Faculty.objects.create(name=serializer.data["faculty"])
            faculty.save()

        major = Major.objects.filter(name__icontains=serializer.data["major"]).first()
        if not major:
            major = Major.objects.create(name=serializer.data["major"])
            major.save()

        degree = Degree.objects.filter(name__icontains=serializer.data["degree"]).first()
        if not degree:
            degree = Degree.objects.create(name=serializer.data["degree"])
            degree.save()

        student.student_id = serializer.data['student_id']
        student.name_title = serializer.data['name_title']
        student.first_name = serializer.data['first_name']
        student.last_name = serializer.data['last_name']
        student.degree = degree
        student.faculty = faculty
        student.major = major
        student.first_check = serializer.data['first_check']
        student.second_check = serializer.data['second_check']
        student.third_check = serializer.data['third_check']
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
            practice = Practice.objects.filter(
                day=serializer.data['day'],
                period=serializer.data['period'],
                place=serializer.data['place']
            ).first()
            if not practice:
                return Response({'error': 'input สถานที่ ช่วงเวลา หรือ วันซ้อม ผิด'}, status=status.HTTP_400_BAD_REQUEST)

            if not (student.order >= practice.order_first and student.order <= practice.order_last):
                return Response({'error': 'นักศึกษาเข้าซ้อมผิด'}, status=status.HTTP_400_BAD_REQUEST)

            if not student.first_check:
                student.first_check = True
                student.first_stamp = datetime.now()
                student.save()

        elif serializer.data["check"] == 2:
            if not student.second_check:
                student.second_check = True
                student.second_stamp = datetime.now()
                student.save()

        elif serializer.data["check"] == 3:
            if not student.third_check:
                student.third_check = True
                student.third_stamp = datetime.now()
                student.save()

        response = StudentSerializer(student).data
        return Response(response)

    @list_route(methods=["post"], url_path="register")
    def register(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = Information.objects.filter(student_id=serializer.data['student_id'],
                                             # is_active=True
                                             ).first()
        if not student:
            return Response("Student Not Found", status=status.HTTP_404_NOT_FOUND)

        student.is_register = True
        student.save()
        return Response(status=status.HTTP_200_OK)

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

    @list_route(methods=["get"], url_path="first-report")
    def first_report(self, request):
        import os
        import pandas as pd
        from django.conf import settings
        from django.http import HttpResponse

        path = settings.MEDIA_ROOT
        file_name = "สถิติการเข้าซ้อมย่อย.xlsx"

        cell = ["1", "2", "3", "4", "5", "6", "7"]
        first_appear_data = pd.DataFrame(columns=cell)
        first_disappear_data = pd.DataFrame(columns=cell)

        first_appear_data.loc[0] = ["", "", "", "รายชื่อผู้เข้าซ้อมย่อย", "", "", ""]
        first_disappear_data.loc[0] = ["", "", "", "รายชื่อผู้ขาดซ้อมย่อย", "", "", ""]

        degree_list = Degree.objects.all()
        faculty_list = Faculty.objects.all()

        i = 1
        for faculty in faculty_list:
            first_appear_data.loc[i] = [faculty.name, "", "", "", "", "", ""]
            i += 1
            for degree in degree_list:
                first_appear_data.loc[i] = ["", degree.name, "", "", "", "", ""]
                i += 1
                student_list = Information.objects.filter(degree=degree, faculty=faculty, first_check=True, is_active=True)
                for student in student_list:
                    first_appear_data.loc[i] = ["", "", student.student_id, student.name_title, student.first_name, student.last_name, student.major.name]
                    i += 1
                first_appear_data.loc[i] = ["", "", "", "", "", "", ("รวม %s คน" % (len(student_list)))]
                i += 1
                first_appear_data.loc[i] = ["", "", "", "", "", "", ""]
                i += 1

        i = 1
        for faculty in faculty_list:
            first_disappear_data.loc[i] = [faculty.name, "", "", "", "", "", ""]
            i += 1
            for degree in degree_list:
                first_disappear_data.loc[i] = ["", degree.name, "", "", "", "", ""]
                i += 1
                student_list = Information.objects.filter(degree=degree, faculty=faculty, first_check=False, is_active=True)
                for student in student_list:
                    first_disappear_data.loc[i] = ["", "", student.student_id, student.name_title, student.first_name, student.last_name, student.major.name]
                    i += 1
                first_disappear_data.loc[i] = ["", "", "", "", "", "", ("รวม %s คน" % (len(student_list)))]
                i += 1
                first_disappear_data.loc[i] = ["", "", "", "", "", "", ""]
                i += 1

        writer = pd.ExcelWriter(os.path.join(path,file_name), engine='xlsxwriter')
        first_appear_data.to_excel(writer, header=False, index=False, sheet_name='รายชื่อผู้เข้าซ้อมย่อย')
        first_disappear_data.to_excel(writer, header=False, index=False, sheet_name='รายชื่อผู้ขาดซ้อมย่อย')
        writer.save()
        csv = open(os.path.join(path, file_name), 'rb').read()
        response = HttpResponse(csv, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
        return response

    @list_route(methods=["get"], url_path="second-report")
    def second_report(self, request):
        import os
        import pandas as pd
        from django.conf import settings
        from django.http import HttpResponse

        path = settings.MEDIA_ROOT
        file_name = "สถิติการเข้าซ้อมใหญ่.xlsx"

        cell = ["1", "2", "3", "4", "5", "6", "7"]
        appear_data = pd.DataFrame(columns=cell)
        disappear_data = pd.DataFrame(columns=cell)

        second_appear_data.loc[0] = ["", "", "", "รายชื่อผู้เข้าซ้อมใหญ่", "", "", ""]
        second_disappear_data.loc[0] = ["", "", "", "รายชื่อผู้ขาดซ้อมใหญ่", "", "", ""]

        degree_list = Degree.objects.all()
        faculty_list = Faculty.objects.all()

        i = 1
        for faculty in faculty_list:
            second_appear_data.loc[i] = [faculty.name, "", "", "", "", "", ""]
            i += 1
            for degree in degree_list:
                second_appear_data.loc[i] = ["", degree.name, "", "", "", "", ""]
                i += 1
                student_list = Information.objects.filter(degree=degree, faculty=faculty, second_check=True, is_active=True)
                for student in student_list:
                    second_appear_data.loc[i] = ["", "", student.student_id, student.name_title, student.first_name, student.last_name, student.major.name]
                    i += 1
                second_appear_data.loc[i] = ["", "", "", "", "", "", ("รวม %s คน" % (len(student_list)))]
                i += 1
                second_appear_data.loc[i] = ["", "", "", "", "", "", ""]
                i += 1

        i = 1
        for faculty in faculty_list:
            second_disappear_data.loc[i] = [faculty.name, "", "", "", "", "", ""]
            i += 1
            for degree in degree_list:
                second_disappear_data.loc[i] = ["", degree.name, "", "", "", "", ""]
                i += 1
                student_list = Information.objects.filter(degree=degree, faculty=faculty, second_check=False, is_active=True)
                for student in student_list:
                    second_disappear_data.loc[i] = ["", "", student.student_id, student.name_title, student.first_name, student.last_name, student.major.name]
                    i += 1
                second_disappear_data.loc[i] = ["", "", "", "", "", "", ("รวม %s คน" % (len(student_list)))]
                i += 1
                second_disappear_data.loc[i] = ["", "", "", "", "", "", ""]
                i += 1

        writer = pd.ExcelWriter(os.path.join(path,file_name), engine='xlsxwriter')
        second_appear_data.to_excel(writer, header=False, index=False, sheet_name='รายชื่อผู้เข้าซ้อมใหญ่')
        second_disappear_data.to_excel(writer, header=False, index=False, sheet_name='รายชื่อผู้ขาดซ้อมใหญ่')
        writer.save()
        csv = open(os.path.join(path, file_name), 'rb').read()
        response = HttpResponse(csv, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
        return response

    @list_route(methods=["get"], url_path="third-report")
    def third_report(self, request):
        import os
        import pandas as pd
        from django.conf import settings
        from django.http import HttpResponse

        path = settings.MEDIA_ROOT
        file_name = "สถิติการเข้าร่วมพิธี.xlsx"

        cell = ["1", "2", "3", "4", "5", "6", "7"]
        third_appear_data = pd.DataFrame(columns=cell)
        third_disappear_data = pd.DataFrame(columns=cell)

        third_appear_data.loc[0] = ["", "", "", "รายชื่อผู้เข้าร่วมพิธี", "", "", ""]
        third_disappear_data.loc[0] = ["", "", "", "รายชื่อผู้ไม่เข้าร่วมพิธี", "", "", ""]

        degree_list = Degree.objects.all()
        faculty_list = Faculty.objects.all()

        i = 1
        for faculty in faculty_list:
            third_appear_data.loc[i] = [faculty.name, "", "", "", "", "", ""]
            i += 1
            for degree in degree_list:
                third_appear_data.loc[i] = ["", degree.name, "", "", "", "", ""]
                i += 1
                student_list = Information.objects.filter(degree=degree, faculty=faculty, third_check=True, is_active=True)
                for student in student_list:
                    third_appear_data.loc[i] = ["", "", student.student_id, student.name_title, student.first_name, student.last_name, student.major.name]
                    i += 1
                third_appear_data.loc[i] = ["", "", "", "", "", "", ("รวม %s คน" % (len(student_list)))]
                i += 1
                third_appear_data.loc[i] = ["", "", "", "", "", "", ""]
                i += 1

        i = 1
        for faculty in faculty_list:
            third_disappear_data.loc[i] = [faculty.name, "", "", "", "", "", ""]
            i += 1
            for degree in degree_list:
                third_disappear_data.loc[i] = ["", degree.name, "", "", "", "", ""]
                i += 1
                student_list = Information.objects.filter(degree=degree, faculty=faculty, third_check=False, is_active=True)
                for student in student_list:
                    third_disappear_data.loc[i] = ["", "", student.student_id, student.name_title, student.first_name, student.last_name, student.major.name]
                    i += 1
                third_disappear_data.loc[i] = ["", "", "", "", "", "", ("รวม %s คน" % (len(student_list)))]
                i += 1
                third_disappear_data.loc[i] = ["", "", "", "", "", "", ""]
                i += 1


        writer = pd.ExcelWriter(os.path.join(path,file_name), engine='xlsxwriter')
        third_appear_data.to_excel(writer, header=False, index=False, sheet_name='รายชื่อผู้เข้าร่วมพิธี')
        third_disappear_data.to_excel(writer, header=False, index=False, sheet_name='รายชื่อผู้ไม่เข้าร่วมพิธี')
        writer.save()
        csv = open(os.path.join(path, file_name), 'rb').read()
        response = HttpResponse(csv, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
        return response

    @list_route(methods=["post"],url_path="search")
    def search(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inputs = serializer.data['search']
        first_check = serializer.data['first_check']
        second_check = serializer.data['second_check']
        third_check = serializer.data['third_check']
        search = inputs.split()

        student_list = Information.objects.all()

        if first_check == "1":
            student_list = student_list.filter(first_check=True)
        elif first_check == "2":
            student_list = student_list.filter(first_check=False)

        if second_check == "1":
            student_list = student_list.filter(second_check=True)
        elif second_check == "2":
            student_list = student_list.filter(second_check=False)

        if third_check == "1":
            student_list = student_list.filter(third_check=True)
        elif third_check == "2":
            student_list = student_list.filter(third_check=False)

        if search:
            for word in search:
                student_search = Information.objects.filter(
                    Q(student_id__contains=word) | Q(first_name__contains=word) | Q(last_name__contains=word) | \
                    Q(degree__name__contains=word) | Q(faculty__name__contains=word) | Q(major__name__contains=word)
                )
                student_list = student_list & student_search

        response = StudentSerializer(student_list, many=True).data
        return Response(response)

    @list_route(methods=["get"],url_path="delete-all")
    def delete_all(self, request):
        import os
        for student in Information.objects.all():
            student.image.delete(save=True)
            student.delete()
        for faculty in Faculty.objects.all():
            faculty.delete()
        for major in Major.objects.all():
            major.delete()
        for degree in Degree.objects.all():
            degree.delete()
        for practice in Practice.objects.all():
            practice.delete()
        try:
            os.remove(os.path.join(os.getcwd(), "media"), dir_fd=None)
        except:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

class FacultyViewSet(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Faculty.objects.all()

    action_serializers = {
        'list': FacultySerializer,
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()


class PlaceViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = Practice.objects.all()

    def list(self, request):
        response = [
            {'key': 'place', 'result': set()},
            {'key': 'day', 'result': set()},
            {'key': 'period', 'result': set()},
        ]
        for practice in Practice.objects.all():
            response[0]['result'].add(practice.place)
            response[1]['result'].add(practice.day)
            if practice.period != "-":
                response[2]['result'].add(practice.period)
        return Response(response)
