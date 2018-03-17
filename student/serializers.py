from rest_framework import serializers

from .models import Information


class CheckSerializer(serializers.Serializer):

    student_id = serializers.CharField(required=True)
    check = serializers.IntegerField(required=True)


class ImageUploadSerializer(serializers.Serializer):

    student_id = serializers.CharField(required=True)
    image = serializers.ImageField(max_length=None, allow_empty_file=False)


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Information
        fields = ('student_id', 'name_title', 'first_name', 'last_name',
                  'faculty', 'major', 'image','id', 'first_check',
                  'second_check', 'third_check')


class CreateStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Information
        fields = ('student_id', 'name_title', 'first_name', 'last_name',
                  'faculty', 'major', 'first_check', 'second_check', 'third_check')


class UpdateStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Information
        fields = ('student_id', 'name_title', 'first_name', 'last_name',
                  'faculty', 'major')


class RunSerializer(serializers.Serializer):

    student_id = serializers.CharField(required=True)


class RunResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Information
        fields = ('student_id', 'name_title', 'first_name', 'last_name',
                  'faculty', 'major', 'image')
