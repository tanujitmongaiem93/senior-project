from django.contrib import admin

# Register your models here.
from .models import Information,Attendance

class InformationAdmin(admin.ModelAdmin):
    list_display = ('student_id','name_title','first_name','last_name','faculty','major')

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('get_student_id','first_check','second_check','third_check')

    def get_student_id(self,attendance):
        return attendance.information.student_id
    get_student_id.short_description = 'STUDENT ID'


admin.site.register(Information,InformationAdmin)
admin.site.register(Attendance,AttendanceAdmin)
