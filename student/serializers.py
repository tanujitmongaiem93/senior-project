from rest_framework import serializers

from .models import Information, Practice, Faculty, Major


class FacultySerializer(serializers.ModelSerializer):
    faculty = serializers.SerializerMethodField()
    major = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = ('faculty', 'major')

    def get_faculty(self, faculty):
        return faculty.name

    def get_major(self, faculty):
        response = []
        for major in Major.objects.filter(faculty=faculty):
            response.append(major.name)
        return response



class SearchSerializer(serializers.Serializer):

    search = serializers.CharField(required=True, allow_blank=True)
    first_check = serializers.CharField()
    second_check = serializers.CharField()
    third_check = serializers.CharField()


class CheckSerializer(serializers.Serializer):

    student_id = serializers.CharField(required=True)
    check = serializers.IntegerField(required=True)
    day = serializers.CharField(required=True)
    period = serializers.CharField(required=True)
    place = serializers.CharField(required=True)


class RegisterSerializer(serializers.Serializer):

    student_id = serializers.CharField(required=True)


class ImageUploadSerializer(serializers.Serializer):

    student_id = serializers.CharField(required=True)
    image = serializers.ImageField(max_length=None, allow_empty_file=False)


class StudentSerializer(serializers.ModelSerializer):
    degree = serializers.SerializerMethodField()
    faculty = serializers.SerializerMethodField()
    major = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Information
        fields = ('order', 'student_id', 'name_title', 'first_name', 'last_name',
                  'degree','faculty', 'major', 'image','id', 'first_check',
                  'second_check', 'third_check')

    def to_representation(self, student):
        data = super(StudentSerializer, self).to_representation(student)
        for practice in Practice.objects.all():
            if student.order >= practice.order_first and student.order <= practice.order_last:
                data.update({
                    'day': practice.day,
                    'period': practice.period,
                    'load_place': practice.load_place,
                    'place': practice.place
                })
                return data

        data.update({
            'day': "",
            'period': "",
            'load_place': "",
            'place': ""
        })
        return data

    def get_image(self, student):
        return student.image.url if student.image else ""

    def get_degree(self, student):
        return student.degree.name if student.degree else "-"

    def get_faculty(self, student):
        return student.faculty.name if student.faculty else "-"

    def get_major(self, student):
        return student.major.name if student.major else "-"


class CreateStudentSerializer(serializers.Serializer):

    student_id = serializers.CharField(max_length=255)
    name_title = serializers.CharField(max_length=255)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    degree = serializers.CharField(max_length=255)
    faculty = serializers.CharField(max_length=255)
    major = serializers.CharField(max_length=255)
    first_check = serializers.BooleanField()
    second_check = serializers.BooleanField()
    third_check = serializers.BooleanField()


class UpdateStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Information
        fields = ('student_id', 'name_title', 'first_name', 'last_name',
                  'faculty', 'major', 'first_check', 'second_check', 'third_check')


class RunSerializer(serializers.Serializer):

    student_id = serializers.CharField(required=True)


class RunResponseSerializer(serializers.ModelSerializer):
    faculty = serializers.SerializerMethodField()
    major = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Information
        fields = ('student_id', 'name_title', 'first_name', 'last_name',
                  'faculty', 'major', 'image')

    def get_image(self, student):
        return student.image.url if student.image else ""

    def get_faculty(self, student):
        return student.faculty.name if student.faculty else "-"

    def get_major(self, student):
        return student.major.name if student.major else "-"
