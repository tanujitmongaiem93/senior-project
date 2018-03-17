from django.contrib import admin

# Register your models here.
from .models import Information

class InformationAdmin(admin.ModelAdmin):
    list_display = ('student_id','name_title','first_name','last_name','faculty','major')


admin.site.register(Information,InformationAdmin)
