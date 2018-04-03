from django.db import models


class Practice(models.Model):
    order_first = models.PositiveIntegerField(default=0)
    order_last = models.PositiveIntegerField(default=0)
    day = models.CharField(max_length=256, blank=True, null=True)
    period = models.CharField(max_length=20, blank=True, null=True)
    load_place = models.TextField(blank=True, null=True)
    place = models.TextField(blank=True, null=True)


class Faculty(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Major(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Degree(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Information(models.Model):
    order = models.PositiveIntegerField(default=0)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, null=True)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, null=True)

    student_id = models.CharField(max_length=8, db_index=True)
    name_title = models.CharField(max_length=6)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='student_image/', null=True)
    is_active = models.BooleanField(default=True)
    is_register = models.BooleanField(default=False)

    first_check = models.BooleanField(default=True)
    second_check = models.BooleanField(default=True)
    third_check = models.BooleanField(default=True)
    first_stamp = models.DateTimeField(null=True)
    second_stamp = models.DateTimeField(null=True)
    third_stamp = models.DateTimeField(null=True)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return self.student_id
    #
    # def add_image():
    #     from django.core.files import File
    #     from os import walk
    #     import os
    #
    #     for (dirpath, dirnames, file_list) in walk(os.path.abspath('student\image')):
    #         for filename in file_list:
    #             student = Information.objects.filter(student_id=filename.split('.')[0]).first()
    #             if student:
    #                 print(student.student_id)
    #                 path = os.path.join(os.path.abspath('student\image'), filename)
    #                 f = File(open(path, 'rb'))
    #                 student.image = f
    #                 student.image.save(filename, f)
    #     return
