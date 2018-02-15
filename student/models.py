from django.db import models

# Create your models here.
class Information(models.Model):
    student_id = models.CharField(max_length=8, db_index=True)
    name_title = models.CharField(max_length=6)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    faculty = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    image = models.ImageField(upload_to='student_image/', null=True)
    is_active = models.BooleanField(default=True)
    is_register = models.BooleanField(default=False)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return self.student_id

    def create_data():
        import pandas as pd
        import os
        data = pd.read_csv(os.path.abspath('student\student.csv'))

        for index, row in data.iterrows():
            Information.objects.create(
                student_id=row['student_id'],
                name_title=row['name_title'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                faculty="วิศวกรรมศาสตร์",
                major=row['major']
            ).save()
        return

    def add_image():
        from django.core.files import File
        from os import walk
        import os

        for (dirpath, dirnames, file_list) in walk(os.path.abspath('student\image')):
            for filename in file_list:
                student = Information.objects.filter(student_id=filename.split('.')[0]).first()
                if student:
                    print(student.student_id)
                    path = os.path.join(os.path.abspath('student\image'), filename)
                    f = File(open(path, 'rb'))
                    student.image = f
                    student.image.save(filename, f)
        return


class Attendance(models.Model):
    information = models.OneToOneField(Information,on_delete=models.CASCADE)
    first_check = models.BooleanField(default=False)
    second_check = models.BooleanField(default=False)
    third_check = models.BooleanField(default=False)
    first_stamp = models.DateTimeField()
    second_stamp = models.DateTimeField()
    third_stamp = models.DateTimeField()
