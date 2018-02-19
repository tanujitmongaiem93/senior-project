from rest_framework import serializers

from .models import Information

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Information
        fields = ('student_id', 'name_title', 'first_name', 'last_name',
                  'faculty', 'major', 'image')
