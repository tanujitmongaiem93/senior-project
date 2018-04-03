from django.contrib import admin

# Register your models here.
from .models import Information, Faculty, Major, Degree, Practice


class PracticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_first', 'order_last', 'day', 'period', 'load_place', 'place')


class InformationAdmin(admin.ModelAdmin):
    list_display = ('student_id','get_name', 'get_degree', 'get_faculty','get_major',
                    'first_check', 'second_check', 'third_check')

    def get_degree(self, student):
        return student.degree.name if student.degree else "-"
    get_degree.short_description = "Degree"

    def get_name(self, student):
        return "%s %s %s" % (student.name_title, student.first_name, student.last_name)
    get_name.short_description = "Name"

    def get_faculty(self, student):
        return student.faculty.name if student.faculty else "-"
    get_faculty.short_description = "Faculty"

    def get_major(self, student):
        return student.major.name if student.major else "-"
    get_major.short_description = "Major"


class FacultynAdmin(admin.ModelAdmin):
    list_display = ('id','name')


class MajorAdmin(admin.ModelAdmin):
    list_display = ('id','name')


class DegreeAdmin(admin.ModelAdmin):
    list_display = ('id','name')

admin.site.register(Practice,PracticeAdmin)
admin.site.register(Information,InformationAdmin)
admin.site.register(Faculty,FacultynAdmin)
admin.site.register(Major,MajorAdmin)
admin.site.register(Degree,DegreeAdmin)
